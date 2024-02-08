"""
Database : Bookmark table interface

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.fields.bookmark import BookmarkField
from qdb.util import DbHelper
from qdb.mixin.bookid import MixinBookID
from qdb.base import DbBase

class DbBookmark(MixinBookID, DbBase):
    """
        DbBookmark provides read/write access to the bookmark table.

        It uses MixinBookID for book id handling
        DbBase for generic access to database functions
    """
    SQL_BOOKMARK_CHECK = """SELECT bookmark
        FROM Bookmark WHERE book_id = ? AND page = ?"""
    SQL_BOOKMARK_DELETE_ALL = """DELETE
        FROM Bookmark WHERE book_id = ?"""
    SQL_BOOKMARK_DELETE_ID = """DELETE
        FROM Bookmark WHERE book_id = ? AND bookmark=?"""
    SQL_BOOKMARK_GET_COUNT = """SELECT count(*) AS count
        FROM Bookmark WHERE book_id = ?"""

    SQL_SELECT_ALL_BY_ID = """SELECT * FROM BookmarkView
        WHERE book_id = ? ORDER BY :order ASC"""
    SQL_BOOKMARK_FOR_ENDS = """SELECT * FROM BookmarkView
        WHERE book_id = ? ORDER BY page :order LIMIT 1"""
    SQL_BOOKMARK_FOR_PAGE = """SELECT * FROM BookmarkView
        WHERE book_id = ? and page <= ? ORDER BY page DESC LIMIT 1"""
    SQL_BOOKMARK_NEXT = """SELECT * FROM BookmarkView
        WHERE book_id = ? and page >  ? ORDER BY page ASC  LIMIT 1"""
    SQL_BOOKMARK_PREVIOUS = """SELECT *
                                FROM BookmarkView
                                WHERE book_id = ? AND
                                      page <  (
                                        SELECT page FROM BookmarkView
                                        WHERE book_id = ? AND page <= ?
                                        ORDER BY page DESC LIMIT 1)
                            ORDER BY page DESC LIMIT 1"""

    view_columns = []

    def __init__(self):
        super().__init__()
        self.setup_logger()

        if not DbBookmark.view_columns:
            DbBookmark.view_columns = DbConn.get_column_names('BookmarkView')

        self.book_id = None
        self._book_id_type = None
        self._last_book_value = None

    def _get_bookmark_at_end(self, book: str | int, order='DESC') -> dict | None:
        """Get a bookmark at the end of the list
        This can be used for getting the first or last bookmark entry

        Args:
            book (str | int): book identi
            order (str, optional): How to order the lookup. Defaults to 'DESC'.

        Returns:
            dict | None: dictionary of names / pages
        """
        sql = DbBookmark.SQL_BOOKMARK_FOR_ENDS.replace(':order', order)
        book_id = self.lookup_book_id(book)
        if book_id is None:
            return None
        rtn = DbHelper.fetchrow(
            sql, book_id, db_fields_to_return=DbBookmark.view_columns)
        return rtn

    def get_first(self, book: str | int) -> dict | None:
        """ Use get_bookmark_at_end to fetch the first.
        Use 'ASC' to get incrementing numbers for pages
        """
        return self._get_bookmark_at_end(book=book, order='ASC')

    def get_last(self, book: str | int) -> dict | None:
        """ Use get_bookmark_at_end to fetch the first.
        Use 'DESC' to get incrementing numbers for pages
        """
        return self._get_bookmark_at_end(book=book, order='DESC')

    def get_name_for_page(self, book: str | int, page) -> str:
        """ Get the name for a bookmark at 'page'. If none, return None """
        res = DbHelper.fetchone(self.SQL_BOOKMARK_CHECK,
                    param =[self.lookup_book_id(book), page],
                    default=None)
        return res

    def is_bookmark(self, book: str | int, page) -> bool:
        """ Determine if there is a bookmark for book at page """
        return self.get_name_for_page(book, page) is not None

    def get_bookmark_for_page(self, book: str | int, page: int) -> dict:
        """ Get a bookmark for page in book """
        book_id = self.lookup_book_id(book)
        res = DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_FOR_PAGE, [
                                book_id, page], DbBookmark.view_columns)
        return res

    def last_page(self, book: str | int, page: int) -> int:
        """ Pass it the book and current page. It will return the last
            page for this bookmark
        """
        bk = self.get_next_bookmark_for_page(book=book, page=page)
        if bk is not None and BookmarkField.PAGE in bk:
            return bk[BookmarkField.PAGE] - 1
        return None

    def get_previous_bookmark_for_page(self, book: str | int, page: int) -> dict:
        """ Pass it the book and page number and it will find the previous bookmark """
        book_id = self.lookup_book_id(book)
        return DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_PREVIOUS, [
            book_id, book_id, page], DbBookmark.view_columns, debug=False)

    def get_next_bookmark_for_page(self, book: str | int, page: int) -> dict:
        """ Pass it the book and page number and it will get the next bookmark"""
        return DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_NEXT, [
            self.lookup_book_id(book), page], DbBookmark.view_columns)

    def add(self, book: str | int, bookmark: str, page: int) -> bool:
        """
            Add a bookmark to the database.
            This requires exact positional parms
        """
        book_id = self.lookup_book_id(book)

        parms = {'book_id': book_id, 'bookmark': bookmark, 'page': page}
        sql = self._format_insert_variable('Bookmark', parms, replace=True)
        query = QSqlQuery(DbConn.db())
        query.prepare(sql)
        query = DbHelper.bind(query, list(parms.values()))
        query.exec()
        self._check_error(query)
        self.get_rtn_code(query)
        query.finish()
        del query
        return self.was_good()

    def delete(self, bookmark: str, book: str | int ) -> bool:
        """Delete a bookmark from the database by bookmark name
            You should pass in named parameters rather than positional but
            positional are always strings.
        Args:
            bookmark (str): Name of the bookmark
            book (str | int): Book.id (int) OR Book.name (str).

        Returns:
            bool: True if deleted
        """
        query = DbHelper.prep(DbBookmark.SQL_BOOKMARK_DELETE_ID)
        query = DbHelper.bind(query, [self.lookup_book_id(book), bookmark])
        query.exec()
        self._check_error(query)
        return self.get_rtn_code(query)

    def delete_by_page(self, book: str | int, page: int)->bool:
        """Delete a bookmark from the database by bookmark name

        Args:
            book (str | int): Book.id (int) or Book.name (str)
            page (int): page number where bookmark is stored against

        Returns:
            bool: True if page was deleted, false if not
        """
        row = self.get_bookmark_for_page(book=book, page=page)
        if row is not None and len(row) > 0 and BookmarkField.NAME in row:
            return self.delete(bookmark=row[BookmarkField.NAME], book=row[BookmarkField.BOOK_ID])
        return False

    def delete_all(self, book: str | int) -> bool:
        """ Delete all pages within a book """
        query = DbHelper.bind(DbHelper.prep(
            DbBookmark.SQL_BOOKMARK_DELETE_ALL), self.lookup_book_id(book))
        query.exec()
        rows = query.numRowsAffected()
        self._check_error(query)
        query.finish()
        return self.was_good() and rows > 0

    def get_all(self, book: str | int | dict = None, order: str = 'page') -> list:
        """ Retrieve a list of all bookmarks by book name or ID """
        if book is None:
            book = self.book_id
        order = (order if order in DbBookmark.view_columns else 'page')
        sql = DbBookmark.SQL_SELECT_ALL_BY_ID.replace(':order', order)
        q = DbHelper.prep(sql)
        q = DbHelper.bind(q, self.lookup_book_id(book))
        q.exec()
        return DbHelper.all(q, DbBookmark.view_columns)

    def get_count(self, book: str | int) -> int:
        """
            Return how many bookmarks are in a book
        """
        book_id = self.lookup_book_id(book)
        if not book_id:
            return 0
        return DbHelper.fetchone(
            DbBookmark.SQL_BOOKMARK_GET_COUNT,
            param=book_id,
            default=0)
