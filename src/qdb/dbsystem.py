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

#
# This file is part of verion 0.3 - a move to use the QT Sql framework
# Previous versions used the python SQL. This should allow better integration
# into the widgets that QT provides
#
# There is minimal effort to make this similar to version 0.2
#
from qdb.dbconn import DbConn
from qdb.util   import DbHelper
from qdb.base   import DbBase
from PySide6.QtSql import QSqlQuery
import logging

class DbSystem(DbBase):
    """
        You should have already opened the database.
        You can improve performance by instantiating this once 
        and all the statments get prepared. Makes it much faster
    """

    SQL_SYSTEM_GET           = "SELECT value FROM System WHERE key=?"   
    SQL_SYSTEM_GET_ALL       = "SELECT key, value FROM System"  
    SQL_SYSTEM_INSERT_REPLACE= "INSERT OR REPLACE INTO System (key, value) VALUES( ?, ?)"   
    SQL_SYSTEM_INSERT_IGNORE = "INSERT OR IGNORE INTO System (key, value) VALUES( ?, ?)"
    SQL_SYSTEM_INSERT_FAIL   = "INSERT INTO System (key, value) VALUES( ?, ?)"
    SQL_SYSTEM_DELETE        = "DELETE FROM System Where key=?"

    SQL_FLAG_INSERT_REPLACE=1
    SQL_FLAG_INSERT_IGNORE=2
    SQL_FLAG_INSERT_FAIL=0

    sql_has_been_prepared = False
    
    def __init__(self):
        super().__init__()
        self.setupLogger()
    
    def     getAll( self )->dict:
        """
            Return all the values in the database as a dictionary
            Note you really should be doing a 'get' for values you 
            want rather than sucking in all of them. This is used by
            the UI interface
        """
        values = {}
        query = QSqlQuery( DbConn.db() )
        if query.exec( DbSystem.SQL_SYSTEM_GET_ALL ):
            while query.next():
                values[ query.value(0)] = query.value(1)
        else:
            self.logger.error( "{}".format( query.lastError().text() ) )
        self._checkError( query )
        query.finish()
        return values 

    def saveAll( self , newData:dict , replace:bool=False, ignore:bool=False )->int:
        """
            The input should be either dictionary values:
                {key:..., value:..., key:..., value:...}
            or a list of key/value pairs:
                [ {key: value}, {key: value}....]
            anything else raises value error
            You should set them one-by-one, but this is used by the UI interface
        """
        if isinstance( newData , list ):
            dataDict = {}
            for item in newData:
                if 'key' in item and 'value' in item:
                    dataDict[ item['key']] = item['value']
            newData = dataDict
        elif not isinstance( newData, dict ):
            msg = "saveAll: Invalid type passed '{}'".format( type( newData ))
            self.logger.error( msg )
            raise ValueError( msg )

        count = 0
        for key, value in newData.items():
            try:
                if self.setValue( key, value , replace=replace, ignore=ignore ):
                    count=count+1
            except Exception as err:
                msg = "saveAll: type '{}' value '{}'".format( type( item ), item)
                self.logger.exception( msg ,stacklevel=1 )
                raise err
        return count

    def getValue( self, key:str, default:str=None)->str:
        rtn = default
        if key:
            rtn = DbHelper.fetchone( self.SQL_SYSTEM_GET , key , default=default)
        return rtn
    
    def setValue( self, key:str, value:str=None , replace:bool=False, ignore:bool=False )->bool:
        """
            if the value is None, the key will be deleted from the database
            True or false will be returned if the operation is a success
        """
        if key is None or key == '' :
            raise ValueError('No key passed')
        if value is None:
            query = DbHelper.bind( DbHelper.prep(self.SQL_SYSTEM_DELETE ), key)
            query.exec()
            self._checkError( query )
            query.finish()
            del query
            return self.wasGood()

        values = { 'key': key, 'value': value }
        sql =self._formatInsertVariable( 'System', values , replace=replace, ignore=ignore )
        query = QSqlQuery( DbConn.db() )
        query.prepare( sql )
        query.addBindValue( key )
        query.addBindValue( value )
        query.exec()
        self._checkError(query )
        query.finish()
        del query
        return self.wasGood()
     
    
