

from qdb.keys import LOG
from qdb.dbconn import DbConn
from qdb.util   import DbHelper
from inspect import stack


class DbLog:
    """ Generic logging to database. This will filter and log messages until a log limit is reached"""

    INSERT = "INSERT INTO Log ( level, class, method , msg  ) VALUES (?, ?, ? ,? )"
    def __init__(self, classname:str='', level:int=1):
        self.setlevel( level )
        self.setclass( classname )

    def setlevel( self, loglevel:int):
        self._loglevel = max( min( LOG.critical , loglevel ), LOG.debug ) 

    def setclass( self, proc:str ):
        self._classname = proc

    def log( self, level:int , method:str, msg:str ):
        print( 'Loglevel: {} Level: {}, method: {} msg {}'.format( self._loglevel, level, method, msg ))
        if level >= self._loglevel:
            query = DbHelper.prep( DbLog.INSERT )
            query = DbHelper.bind( query, [ level, self._classname,  method, msg ] )
            query.exec()
            query.finish()
            del query

    def debug( self, msg:str ):
        return self.log( LOG.debug , stack()[1].function , msg )
    
    def info( self, msg:str ):
        return self.log( LOG.info , stack()[1].function , msg )
    
    def warning(self, msg:str ):
        return self.log( LOG.warning , stack()[1].function , msg )
    
    def critical(self, msg:str ):
        return self.log( LOG.critical , stack()[1].function , msg )
    
    def error( self,  msg:str ):
        return self.log( LOG.critical, stack()[1].function , msg )