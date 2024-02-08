"""
Database Fields: Bookmark

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class BookmarkField:
    """
        Use this for either bookmarkview or bookmark
    """
    BOOK = 'book'  # Book name
    BOOK_ID = 'book_id'  # Book ID
    ID = 'id'  # bookmark ID
    NAME = 'bookmark'  # bookmark name
    PAGE = 'page'  # bookmark starting page
    VALUE = 'page'  # alias for starting page
