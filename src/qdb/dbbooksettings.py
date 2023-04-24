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
from qdb.util   import DbHelper
from qdb.base   import DbBase
from qdb.keys   import BOOKSETTING, DbKeys
from qdb.mixin.bookid import MixinBookID
from util.convert import    toBool, toInt
from typing import Any
import logging

class DbBookSettings( MixinBookID, DbBase ):
    SQL_BOOKSETTING_ALL="""SELECT * FROM BookSettingView WHERE book_id=? ORDER BY :order ASC"""
    SQL_BOOKSETTING_GET="""SELECT * FROM BookSettingView WHERE book_id=? AND key=?"""

    SQL_GET_VALUE="""
            SELECT value AS setting, 
                   'setting' AS source 
            FROM Booksetting 
            WHERE book_id = ? 
              AND key=?
        UNION ALL
            SELECT value AS setting, 
                   'sytem' AS source 
            FROM System 
            WHERE key=?"""
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

    SQL_IS_EXPANDED=False

    encoded_keys = [ BOOKSETTING.dimensions ]
    encoded_bool = [ DbKeys.SETTING_RENDER_PDF ]

    def __init__(self, book:str=None):
        """
            Initialise the class. If you pass a book, it will be used
            as default
        """
        super().__init__()
        self.setupLogger()
        self.columnNames = DbConn.getColumnNames( 'BookSetting')
        self.columnView  = DbConn.getColumnNames( 'BookSettingView')
        if book is not None:
            self.lookup_book_id( book )
        if not DbBookSettings.SQL_IS_EXPANDED:
            DbBookSettings.SQL_BOOKSETTING_ALL   = DbHelper.addColumnNames( DbBookSettings.SQL_BOOKSETTING_ALL,self.columnView)
            DbBookSettings.SQL_BOOKSETTING_GET   = DbHelper.addColumnNames( DbBookSettings.SQL_BOOKSETTING_GET,self.columnView)
            DbBookSettings.SQL_IS_EXPANDED = True

    def _encode( self , key , value ):
        if key in DbBookSettings.encoded_keys :
            return DbHelper.encode( value )
        if key in DbBookSettings.encoded_bool:
            if value == None:
                return None
            return 1 if value == True or value == 1 else 0
        return value
        
    def _decode( self, key, value , raw:bool=False):
        """ Call this to decode the value from the database
            If you pass it raw==True, it will just retrurn the value
        """
        if not raw:
            if value is not None and key in DbBookSettings.encoded_keys :
                return DbHelper.decode( value )
            if key in DbBookSettings.encoded_bool:
                if value == None:
                    return None
                return True if value == True or value == 1 or value == '1' else False
        return value

    def upsertBookSetting(self, book: str | int=None,   key:str=None, value:str=None, ignore=False )->bool:
        """ Update or insert a book setting. If the value is None, the value will be deleted """
        try:
            if book is None or key is None:
                raise ValueError( f'No book or key passed BOOK: {book} KEY: {key} VALUE: {value}')
            sqlid = ( book if book is not None and isinstance( book, int ) else self.lookup_book_id(book))
        except Exception as err:
            self.logger.critical("upsertBookSetting (no book) Book: '%s', BookID: '%s' Key: '%s' [%s]".format( book, id, key, str(err) ), trace=True)
            if ignore:
                return False
            raise err
        if value == None:
            return ( self.deleteValue( book , key, ignore = True ) > 0 )
        value = self._encode( key, value )
        parms = [ sqlid, key, value]
        query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_UPSERT, ), parms)
        query.exec()
        rtn = not self.isError() and query.numRowsAffected() > 0 
        self._checkError( query )
        query.finish()
        return rtn

    def getAll(self, book:str|int=None , order:str='key', fetchall:bool=True)->list:
        """
            Retrieve all the booksettings, ordered by 'order' (key).
            You can ask for all entries and get a list of dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one
        """
        if not book:
            raise ValueError('No book id')
        sql = DbBookSettings.SQL_BOOKSETTING_ALL.replace(':order', order)
        if fetchall:
            return DbHelper.fetchrows( sql , self.lookup_book_id( book ), self.columnView , endquery=self._checkError )
        query = DbHelper.prep( sql )
        query.exec()
        self._checkError( query )
        return query
    
    def getAllSetting( self, book:str|int=None , order:str='key', raw:bool=False)->dict:
        """ This returns all the settings 
            Order of data is by key unless you set 'order'
            If you don't want the values decoded, set 'raw' = true. No conversion will take place
        """
        settings = {}
        for entry in self.getAll( book, order ):
            settings[ entry['key']] = self._decode( entry['key'], entry['value'] , raw)
        return settings

    def getSetting( self, book:str=None, key:str=None, fallback=True, raw:bool=False ):
        """ Fetch the value for the key. """
        if not key:
            raise ValueError( "No lookup key")
        id = self.lookup_book_id( book)
        parms = [ id , key, key]
        rows= DbHelper.fetchrows( DbBookSettings.SQL_GET_VALUE, parms , ['setting','system'], endquery=self._checkError )
        if rows is not None and len(rows)>0:
            if len( rows ) == 1 :
                if fallback:
                    return self._decode( key, rows[0]['setting'], raw=raw )
            else:
                return self._decode( key,rows[0]['setting'] , raw=raw)
        return None

    def getValue( self, book:str=None, key:str=None, fallback:bool=True, default=None, raw:bool=False)->Any:
        """ Fetch value for Book key or fallback to the system setting (if fallback is True )
            If no value exists, you get 'None' 
            If raw = True, no conversion occurs. You get whatever is there.
            NOTE: If you code 'raw=True' this is the same as calling getSetting with fallback=False
        """
        value = self.getSetting(book=book, key=key, fallback=fallback, raw=raw)
        return value if value is not None or raw else default

    def getBool( self, book=None, key=None, fallback=True, default=False )->bool:
        value = self.getValue( book=book, key=key, fallback=fallback, default=default)
        return toBool( value )

    def getInt( self, book=None, key=None, fallback=True, default=0)->int:
        return toInt( self.getValue( book=book, key=key, fallback=fallback, default=default) )

    def setValueById( self, book: str | int=None, key=None, value=None, ignore=False)->bool:
        rtn = True
        print(f'setvalue KEY {key} VALUE: {value}')
        try:
            if key is None or value is None:
                raise ValueError('Key and value are required')
            
            value = self._encode( key, value )
            if value == None:
                return self.deleteValue( book, key, ignore )
            parms = [self.lookup_book_id(book), key, value ]
            sql = DbBookSettings.SQL_BOOKSETTING_ADD.format( ('OR IGNORE ' if ignore else ''))
            query = DbHelper.bind( DbHelper.prep( sql ), parms )
            query.exec()
            self._checkError( query )
            rtn = self.wasGood() and query.numRowsAffected() > 0
            
            query.finish()
        except Exception as err:
            self.logger.critical("setValueById BookID: '%s' Key: '%s' [%s]".format( id, key ,str(err) ) , trace=True)
            if ignore:
                return False
            raise err
        return rtn

    def setValue(self, book: str | int=None, key=None, value=None, ignore=False )->bool:
        return self.setValueById( book, key, value, ignore )
        
    def deleteValue( self, book: str | int=None, key=None, ignore=False)->int:
        """
            Delete one key for book. If no book or key are passed anexcepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. 
        """
        try:
            if not book:
                raise ValueError('No book id')
            parms = [ self.lookup_book_id(book=book ), key]
            query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_DELETE, ), parms )
            query.exec()
            self._checkError( query )
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self.logger.critical("deleteValue. Book: '%s' Key: '%s' [%s]".format( book, key, str(err) ), trace=True )
            if ignore:
                return 0
            raise err
        return rowcount

    def deleteAllValues( self, book: str | int=None, ignore=False)->int:
        """
            Delete one key for book. If no book or key are passed an excepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. """
        try:
            if not book:
                raise ValueError('No book id')
            query = DbHelper.bind( DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_DELETE_ALL, ), self.lookup_book_id(book) )
            query.exec()
            self._checkError( query )
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self.logger.critical("dbooksettings.deleteAllValues. BookID: '%s' [%s]".format( book, str(err)) )
            if ignore:
                return 0
            raise err
        return rowcount
