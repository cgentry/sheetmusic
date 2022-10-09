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

"""
    This uses three 'static' global variables (well, it kees handles open) In order to not open/close the
    database, you should create an instance of the class and not delete it. Then, you get the same variable.

"""
import sqlite3
import inspect
from typing import Tuple

_sheet_db_conn= None
_sheet_db_curr = None
_sheet_db_location = None


class DbConn():

    def __init__( self, databaseName:str=None ):
        if databaseName is not None:
            if self._checkDbName( databaseName):
                self.closeDB()

    def _setLocationName( self, name ):
        global _sheet_db_location
        _sheet_db_location = name

    def _checkDbName( self, databaseName:str=None )->bool:
        global _sheet_db_location
        nameChanged = False
        if databaseName is not None:
            if not isinstance( databaseName, str ):
                raise ValueError( "Wrong datatype passed: {} (_checkDbName)".format( type( databaseName )))
            if _sheet_db_location != databaseName :
                self.closeDB()
                nameChanged = True
            _sheet_db_location = databaseName
        return nameChanged
    
    def name(self)->str:
        global _sheet_db_location
        return _sheet_db_location

    def openDB( self, databaseName:str=None, trace:bool=False)->Tuple[sqlite3.Connection,sqlite3.Cursor]:
        """
            Open up the database if required
            This will not re-open or change database names so may be called 
            as many times you wish.
        """
        global _sheet_db_conn, _sheet_db_curr, _sheet_db_location
        # print( "\nopenDB called with '{}', type: {}".format(databaseName, type(databaseName)) )
        # for idx in range( 1,3):
        #     print( "FROM File: '{}' DEF: '{}', Call: {}@{}".format(  
        #         (inspect.stack()[idx][1]), 
        #         (inspect.stack()[idx][3]), 
        #         (inspect.stack()[idx][4]),
        #         (inspect.stack()[idx][2]) ) )
        if _sheet_db_location is None:
            if databaseName is None:
                raise ValueError( "No database name passed")
        elif not isinstance( _sheet_db_location , str ):
            raise ValueError( "Wrong datatype passed: {} (location)".format( type( _sheet_db_location )))

        if self._checkDbName( databaseName ):
            self.closeDB()
        if _sheet_db_conn is None or _sheet_db_curr is None:
            _sheet_db_conn= sqlite3.connect( _sheet_db_location )
            _sheet_db_conn.row_factory=sqlite3.Row
            if trace:
                _sheet_db_conn.set_trace_callback( print )
            _sheet_db_curr = _sheet_db_conn.cursor()
        return self.handles()

    def closeDB( self , clear=False)->Tuple[sqlite3.Connection,sqlite3.Cursor]: 
        global _sheet_db_conn, _sheet_db_curr, _sheet_db_location
        _sheet_db_curr = None
        if clear:
            _sheet_db_location = None
        try:
            _sheet_db_conn.close() 
        except:
            pass
        finally:
            _sheet_db_conn= None
        return (_sheet_db_conn, _sheet_db_curr )

    def connection(self)->sqlite3.Connection:
        """
            This will return just the db connection handle. It will not open or close anything
        """
        global _sheet_db_conn
        return _sheet_db_conn

    def cursor(self)->sqlite3.Cursor:
        """
            This will return the database cursor. It will not open or close any connection
            If the db is not open you will get exception
        """
        global _sheet_db_curr
        return _sheet_db_curr

    def handles(self)->Tuple[sqlite3.Connection,sqlite3.Cursor]:
        global _sheet_db_conn, _sheet_db_curr
        return (_sheet_db_conn, _sheet_db_curr )
    