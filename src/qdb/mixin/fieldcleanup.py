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

import re

class MixinFieldCleanup:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from_chars = "\t*/:<>?|\\"
        to_chars =   ' '* len( from_chars)
        self.blank_bad_chars = str.maketrans( from_chars, to_chars)

    def clean_field_value(self, field_value: str, level: int=None) -> str:
        """ This takes a field and removes characters that are invalid for filename
        x
            Removes:
            * newline, and tabs
            * invalid characters for file names ( "*/:<>?\| )
            * compress multiple spaces to one
            * removes any leading characters that aren't alphanumeric
            * removes trailing whitespace
        """
        
        # No newline, returns or tabs
        field_value = re.sub(r'[\n\r]+', '', field_value)
        # not permitted in NTFS, Mac, or other systems for filenames
        field_value = field_value.translate( self.blank_bad_chars ) 
        # Reduce multiple spaces to one
        field_value = re.sub(r'\s+',       ' ', field_value)
        # Leading char must be Alphanumeric (removes dot, double dot and spaces)
        field_value = re.sub(r'^[^a-zA-Z\d]+', '', field_value)

        return field_value.strip()
    
    def remove_ctrl_char( self, field_value:str )->str:
        # No newline, returns or tabs
        return re.sub(r'[\n\r]+', '', field_value).strip()
