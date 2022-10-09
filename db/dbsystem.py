
from multiprocessing.sharedctypes import Value
from db.dbsql  import SqlGetID
from db.dbconn import DbConn
from db.keys   import DbKeys
from db.dbgeneric import DbTransform

class DbSystem():
    """
        You should have already opened the database and
        kept the handle alive. If not, oh dear, this might
        not work well
    """
    SQL_SYSTEM_GET="SELECT value FROM System WHERE key=?"
    SQL_SYSTEM_GET_ALL="""
        SELECT key, value
        FROM System
    """
    SQL_SYSTEM_INSERT="INSERT {}INTO System (key, value) VALUES( ?, ?)"
    SQL_SYSTEM_INSERT_REPLACE='OR REPLACE '
    SQL_SYSTEM_INSERT_IGNORE="OR IGNORE "
    SQL_SYSTEM_INSERT_FAIL=""
    SQL_SYSTEM_DELETE = "DELETE FROM System Where key=?"

    def __init__( self ):
        (self.conn, self.cursor ) = DbConn().openDB(  )
        pass

    def getAll( self )->dict:
        """
            Return all the values in the database as a dictionary
            Note you really should be doing a 'get' for values you 
            want rather than sucking in all of them. This is used by
            the UI interface
        """
        return DbTransform().toDictionary( 
            self.cursor.execute( self.SQL_SYSTEM_GET_ALL).fetchall(),
            key='key', 
            data='value' 
        )

    def saveAll( self , newData:list ):
        """
            The input should be a list of dictionary values:
                [ {key:..., value:...}, {key:..., value:...}]
            You should set them one-by-one, but this is used by the UI interface
        """
        for item in newData:
            self.setValue( item['key'], item['value'] )

    def getValue( self, key:str, default:str=None)->str:
        if key is None or key == '':
            return default
        result = self.cursor.execute( self.SQL_SYSTEM_GET, [key])
        row = result.fetchone()
        if row is None:
            return ( None if default is None else str( default ) )
        return str( row['value'] )

    def _insertConflict( self, conflict:str )->str:
        if conflict == None:
            return ""
        if not conflict in [self.SQL_SYSTEM_INSERT_IGNORE, self.SQL_SYSTEM_INSERT_FAIL, self.SQL_SYSTEM_INSERT_REPLACE]:
            conflict = conflict.lower()
            if conflict == 'ignore':
                return self.SQL_SYSTEM_INSERT_IGNORE
            if conflict == 'replace':
                return self.SQL_SYSTEM_INSERT_REPLACE
            if conflict == 'fail':
                return self.SQL_SYSTEM_INSERT_FAIL
            raise ValueError( 'Conflict statement is invalid')
        return conflict
        
    def setValue( self, key:str, value:str=None , conflict:str='OR REPLACE ')->str:
        """
            setValue will do one of three things, depending on 'conflict'
            1. SQL_SYSTEM_INSERT_REPLACE - perform an upsert
            2. SQL_SYSTEM_INSERT_IGNORE - will insert if doesn't exist, otherwise do nothing
            3. SQL_SYSTEM_INSERT_FAIL: fail if key exists. Not the best, but up to you.
            Anything else will fail.
            The final value will be returned
        """
        if key is None or key == '' :
            raise ValueError('No key passed')
        if value is None:
            self.cursor.execute( self.SQL_SYSTEM_DELETE, [ key ])
            return None
        self.cursor.execute( self.SQL_SYSTEM_INSERT.format(self._insertConflict(conflict)), (str(key),str(value)) )
        return self.getValue( key )
