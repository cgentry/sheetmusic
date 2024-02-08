"""
Utility : Book library methods

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import os
import fnmatch
from qdb.fields.book import BookField
from qdb.dbbook import DbBook
from qdb.keys import DbKeys
from qdil.preferences import DilPreferences

class Library():
    """This provides book library functions
    """
    @staticmethod
    def books() -> list:
        """Get all books from the library

        Returns:
            list: list of dictionary entries of all books
        """
        return DbBook().get_all(order=BookField.LOCATION)

    @staticmethod
    def books_not_in_library() -> list:
        """ Get all books where the the location is not in the sheetmusic folder """
        return Library.books_locations()[1]

    @staticmethod
    def books_in_library() -> list:
        """ Get all the books where the location is in the sheetmusic folder"""
        return Library.books_locations()[0]

    @staticmethod
    def books_locations():
        """Return two lists, books in library, books not in library

        Returns:
            tuple: lists of libraries
        """
        all_books = Library.books()
        library = DilPreferences().dbdirectory
        in_lib = []
        not_in_lib = []
        for book in all_books:
            if book[BookField.LOCATION].startswith(library):
                in_lib.append(book)
            else:
                not_in_lib.append(book)
        return (in_lib, not_in_lib)

    @staticmethod
    def folders() -> list:
        """ Generate a list of folders that contain PNG files """
        library = DilPreferences().dbdirectory
        liblist = []
        page_suffix = Library.page_suffix()
        with os.scandir(library) as libdir:
            for entry in libdir:
                if (not entry.name.startswith('.') and
                        Library.is_valid_book_directory(entry.path, page_suffix)):
                    liblist.append(entry.path)
        return liblist

    @staticmethod
    def is_valid_book_directory(book_dir: str, page_suffix: str = None) -> bool:
        """
            Check if a directory exists for a book, check for pages that exist in directory
        """
        if page_suffix is None:
            page_suffix = Library.page_suffix()
        return (os.path.isdir(book_dir)
                and len(fnmatch.filter(os.listdir(book_dir), '*.' + page_suffix)) > 0)

    @staticmethod
    def page_suffix() -> str:
        """ Return the page suffix used (e.g. 'png')"""
        return DilPreferences().get_value(
            DbKeys.SETTING_FILE_TYPE, default=DbKeys.VALUE_FILE_TYPE)
