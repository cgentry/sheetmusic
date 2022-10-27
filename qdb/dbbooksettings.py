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
from qdb.dbconn import DbConn
from qdb.util   import DbHelper
from qdb.base   import DbBase
from util.convert import    toBool, toInt
import logging

class DbBookSettings( DbBase ):
    SQL_BOOKSETTING_ALL="""SELECT * FROM BookSettingView WHERE book_id=? ORDER BY :order ASC"""
    SQL_BOOKSETTING_GET="""SELECT * FROM BookSettingView WHERE book_id=? AND key=?"""

    SQL_GET_VALUE="""
            SELECT value AS setting, 'setting' AS source 
            FROM Booksetting WHERE book_id = ? AND key=?
        UNION ALL
            SELECT value AS setting, 'sytem' AS source FROM System WHERE key=?"""
    SQL_BOOKSETTING_FALLBACK="""
        SELECT   book, id AS book_id, System.key as key, System.value as value
            FROM Book, System
            WHERE Book.id=? AND System.key=?
        """
    SQL_BOOKSETTING_ADD="""
        INSERT {}INTO BookSetting (book_id, key, value )
        VALUES ( ? , ? , ?)
    """
    SQL_BOOKSETTING_UPSERT="""
        INSERT OR REPLACE INTO BookSetting (book_id, key, value )
        VALUES ( ?, ?, ?)
    """
    SQL_BOOKSETTING_DELETE      ="""DELETE FROM BookSetting WHERE book_id=:id AND key=?"""
    SQL_BOOKSETTING_DELETE_ALL  ="""DELETE FROM BookSetting WHERE book_id=?"""
    SQL_GET_BOOK_ID             ="""SELECT id FROM Book WHERE book=?"""

    SQL_IS_EXPANDED=False

    def __init__(self, book:str=None):
        """
            Initialise the class. If you pass a book, it will be used
            as default
        """
        super().__init__()
        self.setupLogger()
        self.columnNames = DbConn.getColumnNames( 'BookSetting')
        self.columnView  = DbConn.getColumnNames( 'BookSettingView')
        self.book = book
        self._currentID = None
        if not DbBookSettings.SQL_IS_EXPANDED:
            DbBookSettings.SQL_BOOKSETTING_ALL   = DbHelper.addColumnNames( DbBookSettings.SQL_BOOKSETTING_ALL,self.columnView)
            DbBookSettings.SQL_BOOKSETTING_GET   = DbHelper.addColumnNames( DbBookSettings.SQL_BOOKSETTING_GET,self.columnView)
            DbBookSettings.SQL_IS_EXPANDED = True

    def _bookID( self, book:str=None, ignore=False )->int:
        if self._setBook( book , ignore=False ):
            self._currentID = DbHelper.fetchone( DbBookSettings.SQL_GET_BOOK_ID , param=self.book )
        return self._currentID

    def _setBook(self, book:str, ignore=False )->bool:
        """ Set the book name to the value passed. if it has changed, then
            reset the current, stored book id
        """
        if book is None:
            if self.book is None:
                if ignore:
                    return False
                raise ValueError("No book name supplied")
        elif book != self.book:
            self.book = book
            self.bookID = None
            return True
        return False
     
    def getAll(self, book:str=None , order:str='key', fetchall:bool=True)->list:
        """
            Retrieve all the booksettings, ordered by 'order' (key).
            You can ask for all entries and get a list of dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one
        """
        sql = DbBookSettings.SQL_BOOKSETTING_ALL.replace(':order', order)
        if fetchall:
            return DbHelper.fetchrows( sql , self._bookID( book ), self.columnNames )
        query = DbHelper.prep( sql )
        query.exec()
        return query
    
    def getSetting( self, book:str=None, key:str=None, fallback=True ):
        if not key:
            raise ValueError( "No lookup key")
        parms = [ self._bookID( book) , key, key]
        rows= DbHelper.fetchrows( DbBookSettings.SQL_GET_VALUE, parms , ['setting','system'])
        if rows is not None and len(rows)>0:
            if len( rows ) == 1 :
                if fallback:
                    return rows[0]['setting']
            else:
                return rows[0]['setting']
        return None

    def getValue( self, book:str=None, key:str=None, fallback=True, default=None)->str:
        """ Fetch value for Book key or fallback to the system setting 
            If no value exists, you get 'None'
        """
        value = self.getSetting(book=book, key=key, fallback=fallback)
        return value if value is not None else default

    def getBool( self, book=None, key=None, fallback=True, default=False)->bool:
        value = self.getValue( book=book, key=key, fallback=fallback, default=default)
        return toBool( value )

    def getInt( self, book=None, key=None, fallback=True, default=0)->int:
        value = self.getValue( book=book, key=key, fallback=fallback, default=default)
        return toInt( value )

    def setValueById( self, id:int=None, key=None, value=None, ignore=False)->bool:
        rtn = True
        try:
            if key is None or value is None:
                raise ValueError('Key and value are required')
            id = (self._bookID() if id == None else id )

            parms = [id, key, value ]
            sql = DbBookSettings.SQL_BOOKSETTING_ADD.format( ('OR IGNORE ' if ignore else ''))
            query = DbHelper.bind( DbHelper.prep( sql ), parms )
            query.exec()
            self._checkError( query )
            rtn = self.wasGood() and query.numRowsAffected() > 0
            
            query.finish()
        except Exception as err:
            self.logger.exception("setValueById BookID: '%s' Key: '%s' [%s]",  id, key ,str(err) , stacklevel=1)
            if ignore:
                return False
            raise err
        return rtn

    def setValue(self, book=None, key=None, value=None, ignore=False )->bool:
        try:
            rtn = self.setValueById( self._bookID(book),  key, value, ignore=ignore )
        except Exception as err:
            self.logger.exception("setValue. Book: '%s' Key: '%s' [%s]", book, key ,str(err), stacklevel=1)
            if ignore:
                return False
            raise err
        return rtn
        
    def upsertBookSetting(self, book:str=None, id:int=None,  key:str=None, value:str=None, ignore=False )->bool:
        try:
            sqlid = ( id if id is not None else self._bookID(book))
        except Exception as err:
            self.logger.exception("upsertBookSetting (no book) Book: '%s', BookID: '%s' Key: '%s' [%s]", book, id, key, str(err) , stacklevel=1)
            if ignore:
                return False
            raise err

        parms = [ sqlid, key, value]
        query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_UPSERT, ), parms)
        query.exec()
        rtn = not self.isError() and query.numRowsAffected() > 0 
        self._checkError( query )
        query.finish()
        return rtn

    def deleteValue( self, book=None, key=None, ignore=False)->int:
        """
            Delete one key for book. If no book or key are passed anexcepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. 
        """
        try:
            parms = [ self._bookID(book=book ), key]
            query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_DELETE, ), parms )
            query.exec()
            self._checkError( query )
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self.logger.exception("deleteValue. Book: '%s' Key: '%s' [%s]", book, key, str(err), stacklevel=1 )
            if ignore:
                return 0
            raise err
        return rowcount

    def deleteAllValues( self, book:str=None, ignore=False)->int:
        """
            Delete one key for book. If no book or key are passed anexcepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. """
        try:
            parms = [ self._bookID(book=book )]
            query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_DELETE_ALL, ), self._bookID(book) )
            query.exec()
            self._checkError( query )
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self.logger.exception("dbooksettings.deleteAllValues. BookID: '%s' [%s]", book, str(err), stacklevel=1)
            if ignore:
                return 0
            raise err
        return rowcount
