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
#
# image files should be in a single folder and end in '.png'
# configuration for each book is located in
# config.ini - See ConfigFile in configfile.py
#

from qdb.dbconn import DbConn
from qdb.keys import BOOKMARK
from qdb.util import DbHelper
from qdb.dbbook import DbBook
from qdb.mixin.bookid import MixinBookID
from qdb.base import DbBase
from PySide6.QtSql import QSqlQuery


class DbBookmark(MixinBookID, DbBase):
    SQL_BOOKMARK_CHECK = """SELECT bookmark          FROM Bookmark WHERE book_id = ? AND page = ?"""
    SQL_BOOKMARK_DELETE_ALL = """DELETE                   FROM Bookmark WHERE book_id = ?"""
    SQL_BOOKMARK_DELETE_ID = """DELETE                   FROM Bookmark WHERE book_id = ? AND bookmark=?"""
    SQL_BOOKMARK_GET_COUNT = """SELECT count(*) AS count FROM Bookmark WHERE book_id = ?"""

    SQL_SELECT_ALL_BY_ID = """SELECT * FROM BookmarkView WHERE book_id = ? ORDER BY :order ASC"""
    SQL_BOOKMARK_FOR_ENDS = """SELECT * FROM BookmarkView WHERE book_id = ? ORDER BY page :order LIMIT 1"""
    SQL_BOOKMARK_FOR_PAGE = """SELECT * FROM BookmarkView WHERE book_id = ? and page <= ? ORDER BY page DESC LIMIT 1"""
    SQL_BOOKMARK_NEXT = """SELECT * FROM BookmarkView WHERE book_id = ? and page >  ? ORDER BY page ASC  LIMIT 1"""
    SQL_BOOKMARK_PREVIOUS = """SELECT * 
                                FROM BookmarkView 
                                WHERE book_id = ? AND 
                                      page <  ( 
                                        SELECT page FROM BookmarkView 
                                        WHERE book_id = ? AND page <= ? 
                                        ORDER BY page DESC LIMIT 1) 
                            ORDER BY page DESC LIMIT 1"""

    joinView = None

    def __init__(self):
        super().__init__()
        self.setupLogger()

        if DbBookmark.joinView is None:
            DbBookmark.joinView = DbConn.getColumnNames('BookmarkView')

        self.bookID = None
        self._book_id_type = None
        self._last_book_value = None

    def _getBookmarkAtEnd(self, book: str | int, order='DESC') -> dict | None:
        sql = DbBookmark.SQL_BOOKMARK_FOR_ENDS.replace(':order', order)
        id = self.lookup_book_id(book)
        if id is None:
            return None
        rtn = DbHelper.fetchrow(
            sql, id, db_fields_to_return=DbBookmark.joinView)
        return rtn

    def first(self, book: str | int) -> dict | None:
        """ Fetch the very first bookmark for a book """
        return self._getBookmarkAtEnd(book=book, order='ASC')

    def last(self, book: str | int) -> dict | None:
        """ Fetch the very last bookmark for a book"""
        return self._getBookmarkAtEnd(book=book, order='DESC')

    def getNameForPage(self, book: str | int, page) -> str:
        """ Get the name for a bookmark at 'page'. If none, return None """
        res = DbHelper.fetchone(self.SQL_BOOKMARK_CHECK, [
                                self.lookup_book_id(book), page], default=None)
        return res

    def isBookmark(self, book: str | int, page) -> bool:
        name = self.getNameForPage(book, page)
        return (name is not None)

    def getBookmarkForPage(self, book: str | int, page: int) -> dict:
        bookID = self.lookup_book_id(book)
        res = DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_FOR_PAGE, [
                                bookID, page], DbBookmark.joinView)
        return res

    def lastpage(self, book: str | int, page: int) -> int:
        """ Pass it the book and current page. It will return the last
            page for this bookmark
        """
        bk = self.getNextBookmarkForPage(book=book, page=page)
        if bk is not None and BOOKMARK.page in bk:
            return bk[BOOKMARK.page] - 1
        return None

    def getPreviousBookmarkForPage(self, book: str | int, page: int) -> dict:
        """ Pass it the book and page number and it will find the previous bookmark """
        id = self.lookup_book_id(book)
        res = DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_PREVIOUS, [
                                id, id, page], DbBookmark.joinView, debug=False)
        return res

    def getNextBookmarkForPage(self, book: str | int, page: int) -> dict:
        id = self.lookup_book_id(book)
        res = DbHelper.fetchrow(DbBookmark.SQL_BOOKMARK_NEXT, [
                                id, page], DbBookmark.joinView)
        return res

    def add(self, book: str | int, bookmark: str, page: int) -> bool:
        """
            Add a bookmark to the database. 
            This requires exact positional parms
        """
        bookID = self.lookup_book_id(book)

        parms = {'book_id': bookID, 'bookmark': bookmark, 'page': page}
        sql = self._formatInsertVariable('Bookmark', parms, replace=True)
        query = QSqlQuery(DbConn.db())
        query.prepare(sql)
        query = DbHelper.bind(query, list(parms.values()))
        query.exec()
        self._checkError(query)
        self.getReturnCode(query)
        query.finish()
        del query
        return self.wasGood()

    def delete(self, bookmark: str, book: str | int = None) -> bool:
        """
            Delete a bookmark from the database by bookmark
            You should pass in named parameters rather than positional but 
            positional are always strings.

            bookmark: name of the bookmark
            book: Book.id (int) OR Book.name (str)
        """

        query = DbHelper.prep(DbBookmark.SQL_BOOKMARK_DELETE_ID)
        query = DbHelper.bind(query, [self.lookup_book_id(book), bookmark])
        query.exec()
        self._checkError(query)
        return self.getReturnCode(query)

    def delete_by_page(self, book: str | int, page: int):
        row = self.getBookmarkForPage(book=book, page=page)
        if row is not None and len(row) > 0 and BOOKMARK.name in row:
            return self.delete(bookmark=row[BOOKMARK.name], book=row[BOOKMARK.book_id])
        return False

    def delete_all(self, book: str | int) -> bool:
        query = DbHelper.bind(DbHelper.prep(
            DbBookmark.SQL_BOOKMARK_DELETE_ALL), self.lookup_book_id(book))
        query.exec()
        rows = query.numRowsAffected()
        self._checkError(query)
        query.finish()
        return self.wasGood() and rows > 0

    def getAll(self, book: str | int, order: str = 'page') -> list:
        """ Retrieve a list of all bookmarks by book name or ID """
        if book is None:
            return []
        order = (order if order in DbBookmark.joinView else 'page')
        sql = DbBookmark.SQL_SELECT_ALL_BY_ID.replace(':order', order)
        q = DbHelper.prep(sql)
        q = DbHelper.bind(q, self.lookup_book_id(book))
        q.exec()
        return DbHelper.all(q, DbBookmark.joinView)

    def getAllId(self, book: str | int, order: str = 'page') -> list:
        """ Retrieve a list of all bookmarks by book ID 
            DEPRECATED: Call getAll"""
        return self.getAll( book, order=order )

    def count(self, book: str | int) -> int:
        """
            Return how many bookmarks are in a book
        """
        id = self.lookup_book_id(book)
        if id is None or id < 1:
            return 0
        return DbHelper.fetchone(DbBookmark.SQL_BOOKMARK_GET_COUNT, id, default=0)
