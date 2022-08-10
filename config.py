# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# NOTE:
# A 'section' in a configfile is either a bookmark or DEFAULT


import configparser
from musicutils import toBool, toInt
from musicsettings import MusicSettings

class Config( configparser.ConfigParser):

    def __init__(self, settings=None):
        super().__init__()
        if settings is None:
            self.pref = MusicSettings()
        else:
            self.pref = settings

    def pformat(self) -> str:
        printLine = ""
        if len( super().defaults()) > 0 :
            printLine = "DEFAULT:\n"
        for key in super().defaults():
            printLine = printLine + "{}: {}\n".format(key, super().get("DEFAULT",key))
        for name in self.sections():
            printLine = printLine + "[{}]:\n".format(name)
            for key in self.options( name ):
                printLine = printLine + "\t[{}]: {}\n".format(key, self.get(name, key))
        return printLine

    def getConfig(self, key, section='DEFAULT', value=None, fallback=True):
        """
        Get the value for 'key' from the section passed. If it doesn't exist, 
        get the value from 'DEFAULT'. If that doesn't exist, try and get the value
        from the preferences setting.
        If none exists, then use the value passed.
        """
        if self.has_option(section, key):
            return self.get(section, key)
        
        if fallback and self.pref.contains( key ):
            return self.pref.value( key )

        return value

    def getConfigInt( self,key,section='DEFAULT', value=None, fallback=True )->int:
        return toInt(self.getConfig( key, section, value, fallback))

    def getConfigBool( self,key,section='DEFAULT', value=None, fallback=True)->bool:
        return toBool( self.getConfig( key, section, value, fallback) )
       
    def setConfig(self, key, value, section="DEFAULT")->None:
        if section != 'DEFAULT':
            if not self.has_section( section ):
                self.add_section( section )
        self[section][key]= str(value)

    def sectionsSorted(self)->list:
        sections = self.sections()
        sections.sort()
        return sections
