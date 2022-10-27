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


#####
# dbgenerics are the base classes for simple database retrieval
# there are:
#   DbGenericName - a single key table
#   DbGenericKeyValue - simple key/value table
import logging
from typing import Any
from qdb.dbconn import DbConn
from qdb.util   import DbHelper
from PySide6.QtSql  import QSqlQuery

class DbGenericName( ):
    tableName=""
    fieldNames = ['name','value','id']
    SQL_GET_LIKE="""
        SELECT name, value, id
        FROM :TABLE
        WHERE name LIKE ?
        ORDER BY name COLLATE NOCASE
        """
    SQL_SELECT_ID="""SELECT id FROM :TABLE WHERE name=?"""
    SQL_SELECT_ALL="""
        SELECT name 
        FROM :TABLE 
        ORDER BY name COLLATE NOCASE :sequence"""
    SQL_EDIT_NAME ="""
        UPDATE :TABLE  
        SET name = :newValue 
        WHERE name = :oldValue"""
    SQL_GET_ID="SELECT id FROM :TABLE WHERE name=?"
    SQL_INSERT="INSERT INTO :TABLE (name) VALUES (?)"

    def __init__(self, table:str=None):
        if table is not None:
            self.tableName = table
        
    def setupLogger(self):
        self.logger = logging.getLogger( self.__class__.__name__ )

    def getall(self, sequence='ASC')->list:
        """ Fetch the 'name' field from the database and return it as a list (rather than a row) """
        query = QSqlQuery( DbConn.db() )
        if not query.exec( self.SQL_SELECT_ALL.replace( ':sequence', sequence).replace(':TABLE', self.tableName ) ):
            self.logger.critical( "getall: {}".format(  query.lastError().text() ) )
            return []
        all =  DbHelper.allList( query  , 0 )
        query.finish()
        del query
        return all

        return self.toList( self.cursor.execute( sql).fetchall() )

    def getID( self, name:str , create:bool=False )->int:
        """ This will lookup the record ID for 'name'.
            If create is true, a new record will be created 
        """
        sql = self.SQL_SELECT_ID.replace(':TABLE', self.tableName)
        val = DbHelper.fetchone( sql , name)
        if val is None and create:
            val = self.insertID( name )
        return val

    def insertID( self, name:str )->int:
        sql = self.SQL_INSERT.replace(':TABLE', self.tableName)
        query = DbHelper.bind( DbHelper.prep( sql ) ,  name )
        val = ( query.lastInsertId() if query.exec() else None )
        query.finish()
        return val

    def edit( self, oldValue:str, newValue:str, commit=True)->int:
        if oldValue is None or newValue is None:
            return 0
        sql = self.SQL_EDIT_NAME.replace(':TABLE', self.tableName)
        query = DbHelper.bind( DbHelper.pref( sql ),  
            {'newValue' : newValue, 'oldValue': oldValue } )
        rows = ( query.numRowsAffected if query.exec() else 0 )
        query.finish()
        return rows

    def has( self, name:str )->bool:
        """
            return True if record exists, False otherwise
        """
        return ( self.getID( name ) is not None )