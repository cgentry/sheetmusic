# This Python file uses the following encoding: utf-8
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

def toInt( value, default=0, ignore=True) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float ):
        return int(value)
    if isinstance(value, str ):
        if value:
            try:
                return int(value)
            except ValueError as err:
                if ignore:
                    return default
                else:
                    raise err

    return default

def toBool(v):
    if isinstance(v,bool):
        return v
    if v is None:
        return False
    if isinstance( v , int ):
        return v != 0
    return v.lower() in ("yes", "true", "t", "1","ok")
