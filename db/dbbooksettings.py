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
from db.dbconn import DbConn
from db.dbsql  import _sqlUpsert, _sqlInsert, SqlInsert, SqlRowString, SqlColumnNames

class DbBookSettings():
    SQL_BOOKSETTING_ALL="""SELECT *
        FROM  BookSettingView
        WHERE book=:book
        ORDER BY key ASC"""
    SQL_BOOKSETTING_GET="""SELECT *
        FROM BookSettingView
        WHERE book=:book AND key=:key
        """
    SQL_BOOKSETTING_FALLBACK="""
        SELECT book, id AS book_id, System.*
            FROM Book, System
            WHERE Book.book=:book
            AND System.key=:key
        """
    SQL_BOOKSETTING_ADD="""
        INSERT INTO {}BookSetting (book_id, key, value )
        VALUES ( :id, :key, :value)
    """
    SQL_BOOKSETTING_UPSERT="""
        INSERT OR REPLACE INTO BookSetting (book_id, key, value )
        VALUES ( :id, :key, :value)
    """
    SQL_BOOKSETTING_DELETE="""DELETE FROM BookSetting WHERE book_id=:id AND key=:key"""
    SQL_BOOKSETTING_DELETE_ALL="""DELETE FROM BookSetting WHERE book_id=:id"""
    SQL_GET_BOOK_ID="""SELECT id FROM Book WHERE book=:book"""

    def __init__(self, book:str=None):
        """
            Initialise the class. If you pass a book, it will be used
            as default
        """
        self.columnNames = SqlColumnNames( 'BookSettings')
        self.book = book
        self.cursor = DbConn().cursor()

    def _setBook(self, book:str )->str:
        if book is None:
            if self.book is None:
                raise ValueError("No book name supplied")
            return self.book
        return book

    def _bookID(self, book:str=None, ignore=True):
        """ Fetch Book id """
        result = self.cursor.execute(self.SQL_GET_BOOK_ID, [self._setBook(book)] )
        row = result.fetchone()
        if row is None or len( row ) == 0:
            raise sqlite3.OperationalError("Book not found")
        return int( row['id'])
        
    def getAll(self, book:str=None ):
        """
            Get All book settings for a particular book.
        """
        result = self.cursor.execute( self.SQL_BOOKSETTING_ALL, [self._setBook(book)])
        return result.fetchall()
        
    def getValue( self, book=None, key=None, fallback=True):
        """ Fetch setting for Book or fallback to the system setting """
        book = self._setBook[book]
        parms = {'book':book, 'key':key}
        result = self.cursor.execute( self.SQL_BOOKSETTING_GET, parms)
        rows = result.fetchone()
        if fallback and rows is None:
            result = self.cursor.execute( self.SQL_BOOKSETTING_FALLBACK, parms)
            rows = result.fetchone()
        return rows

    def getBool( self, book=None, key=None, fallback=True, default=False)->bool:
        row = self.getValue( book=book, key=key, fallback=fallback )
        if row is not None:
            try:
                return ( row['value'] == 'True' or int(row['value']) == 1)
            except:
                return default
        return default

    def getInt( self, book=None, key=None, fallback=True, default=0)->bool:
        row = self.getValue( book=book, key=key, fallback=fallback )
        if row is not None:
            try:
                return int( row['value'] )
            except:
                return default
        return default

    def setValueById( self, id:int=None, key=None, value=None, ignore=False)->bool:
        try:
            if id is None:
                raise ValueError("Book ID is required")
            if key is None or value is None:
                raise ValueError("ID and Key are required")
            parms = {"id": id, "key":key, "value":value }
            sql = self.SQL_BOOKSETTING_ADD.format( ('OR IGNORE ' if ignore else ''))
            (_, cursor) = DbConn().openDB()
            self.cursor.execute( sql, parms)
        except Exception as err:
            if ignore:
                return False
            raise err
        return True

    def setValue(self, book=None, key=None, value=None, ignore=False )->bool:
        id = self._bookID(book=book, ignore=ignore)
        return self.setValueById( id, key, value, ignore=ignore )
        
    def upsertBookSetting(self, book:str=None, id:int=None,  key:str=None, value:str=None, ignore=False )->bool:

        parms = { "id": id, "key":key, "value":value} 
        try:
            if id is None:
                parms['id'] = self._bookID(book=book, ignore=ignore)
            self.cursor.execute( self.SQL_BOOKSETTING_UPSERT, parms)
        except Exception as err:
            if ignore:
                return False
            raise err
        return True

    def deleteValue( self, book=None, key=None, ignore=False):
        """
            Delete one key for book. If no book or key are passed anexcepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. """
        try:
            id = self._bookID(book=book, ignore=ignore)
            parms = {"id": id, "key":key}
            self.cursor.execute( self.SQL_BOOKSETTING_DELETE, parms)
        except Exception as err:
            if ignore:
                return 0
            raise err
        return self.cursor.rowcount

    def deleteAllValues( self, book=None, ignore=False):
        """
            Delete one key for book. If no book or key are passed anexcepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. """
        try:
            id = self._bookID(book=book, ignore=ignore)
            parms = {"id": id}
            self.cursor.execute( self.SQL_BOOKSETTING_DELETE_ALL, parms)
        except Exception as err:
            if ignore:
                return 0
            raise err
        return self.cursor.rowcount
