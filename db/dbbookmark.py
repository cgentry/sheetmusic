# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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

import sqlite3
from db.dbconn      import DbConn
from db.dbsql       import SqlUpsert, _forceDictionary
from db.keys        import BOOKMARK
from db.dbgeneric   import DbTransform
from db.dbbook      import DbBook

class DbBookmark():
    SQL_BOOKMARK_CHECK="""
        SELECT bookmark
        FROM   Bookmark 
        WHERE  page = ? 
        AND book_id IN (SELECT book_id FROM Book WHERE book= ?);
    """
    SQL_BOOKMARK_DELETE="""
        DELETE FROM Bookmark 
        WHERE bookmark=:bookmark 
        AND book_id IN (SELECT book_id FROM Book WHERE book=:book);"""
    SQL_BOOKMARK_DELETE_ID="""
        DELETE FROM Bookmark 
        WHERE bookmark = :bookmark 
        AND book_id    = :book_id;"""
    SQL_BOOKMARK_DELETE_ALL = """
        DELETE FROM Bookmark 
        WHERE book_id IN (SELECT book_id FROM Book WHERE book=:book)"""
    SQL_BOOKMARK_FOR_ENDS="""
            SELECT *
            FROM BookmarkView
            WHERE book=:book
            ORDER BY page :order LIMIT 1"""
    SQL_BOOKMARK_FOR_PAGE="""SELECT *
            FROM BookmarkView
            WHERE book=:book and page <=:page
            ORDER BY page DESC LIMIT 1"""
    SQL_BOOKMARK_GET_COUNT="SELECT count(*) FROM BookmarkView where book = :book"
    SQL_BOOKMARK_NEXT="""
        SELECT * 
        FROM BookmarkView 
        WHERE book = :book AND page > (
            SELECT page 
            FROM BookmarkView 
            WHERE book = :book AND page <= :page
            ORDER BY page DESC LIMIT 1 
        ) ORDER BY page ASC LIMIT 1;"""
    SQL_BOOKMARK_PREVIOUS="""SELECT * 
        FROM BookmarkView 
        WHERE book = :book AND page < (
            SELECT page 
            FROM BookmarkView 
            WHERE book = :book AND page <= :page
            ORDER BY page DESC LIMIT 1 
        ) ORDER BY page DESC LIMIT 1;"""
    SQL_BOOKMARK_SELECT_ALL="SELECT * From BookmarkView WHERE book    = :book    ORDER BY :order ASC"
    SQL_BOOKMARK_SELECT_ALL_BY_ID="SELECT * From BookmarkView WHERE book_id = :book_id ORDER BY :order ASC"
    
    def __init__(self):
        (self.conn, self.cursor) = DbConn().handles()

    def _getBookmarkAtEnd( self, book=None, order='DESC')->dict:
        sql = self.SQL_BOOKMARK_FOR_ENDS.replace(':order', order )
        res = self.cursor.execute( sql, {'book': book} )
        return DbTransform().rowToDictionary(res.fetchone() )
        
    def getFirst( self, book=None )->dict:
        return self._getBookmarkAtEnd( book=book, order='ASC')

    def getLastBookmark( self, book=None )->dict:
        return self._getBookmarkAtEnd( book=book, order='DESC')

    def getNameForPage( self, book:str, page )->str:
        """ Get the name for a bookmark at 'page'. If none, return None """
        res = self.cursor.execute( self.SQL_BOOKMARK_CHECK, (page, book))
        row = res.fetchone()
        return( str( row[ BOOKMARK.name ]) if row is not None else None )

    def isBookmark( self, book:str , page )->bool:
        name = self.getNameForPage( book, page )
        return ( name is not None )

    def getBookmarkForPage( self, **kwargs )->dict:
        res = self.cursor.execute( self.SQL_BOOKMARK_FOR_PAGE, kwargs )
        return DbTransform().rowToDictionary(res.fetchone() )

    def getLastpageForBookmark( self, book:str, page:int)->int:
        """ Pass it the current bookmark page and the title
            if this is the last, None is returned. You should
            then get the last page from the file util
        """
        bk = self.getNextBookmarkForPage( book=book, page=page)
        if bk is not None:
            return bk[ BOOKMARK.page ] - 1
        return None

    def getPreviousBookmarkForPage( self, **kwargs)->dict:
        res = self.cursor.execute( self.SQL_BOOKMARK_PREVIOUS, kwargs )
        return DbTransform().rowToDictionary( res.fetchone() ) 
        
    def getNextBookmarkForPage( self, **kwargs)->dict:
        res = self.cursor.execute( self.SQL_BOOKMARK_NEXT, kwargs )
        return DbTransform().rowToDictionary( res.fetchone() ) 

    def addBookmark(self, book:str, bookmark:str, page:int):
        """
            Add a bookmark to the database. 
            This requires exact positional parms
        """
        bookID = DbBook().getId( book )
        SqlUpsert( 'Bookmark', bookmark=bookmark, page=page, book_id=bookID )

    def delBookmark(self, *argv, **kwargs )->bool:
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
        fields = _forceDictionary(argv, kwargs, 'book', 'bookmark' )
        if 'book_id' in fields:
            self.cursor.execute( self.SQL_BOOKMARK_DELETE_ID, fields )
        else: # Delete by BOOK name rather than ID
            self.cursor.execute( self.SQL_BOOKMARK_DELETE, fields )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delBookmarkByPage(self, *argv, **kwargs ):
        fields = _forceDictionary(argv, kwargs, 'book' )
        result=self.cursor.execute( self.SQL_BOOKMARK_FOR_PAGE, fields)
        if result is not None:
            row = result.fetchone()
            if row is not None:
                return self.delBookmark( book=row['book'], bookmark=row['bookmark'] )
        return False

    def delAllBookmarks(self, *argv, **kwargs ):
        fields = _forceDictionary(argv, kwargs, 'book' )
        try:
            fields['book_id'] = DbBook().getId( fields['book'] )
        except:
            return False
        self.cursor.execute( self.SQL_BOOKMARK_DELETE_ALL, fields )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def __getAll( self, sql:str, order:str, fields:dict )->list:
        list = []
        rows = self.cursor.execute(sql, fields )
        for row in rows.fetchall():
            list.append( DbTransform().rowToDictionary( row ))
        return list

    def getAll(self, *argv, order:str='page', **kwargs)->list:
        """
            Retrieve a list of all bookmarks by book name
        """
        sql = self.SQL_BOOKMARK_SELECT_ALL.replace(':order', order)
        fields = _forceDictionary(argv, kwargs, 'book' )
        return self.__getAll( sql, order, fields )
        
    def getAllId(self, *argv, order:str='page', **kwargs)->list:
        sql = self.SQL_BOOKMARK_SELECT_ALL_BY_ID.replace(':order', order)
        fields = _forceDictionary(argv, kwargs, 'book_id' )
        return self.__getAll( sql, order, fields )

    def getTotal( self, *argv, **kwargs)->int:
        """
            How many bookmarks for a title?
            Pass either 'title' or book='title'
        """
        fields = _forceDictionary(argv, kwargs, 'book' )
        rows = self.cursor.execute(self.SQL_BOOKMARK_GET_COUNT,fields)
        result = rows.fetchone()
        return int( result[0])

    def insert( self, book:str, bookmark:str, page:int, previousBookmark:str=None):
        """
            Insert will delete the previous bookmark and add a new one
        """
        bookID = DbBook().getId( book )
        if previousBookmark is not None:
            self.delBookmark( book_id=bookID, bookmark=previousBookmark)
        SqlUpsert( 'Bookmark', bookmark=bookmark, page=page, book_id=bookID )
        pass