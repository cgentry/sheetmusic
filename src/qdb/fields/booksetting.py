"""
Database Fields: BookSettingField

BookSetting is a table that uses a key/value
pair to store additional values for a book rather
than expanding out the Book table

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class BookSettingField:
    """ Book columns that can be set """
    BOOK = 'book'  # Book name
    BOOK_ID = 'book_id'  # Book ID
    ID = 'id'  # bookmark ID
    NAME = 'key'  # setting name
    VALUE = 'value'  # setting value
    DATE_ADDED = 'date_added'
    DATE_UPDATED = 'date_updated'

    # Predefined NAME values for pairs
    KEY_DIMENSIONS = 'dimensions'  # Class pdfclass
    KEY_LOCAL_ADDED = 'local_added'
    KEY_LOCAL_UPDATED = 'local_updated'

    KEY_MAX_H = 'max_height' # Unscaled size values
    KEY_MAX_W = 'max_width'
