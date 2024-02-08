"""
Tomlbook Module part of
"""
# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file is part of Sheetmusic.

# Sheetmusic is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from pathlib import Path
from datetime import date, datetime
import tomllib

from constants import ProgramConstants
from qdb.fields.book import BookField
from qdb.keys import DbKeys
from qdb.dbsystem import DbSystem



class MixinTomlBook:
    """ This is a configuration storage/load mixin.
        Handles in configuration files that store key information.

        If a filename is passed in, the filename will have it's extension removed and '.cfg' added
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._use_toml_file = DbSystem().get_value(DbKeys.SETTING_USE_TOML_FILE, True)

    CONFIG_TOML_FILE = 'properties.cfg'
    CONFIG_TOML_EXT = '.cfg'
    VALID_TOML_KEYS = [
        BookField.BOOK, BookField.COMPOSER, BookField.GENRE,
        BookField.NUMBER_STARTS, BookField.LAST_READ,
        BookField.AUTHOR, BookField.PUBLISHER, BookField.LINK,
    ]

    def _toml_format(self, value)->str:
        match value:
            case bool():
                return "true" if value else "false"
            case float() | int():
                return str(value)
            case str():
                return '"{}"'.format( value.replace('"', '\\"'))
            case datetime():
                return value.isoformat()
            case date():
                return value.isoformat()
            case list():
                return f"[{', '.join(self._toml_format(v) for v in value)}]"
            case _:
                raise TypeError(
                    f"{type(value).__name__} {value!r} is not supported"
        )

    def toml_path(self, directory: str, filename: str = None) -> str:
        """ Format the full directory path for the TOML file
            If you pass a directory and filename in,
            it will always replace the extension and add '.cfg'

            This is useful if you want to save a config file next to the PDF file.
            If directory points to a file, rather than a directory, it will be used to point to
            a config file.
        """
        if filename is None:
            if os.path.isfile(directory):
                return Path(directory).with_suffix(MixinTomlBook.CONFIG_TOML_EXT)
            filename = MixinTomlBook.CONFIG_TOML_FILE
        else:
            filename = Path(filename).with_suffix(
                MixinTomlBook.CONFIG_TOML_EXT)
        return os.path.join(directory, filename)

    def _dict_to_str( self, config:dict )->str:
        vlist = []
        for key in MixinTomlBook.VALID_TOML_KEYS:
            if key in config:
                apstr=f"{key.strip()} = {self._toml_format( config[key])}"
                vlist.append( apstr )
        return "\n".join( vlist )

    def set_toml(self, usetoml:bool):
        """ Override the system TOML flag"""
        self._use_toml_file = usetoml

    def use_toml(self)->bool:
        """ Return True if using TOML file"""
        return self._use_toml_file

    def write_toml_properties(self, config: dict, directory: str, filename: str = None) -> str:
        """ Write out the propertes valid for a TOML configuration file."""
        if not self.use_toml():
            return ""
        toml_fname = self.toml_path(directory, filename)
        with open( toml_fname , "w", encoding="utf-8" ) as f:
            f.write( f"# SheetMusic version {ProgramConstants.VERSION }\n" )
            f.write( f"# Written {datetime.now().isoformat()}\n" )
            if BookField.SOURCE in config:
                f.write(f"# FOR: {config[BookField.SOURCE ]}\n")
            f.write( self._dict_to_str( config ))
        return toml_fname

    def delete_toml_properties(self,  directory: str, filename: str = None) -> bool:
        """ Remove toml property from file """
        path = self.toml_path(directory, filename)
        file_exists = os.path.isfile(path)
        if file_exists:
            os.remove(path)
        return file_exists

    def read_toml_properties(self, directory: str = None) -> dict:
        """ Read toml properties from file"""
        return self.read_toml_properties_file(self.toml_path(directory))

    def read_toml_properties_file(self, directory: str, filename: str = None) -> dict:
        """ Load the TOML file into a dictionary """
        if self.use_toml():
            path = self.toml_path(directory, filename)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8" ) as f:
                    toml = f.read()
                return self.read_toml_properties_str( toml )
        return {}

    def read_toml_properties_str( self, toml_str:str )->dict:
        """ Process the string and turn into toml file """
        rtn = {}
        if self.use_toml():
            data = tomllib.loads(toml_str)
            for key, data in data.items():
                if key in MixinTomlBook.VALID_TOML_KEYS:
                    rtn[key] = data
        return rtn
