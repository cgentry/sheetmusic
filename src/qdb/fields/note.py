"""
Database Fields: Note

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from dataclasses import dataclass
from qdb.util import DbHelper


@dataclass(init=False)
class NoteField:
    """ Note columns """
    ID = "id"
    NOTE = "note"
    LOCATION = "location"
    SIZE = "size"
    BOOK_ID = "book_id"
    PAGE = "page"
    SEQ = "sequence"

    RECORD = {
        NOTE: '',
        LOCATION: None,
        SIZE: None,
        BOOK_ID: None,
        PAGE: 0,
        SEQ: 0
    }

    @staticmethod
    def new(values: dict = None, encode: bool = True) -> dict:
        """Create a new note record.
        The record will be set with sensible defaults
        but values can be overridden by passing a dict

        Args:
            values (dict, optional): Optional override.
                Defaults to None.
            encode (bool): True if you want values encoded

        Returns:
            dict: Key/Value pair matching the Note records
        """
        if values is None:
            return NoteField.RECORD
        if encode:
            if NoteField.SIZE in values and \
                    values[NoteField.SIZE] is not None:
                values[NoteField.SIZE] = \
                    DbHelper.encode(values[NoteField.SIZE])
            if NoteField.LOCATION in values and \
                    values[NoteField.LOCATION] is not None:
                values[NoteField.LOCATION] = \
                    DbHelper.encode(values[NoteField.LOCATION])
        return NoteField.RECORD | values
