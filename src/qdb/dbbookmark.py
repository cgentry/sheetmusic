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

from qdb.dbconn      import DbConn
from qdb.keys        import BOOKMARK
from qdb.util        import DbHelper
from qdb.dbbook      import DbBook
from qdb.base        import DbBase
from PySide6.QtSql   import QSqlQuery

class DbBookmark(DbBase):
    SQL_BOOKMARK_CHECK      = """SELECT bookmark FROM  Bookmark WHERE book_id = ? AND page = ?"""
    SQL_BOOKMARK_GET_COUNT  = """SELECT count(*) AS count FROM Bookmark where book_id = ?"""
    SQL_BOOKMARK_DELETE_ID  = """DELETE   FROM Bookmark     WHERE book_id = ? AND bookmark=?"""
    SQL_BOOKMARK_DELETE_ALL = """DELETE   FROM Bookmark     WHERE book_id = ?"""
    SQL_SELECT_ALL_BY_ID    = """SELECT * FROM Bookmark 
                                  JOIN Book ON Book.id=book_id WHERE book_id = ? ORDER BY :order ASC"""
    SQL_BOOKMARK_FOR_ENDS   = """SELECT * FROM Bookmark 
                                  JOIN Book ON Book.id=book_id WHERE book_id = ? ORDER BY page :order LIMIT 1"""
    SQL_BOOKMARK_FOR_PAGE   = """SELECT * FROM Bookmark 
                                  JOIN Book ON Book.id=book_id WHERE book_id = ? and page <= ? ORDER BY page DESC LIMIT 1"""
    SQL_BOOKMARK_NEXT       = """
            SELECT * FROM Bookmark 
            JOIN Book ON Book.id=book_id WHERE book_id = ? AND page > (
                SELECT page 
                FROM Bookmark 
                WHERE book_id = ? AND page <= ?
                ORDER BY page DESC LIMIT 1 
        ) ORDER BY page ASC LIMIT 1;"""
    SQL_BOOKMARK_PREVIOUS   = """
            SELECT * FROM Bookmark 
            JOIN Book ON Book.id=book_id WHERE book_id = ? AND page < (
                SELECT page 
                FROM Bookmark 
                WHERE book_id = ? AND page <= ?
                ORDER BY page DESC LIMIT 1 
        ) ORDER BY page DESC LIMIT 1;"""
    
    SQL_IS_EXPANDED=False

    columnNames = None
    joinView    = None
    
    def __init__(self):
        super().__init__( )
        self.setupLogger()

        if DbBookmark.columnNames is None or DbBookmark.joinView is None:
            DbBookmark.columnNames = DbConn.getColumnNames( 'Bookmark')
            DbBookmark.joinView    = DbBookmark.columnNames
            DbBookmark.joinView.remove('id')
            DbBookmark.joinView.extend([ 'Bookmark.id', 'book', 'total_pages'])
        if not DbBookmark.SQL_IS_EXPANDED:
            DbBookmark.SQL_BOOKMARK_FOR_ENDS = DbHelper.addColumnNames( DbBookmark.SQL_BOOKMARK_FOR_ENDS,DbBookmark.joinView)
            DbBookmark.SQL_BOOKMARK_FOR_PAGE = DbHelper.addColumnNames( DbBookmark.SQL_BOOKMARK_FOR_PAGE,DbBookmark.joinView)

            DbBookmark.SQL_BOOKMARK_NEXT     = DbHelper.addColumnNames( DbBookmark.SQL_BOOKMARK_NEXT,DbBookmark.joinView)
            DbBookmark.SQL_BOOKMARK_PREVIOUS = DbHelper.addColumnNames( DbBookmark.SQL_BOOKMARK_PREVIOUS,DbBookmark.joinView)

            DbBookmark.SQL_SELECT_ALL_BY_ID = DbHelper.addColumnNames( DbBookmark.SQL_SELECT_ALL_BY_ID,DbBookmark.joinView)

            DbBookmark.SQL_IS_EXPANDED = True
        self.bookID = None

    def _getBookmarkAtEnd( self, book=None, order='DESC')->dict:
        sql = DbBookmark.SQL_BOOKMARK_FOR_ENDS.replace(':order', order )
        id = self._getBookID(book)
        if id is None:
            return None
        rtn = DbHelper.fetchrow( sql , id , db_fields_to_return=DbBookmark.joinView )
        return rtn
    
    def _getBookID(self, book:str )->int:
        if self.bookID is None or self.bookID != book :
            sql = "SELECT id FROM Book where book=?"
            self.bookID = DbHelper.fetchone( sql , book )
        return self.bookID

    def getFirst( self, book=None )->dict:
        return self._getBookmarkAtEnd( book=book, order='ASC')

    def getLastBookmark( self, book=None )->dict:
        return self._getBookmarkAtEnd( book=book, order='DESC')

    def getNameForPage( self, book:str, page )->str:
        """ Get the name for a bookmark at 'page'. If none, return None """
        res = DbHelper.fetchone( self.SQL_BOOKMARK_CHECK , [ self._getBookID( book ), page ] , default=None)
        return res

    def isBookmark( self, book:str , page )->bool:
        name = self.getNameForPage( book, page )
        return ( name is not None )

    def getBookmarkForPage( self, book:str, page:int )->dict:
        bookID = self._getBookID( book )
        res = DbHelper.fetchrow( DbBookmark.SQL_BOOKMARK_FOR_PAGE, [bookID, page] , DbBookmark.joinView)
        return res

    def getLastpageForBookmark( self, book:str, page:int)->int:
        """ Pass it the current bookmark page and the title
            if this is the last, None is returned. You should
            then get the last page from the file util
        """
        bk = self.getNextBookmarkForPage( book=book, page=page)
        if bk is not None and BOOKMARK.page in bk:
            return bk[ BOOKMARK.page ] - 1
        return None

    def getPreviousBookmarkForPage( self, book:str, page:int )->dict:
        id = self._getBookID( book )
        res = DbHelper.fetchrow( DbBookmark.SQL_BOOKMARK_PREVIOUS, [id, id, page] , DbBookmark.joinView, debug=False )
        return res
        
    def getNextBookmarkForPage( self, book:str, page:int )->dict:
        id = self._getBookID(book)
        res = DbHelper.fetchrow( DbBookmark.SQL_BOOKMARK_NEXT, [id, id, page] , DbBookmark.joinView)
        return res

    def addBookmark(self, book:str, bookmark:str, page:int)->bool:
        """
            Add a bookmark to the database. 
            This requires exact positional parms
        """
        bookID = self._getBookID( book )
        parms = {'book_id':bookID,'bookmark':bookmark, 'page':page }
        sql = self._formatInsertVariable( 'Bookmark', parms , replace=True)
        query = QSqlQuery( DbConn.db())
        query.prepare( sql )
        query = DbHelper.bind( query, list( parms.values() ) )
        query.exec(  )
        self._checkError( query )
        self.getReturnCode( query )
        del query
        return self.wasGood()

    def delBookmark(self, bookmark:str, book:str=None, book_id:int=None )->bool:
        """
            Delete a bookmark from the database by bookmark
            You should pass in named parameters rather than positional but 
            positional are always strings.

            Pass either title and bookmark 
                ( bookname, bookmarkname )
            or by named parameters
                (book=name, bookmark=bookmarkName)
            or by named book_id parms.
                (book_id = # , bookmark = bookmarkName )
        """
        if book is not None:
            book_id = self._getBookID( book )
        elif book_id is None:
            raise ValueError("Delete Bookmark: no book or id passed")
            
        query = DbHelper.prep( DbBookmark.SQL_BOOKMARK_DELETE_ID )
        query = DbHelper.bind( query , [ book_id, bookmark] )
        query.exec()
        self._checkError( query )
        return self.getReturnCode( query )

    def delBookmarkByPage(self, book:str, page:int ):
        row = self.getBookmarkForPage( book=book, page=page )
        if row is not None and len( row ) > 0 and BOOKMARK.name in row:
            return self.delBookmark( bookmark=row[BOOKMARK.name] , book_id=row[BOOKMARK.book_id] )
        return False

    def delAllBookmarks(self, book:str)->bool:
        query = DbHelper.bind( DbHelper.prep( DbBookmark.SQL_BOOKMARK_DELETE_ALL), self._getBookID( book ) )
        query.exec()
        rows = query.numRowsAffected()
        self._checkError( query )
        query.finish()
        return self.wasGood() and rows > 0 

    def getAll(self, book:str, order:str='page' )->list:
        """ Retrieve a list of all bookmarks by book name """
        id = self._getBookID( book )
        return self.getAllId( id , order=order )
        
    def getAllId(self,book_id:int, order:str='page')->list:
        """ Retrieve a list of all bookmarks by book ID """
        order = ( order if order in DbBookmark.columnNames else 'page')
        sql = DbBookmark.SQL_SELECT_ALL_BY_ID.replace(':order', order)
        q = DbHelper.prep(sql)
        q = DbHelper.bind( q , book_id )
        q.exec()
        return DbHelper.all( q, DbBookmark.joinView )

    def getTotal( self, book:int )->int:
        """
            Return how many bookmarks are in a book
        """
        id = self._getBookID(book)
        if id is None or id < 1 :
            return 0
        return DbHelper.fetchone( DbBookmark.SQL_BOOKMARK_GET_COUNT ,id , default=0)

    def insert( self, book:str, bookmark:str, page:int, previousBookmark:str=None):
        """
            Insert will delete the previous bookmark and add a new one
        """
        bookID = DbBook().getId( book )
        parms = {'book_id': bookID , 'bookmark': bookmark , 'page':page }
        sql = self._formatInsertVariable( 'Bookmark', parms , replace=True )
        q = DbHelper.bind( sql , list( parms.values() ))
        q.exec()
        self._checkError( q )
        q.finish()
        return self.getReturnCode( q )