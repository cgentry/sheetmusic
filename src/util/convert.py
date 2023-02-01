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

def toInt( value, default=0, ignore=True) -> int:
    rtn = default
    if value is not None and value != "":
        if isinstance( value, bool ):
            rtn =  ( 1 if value else 0)
        else: 
            try:
                rtn= int(value)
            except ValueError as err:
                if not ignore:
                    raise err
    return rtn

def toBool(v,default=False):
    if isinstance(v,bool):
        return v
    if v is None:
        return default
    if isinstance( v , int ):
        return v != 0
    return v.lower() in ("yes", "true", "t", "1","ok")
