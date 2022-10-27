from PySide6.QtSql import QSqlQuery, QSqlError
from qdb.util import DbHelper
import logging
from inspect import stack
from os import path

class DbBase():
    """
        A simple class to perform some basic QSql setups
    """
    _wasError = False
    _lastError = None
    _errorMessages = {}
    logger = None

    def __init__(self):
        pass
    
    def setupLogger(self):
        self.logger = logging.getLogger( self.__class__.__name__ )

    def getReturnCode( self, query:QSqlQuery ):
        rtn = self.wasGood() and query.numRowsAffected() > 0
        query.finish()
        return rtn

    def _formatInsertVariable( self, table:str, parms:dict , replace:bool=False, ignore:bool=False)->str:
        """ Take a dictionary and format for an insert 
            You can set mode of insert by setting replace or ignore flags"""
        names  = ','.join( list(parms.keys()) )
        values = ','.join( [ '?' for i in range( 0, len(parms))] )
        if replace:
            insertOp = 'OR REPLACE'
        elif ignore:
            insertOp = 'OR IGNORE'
        else:
            insertOp = ''

        return "INSERT {} INTO {} ({}) VALUES ({})".format( insertOp, table, names, values )

    def _prepareInsertVariable( self, sql, parms:dict)->QSqlQuery:
        return DbHelper.bind( DbHelper.prep( sql ) , list( parms.values() ))

    def _formatUpdateVariable( self, table:str, keyfield:str, keyvalue:str, parms:dict )->str:
        """ 
            Take a dictionary and format for update. 
            You need to pass the keyfield and the keyvalue
            Which cannot be part of the parms
        """
        setlist = [ "{} = ?".format( key.strip('*') ) for key in list( parms.keys() ) ]

        return "UPDATE {} SET {}  WHERE {} = ?".format( table, ','.join(setlist) , keyfield )
    
    def _checkError( self, query:QSqlQuery)->bool:
        self._errorMessages = {'sql': query.lastQuery() ,'values':query.boundValues() }
        self._lastError     = query.lastError()
        self._wasError      = query.lastError().isValid()

        if self._lastError.type() == QSqlError.ConnectionError :
            self._errorMessages['error_type'] = 'Database: Connection Error'
        elif self._lastError.type() == QSqlError.StatementError:
            self._errorMessages['error_type'] = 'Program: SQL Error'
        elif self._lastError == QSqlError.TransactionError:
            self._errorMessage['error_type'] = 'Database: Transaction error'
        elif self._lastError == QSqlError.UnknownError:
            self.errorMessage['error_type'] = '?: Unknown error'
        if self._wasError:
            self._errorMessages['error_db'] = self._lastError.databaseText()
            self._errorMessages['error_driver'] = self._lastError.driverText()
            stacklist = stack()
            for i in range( len(stacklist)-1, 0 , -1):
                stackinfo = stacklist[i]
                tag = 'caller-' + str(len(stacklist) - i)
                fname = "{}/{}".format( path.basename( path.dirname( stackinfo.filename)) , path.basename( stackinfo.filename ) )
                self._errorMessages[tag] = "{}:{}@{}".format( fname , stackinfo.function, stackinfo.lineno ) 
            self.logger.error( "DbBase:\n\t" + "\n\t".join( ["{:12}: '{}'".format(k, self._errorMessages[ k ]) for k in sorted(self._errorMessages ) ] ) )
        return self._wasError
    
    def lastError(self)->QSqlError:
        return self._lastError

    def isError(self)->bool:
        return self._wasError

    def wasGood(self)->bool:
        return not self._wasError

    def logmsg( self  )->str:
        if self._lastError :
            return "Database error: '{}'  Database: '{}' SQL: '{}'".format( 
                self._errorMessages['type'] , 
                self._lastError.databaseText(), 
                self._errorMessages['sql'] )
        return ''
        
    def __init__(self):
        super().__init__()
        self._errorMessages = {}
        self._lastError = QSqlError()
        self._wasError = False