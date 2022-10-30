
# This module is part of sheetmusic and uses QtSQL packages

from PySide6.QtSql  import QSqlDatabase, QSqlQuery
from qdb.keys       import DbKeys
import logging

_qdb_conn = None
_qdb_name = None
_qdb_path = None

class DummyConnection:
    def commit(self):
        print("Obsolete call to commit")

    def close(self):
        print("Obsolete call to close")

class DbConn():
    DB_NAME = 'sheetmusic'

    @staticmethod
    def clearLastName():
        global _qdb_path, _qdb_name
        _qdb_path = None
        _qdb_name = None

    @staticmethod
    def isOpen()->bool:
        global _qdb_name
        return QSqlDatabase.database(_qdb_name,open=False).isOpen()

    @staticmethod
    def isValid(open=False)->bool:
        global _qdb_name
        return QSqlDatabase.database( _qdb_name, open=open).isValid()

    @staticmethod
    def name()->str:
        """ This will return the connection name, not the db name """
        global _qdb_conn
        return (QSqlDatabase.connectionName(_qdb_conn) if _qdb_conn is not None else None)

    @staticmethod
    def dbname()->str:
        """ This will return the db name ( VALUE_DEFAULT_DB_FILENAME ) """
        global _qdb_conn
        return (QSqlDatabase.databaseName(_qdb_conn) if _qdb_conn is not None else None)

    @staticmethod
    def getConnection( open=False)->QSqlDatabase:
        global _qdb_name
        rtn =  QSqlDatabase.database( _qdb_name, open=open)
        return rtn if rtn.isValid() else None

    @staticmethod
    def openDB( databasePath:str=None, connectionName:str=DbKeys.VALUE_DEFAULT_DB_FILENAME, trace:bool=False )->QSqlDatabase:
        global _qdb_conn, _qdb_name, _qdb_path
        #print("\nOPEN DB")
        #print("\topen database path  :{:15s}, global:{:15s}".format( str(databasePath), str(_qdb_path) ) )
        #print("\topen database named :{:15s}, global:{:15s}".format( str(connectionName), str(_qdb_name) ) )
        if _qdb_conn is None or not _qdb_conn.isValid():
            if databasePath is None:
                if _qdb_path is None:
                    raise ValueError("\tNo database name passed")
                else:
                    return DbConn.reopenDB( )
        else: # _qdb_conn is not none
            #print("\tRe-establish open")
            _qdb_conn.open()
            return _qdb_conn

        _qdb_path = databasePath
        _qdb_conn = QSqlDatabase.addDatabase("QSQLITE", connectionName=connectionName )
        _qdb_conn.setDatabaseName( databasePath )

        _qdb_name = QSqlDatabase.connectionName(_qdb_conn )
        #print("\t_qdb_name is now", _qdb_name)
        
        _qdb_conn.open()
        #print("\tEND OPENDB")
        #print("- "*50)
        return _qdb_conn

    @staticmethod
    def db()->QSqlDatabase:
        return DbConn.reopenDB()

    @staticmethod
    def closeDB():
        global _qdb_conn
        """ This will close the db but doesn't destroy the db entry """
        if _qdb_conn is not None and _qdb_conn.isOpen():
            _qdb_conn.commit()
            _qdb_conn.close()
        
    @staticmethod
    def destroyConnection():
        global _qdb_conn, _qdb_name
        """ Only call this if you are exiting the program """
        DbConn.closeDB()
        _qdb_conn = None
        QSqlDatabase.removeDatabase( _qdb_name)
        _qdb_name = None
        
    @staticmethod
    def reopenDB()->QSqlDatabase:
        global _qdb_name, _qdb_conn
        _qdb_conn =  QSqlDatabase.database( _qdb_name , open=True )
        if not _qdb_conn.isValid():
            logging.critical( "DB Open error: {}".format(  _qdb_conn.lastError().text() ) )
        return _qdb_conn

    @staticmethod
    def query()->QSqlQuery:
        return QSqlQuery( DbConn.db() )

    @staticmethod
    def connection()->DummyConnection:
        return DummyConnection()

    @staticmethod
    def handles():
        """ OBSOLETE: This returns a fake connection and a valid query
            this will be removed after code cleanup occurs
        """
        return (DbConn.connection() , DbConn.cursor() )


    @staticmethod
    def getColumnNames( table:str )->list:
        global _qdb_conn
        """ Retrieve a list of all column names from the database 
            (Usefull when creating queries) 
        """
        if not _qdb_conn or _qdb_conn.isOpenError() :
            raise RuntimeError( "Database is not open")
        columns = []
        record = _qdb_conn.record( table )
        for index in range( 0 , record.count() ):
            name = record.fieldName(index)
            if name.__contains__(':'):
                x = name.split(':')
                columns.append( x[0] )
            else:
                columns.append( name )
        return columns

    @staticmethod
    def commit()->bool:
        global _qdb_conn
        if _qdb_conn is not None and _qdb_conn.isOpen():
            return  _qdb_conn.commit()
        return False

    @staticmethod
    def cleanDB( ):
        global _qdb_conn
        query = QSqlQuery( _qdb_conn )
        for table in DbKeys().primaryKeys:
            query.exec( "REINDEX {};".format( table ))
    
        query.exec("vacuum;")
        query.finish()
        del query

    @staticmethod
    def dump( filename:str ):
        global _qdb_conn
        # query = QSqlQuery( DbConn.db() )
        # with open(filename, 'w') as f:
        #     for line in con.iterdump():
        #         f.write('%s\n' % line)
        pass