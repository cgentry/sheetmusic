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

from typing import Any
from db.dbconn import DbConn

class DbTransform():
    """
    This class allows you to convert from rows to dictionaries 
    or lists
    """
    def rowToDictionary( self, row ):    
        if row is None:
            return None
        result = {}
        for key in row.keys():
            result[key] = row[key]
        return result

    def toDictionary( self, rows=None , key='id', data='name')->dict:
        if rows is None:
            return {}
        return { row[key]:row[data] for row in rows }

    def toList( self, rows , data='name')->list:
        """
            Run through rows and select only the desired data
            The column you want is passed as 'data'
        """
        if rows is None or len(rows) == 0 :
            return []
        return [ row[data] for row in rows ]

class DbGenericName( DbTransform):
    tableName=""
    fieldNames = ['name','value','id']
    SQL_GET_LIKE="""
        SELECT * 
        FROM :TABLE
        WHERE name LIKE ?
        ORDER BY name COLLATE NOCASE
        """
    SQL_SELECT_ONE="""
        SELECT *
        FROM :TABLE
        WHERE name=?
        """
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
        (self.conn,self.cursor) = DbConn().openDB()

    def getall(self, sequence='ASC')->list:
        """ Fetch the 'name' field from the database and return it as a list (rather than a row) """
        sql = (self.SQL_SELECT_ALL.replace(':TABLE', self.tableName)).replace(':sequence', sequence )
        return self.toList( self.cursor.execute( sql).fetchall() )

    def has( self, name:str )->bool:
        """
            return True if record exists, false otherwise
        """
        sql = self.SQL_SELECT_ONE.replace(':TABLE', self.tableName)
        row = self.cursor.execute( sql , [name]).fetchone()
        return row is not None and row['name']

    def getID( self, name:str )->int:
        return self.getorsetId( name, create=False)

    def getorsetId( self, name:str , create=True)->int:
        """
            This will get a record ID for a 'name'. If create is true,
            and there is no record, one will be inserted and the record ID will
            be returned
        """
        sql = self.SQL_SELECT_ONE.replace(':TABLE', self.tableName)
        row = self.cursor.execute( sql , [name]).fetchone()
        if row is not None and row['name']:
            return int( row['id'] )
        if not create:
            return None
        
        self.cursor.execute(self.SQL_INSERT.replace(':TABLE', self.tableName), [name])
        self.conn.commit()
        return self.cursor.lastrowid


    def edit( self, oldValue:str, newValue:str, commit=True)->int:
        if oldValue is None or newValue is None:
            return 0
        self.cursor.execute( self.SQL_EDIT_NAME.replace(':TABLE', self.tableName), 
            {'newValue' : newValue, 'oldValue': oldValue } )
        if commit:
            self.conn.commit()
        return self.cursor.rowcount

