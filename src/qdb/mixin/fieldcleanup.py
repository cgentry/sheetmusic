"""
 Database Mixin : Cleanup

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import re

class MixinFieldCleanup:
    """Clean out invalid characters in fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from_chars = "\t*/:<>?|\\"
        to_chars =   ' '* len( from_chars)
        self.blank_bad_chars = str.maketrans( from_chars, to_chars)

    def clean_field_value(self, field_value: str ) -> str:
        """This takes a field and removes characters that are invalid for filename
            Removes:
            * newline, and tabs
            * invalid characters for file names ( "*/:<>?\\| )
            * compress multiple spaces to one
            * removes any leading characters that aren't alphanumeric
            * removes trailing whitespace

        Args:
            field_value (str): Value to cleanup

        Returns:
            str: cleaned string
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
        """Remove newline or linefeed characters and leading/trailing blanks

        Args:
            field_value (str): Dirty string

        Returns:
            str: clean string
        """
        return re.sub(r'[\n\r]+', '', field_value).strip()
