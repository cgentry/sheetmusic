"""
Database Fields: Book

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class BookField:
    """
    This will work for both Book and Bookview
    the view has composer and genre and local_* fields
    """
    ID = 'id'
    NAME = 'book'
    BOOK = 'book'
    TITLE = 'book'
    COMPOSER = 'composer'
    COMPOSER_ID = 'composer_id'
    GENRE = 'genre'
    GENRE_ID = 'genre_id'
    SOURCE = 'source'           # Location of original
    SOURCE_TYPE = 'source_type'  # What type is it? png or pdf
    LOCATION = 'location'       # Location of display material
    LINK = 'link'               # optional: url link
    VERSION = 'version'
    AUTHOR = 'author'           # optional
    PUBLISHER = 'publisher'     # optional
    TOTAL_PAGES = 'total_pages'
    ASPECT_RATIO = 'aspectRatio'
    LAST_READ = 'last_read'
    NUMBER_STARTS = 'numbering_starts'
    NUMBER_ENDS = 'numbering_ends'
    NAME_DEFAULT = 'name_default'
    DATE_ADDED = 'date_added'
    DATE_UPDATED = 'date_updated'
    DATE_READ = 'date_read'
    FILE_MODIFIED = 'date_file_modified'
    FILE_CREATED = 'date_file_created'
    PDF_CREATED = 'date_pdf_created'
    PDF_MODIFIED = 'date_pdf_modified'
