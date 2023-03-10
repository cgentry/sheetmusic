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
from qdb.keys import BOOK
from pathlib import Path
from datetime import date, datetime
from qdb.keys import ProgramConstants


class MixinTomlBook:
    """ This is a configuration storage/load mixin. It will handle in configuration files that store key information. 

        If a filename is passed in, the filename will have it's extension removed and '.cfg' added
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    CONFIG_TOML_FILE = 'properties.cfg'
    CONFIG_TOML_EXT = '.cfg'
    VALID_TOML_KEYS = [
        BOOK.book, BOOK.composer, BOOK.genre,  
        BOOK.numberStarts, BOOK.lastRead,
        BOOK.author, BOOK.publisher, BOOK.link,
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
            If you pass a directory and filename in, it will always replace the extension and add '.cfg'

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
        list = []
        for key in MixinTomlBook.VALID_TOML_KEYS:
            if key in config:
                list.append("{} = {}".format( key.strip(), self._toml_format( config[key])))
        return "\n".join( list )
              
    def write_toml_properties(self, config: dict, directory: str, filename: str = None) -> str:
        """ Write out the propertes valid for a TOML configuration file."""
        toml_fname = self.toml_path(directory, filename)
        with open( toml_fname , "w") as f:
            f.write( "# SheetMusic version {}\n".format( ProgramConstants.version ) )
            f.write( "# Written {}\n".format( datetime.now().isoformat() ) )
            if BOOK.source in config:
                f.write("# FOR: {}\n".format( config[BOOK.source ]))
            f.write( self._dict_to_str( config ))
        return toml_fname

    def delete_toml_properties(self,  directory: str, filename: str = None) -> bool:
        path = self.toml_path(directory, filename)
        file_exists = os.path.isfile(path)
        if file_exists:
            os.remove(path)
        return file_exists

    def read_toml_properties(self, directory: str = None) -> dict:
        return self.read_toml_properties_file(self.toml_path(directory))

    def read_toml_properties_file(self, directory: str, filename: str = None) -> dict:
        """ Load the TOML file into a dictionary """
        path = self.toml_path(directory, filename)
        if os.path.isfile(path):
            with open(path, "r") as f:
                toml = f.read()
            return self.read_toml_properties_str( toml )
        return {}

    def read_toml_properties_str( self, toml_str:str )->dict:
        """ Process the string and turn into toml file """
        import tomllib
        rtn = {}
        data = tomllib.loads(toml_str)
        for key, data in data.items():
            if key in MixinTomlBook.VALID_TOML_KEYS:
                rtn[key] = data
        return rtn