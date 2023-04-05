

from qdb.keys import LOG
from qdb.util   import DbHelper
from inspect import stack


class Trace():
    def calls( depth:int=4 , start:int=0)->list:
        slen = min( len( stack() ), depth+start) 
        scalls = []
        counter = 1
        for index in range( start, slen ):
            sdict = stack()[index]
            scalls.append( "{}: {:>20s}@{:4d} File:{}".format( counter, sdict[3] , sdict[2] , sdict[1]))
            counter += 1
        return scalls
    
    def callstr( header:str="", depth:int=4, start:int=2 )->str:
        return ( "{}\n\t{}".format(header, "\n\t".join( Trace.calls( depth, start )) ) )
    
    def printout( header:str="", depth=4 , start:int=1):
        print( Trace.callstr( header, depth, start ) )

class DbLog:
    """ Generic logging to database. This will filter and log messages until a log limit is reached"""

    INSERT = "INSERT INTO Log ( level, class, method , msg  ) VALUES (?, ?, ? ,? )"
    SQL_LEVEL  = 'SELECT value FROM System WHERE key="logging_enabled"'
    SQL_CLEAR  = 'DELETE FROM Log WHERE level <= ?'
    _loglevel = None

    def __init__(self, classname:str='', level:int=None):
        self.setlevel( level )
        self.setclass( classname )

    def setlevel( self, loglevel:int=None):
        if loglevel is None and DbLog._loglevel is None:
            loglevel = int( DbHelper.fetchone( DbLog.SQL_LEVEL , default=LOG.disabled ) )
        self._loglevel = max( min( LOG.critical , loglevel ), LOG.disabled ) 

    def setclass( self, proc:str ):
        self._classname = proc

    def log( self, level:int , method:str, msg:str , trace=False):
        if level >= self._loglevel and self._loglevel > 0 :
            query = DbHelper.prep( DbLog.INSERT )
            if trace:
                msg = Trace.callstr( msg , start=2)
            query = DbHelper.bind( query, [ level, self._classname,  method, msg ] )
            query.exec()
            query.finish()
            del query

    def debug( self, msg:str , trace=False):
        return self.log( LOG.debug , stack()[1].function , msg , trace )
    
    def info( self, msg:str , trace=False ):
        return self.log( LOG.info , stack()[1].function , msg , trace)
    
    def warning(self, msg:str ,trace=True ):
        return self.log( LOG.warning , stack()[1].function , msg , trace)
    
    def critical(self, msg:str , trace=True):
        return self.log( LOG.critical, stack()[1].function, msg , trace )
    
    def error( self,  msg:str , trace=True ):
        return self.log( LOG.critical, stack()[1].function , msg , trace)
    
    def clear(self, level:int):
        query = DbHelper.prep( DbLog.SQL_CLEAR )
        query = DbHelper.bind( query , [ level ])
        query.exec()
        query.finish()
        del query
        DbHelper.prep( 'VACUUM;').exec()
        