"""
Database interface: Logging interface

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from inspect import stack
from dataclasses import dataclass
from qdb.util import DbHelper

@dataclass(init=False, frozen=True)
class LOG:
    """ Data definition class"""
    disabled = 0
    debug = 1
    info = 2
    warning = 3
    critical = 4


LOGSTR = {LOG.debug: 'debug', LOG.info: 'info',
          LOG.warning: 'warning', LOG.critical: 'critical'}

class Trace():
    """
    A collection of static routines to fetch
    information from the stack and trace.
    Used for debugging.
    """
    @staticmethod
    def calls( depth:int=4 , start:int=0)->list:
        """Return a list of calls

        Args:
            depth (int, optional): Number of entries to return. Defaults to 4.
            start (int, optional): Starting point in stack. Defaults to 0.

        Returns:
            list: _description_
        """
        slen = min( len( stack() ), depth+start)
        scalls = []
        counter = 1
        for index in range( start, slen ):
            sdict = stack()[index]
            scalls.append( f"{counter}: {sdict[3]:>20s}@{sdict[2]:4d} File:{sdict[1]}")
            counter += 1
        return scalls

    @staticmethod
    def callstr( header:str="", depth:int=4, start:int=2 )->str:
        """Format a the call string

        Args:
            header (str, optional): Header string. Defaults to "".
            depth (int, optional): How deep the number of calls. Defaults to 4.
            start (int, optional): Offset in stack. Defaults to 2.

        Returns:
            str: _description_
        """
        calls = "\n\t".join( Trace.calls( depth, start ))
        return  f"{header}\n\t{calls}"

    @staticmethod
    def printout( header:str="", depth=4 , start:int=1):
        """ Printout the call sheader trace"""
        print( Trace.callstr( header, depth, start ) )

class DbLog:
    """ Generic logging to database.
    This will filter and log messages until a log limit is reached"""

    INSERT = "INSERT INTO Log ( level, class, method , msg  ) VALUES (?, ?, ? ,? )"
    SQL_LEVEL  = 'SELECT value FROM System WHERE key="logging_enabled"'
    SQL_CLEAR  = 'DELETE FROM Log WHERE level <= ?'
    _loglevel = None

    def __init__(self, classname:str='', level:int=None):
        self.setlevel( level )
        self.setclass( classname )

    def setlevel( self, loglevel:int=None)->None:
        """ Set what 'level' you want.
        Levels are defined in the DbLog.SQL_LEVEL"""
        if loglevel is None and DbLog._loglevel is None:
            loglevel = int( DbHelper.fetchone( DbLog.SQL_LEVEL , default=LOG.disabled ) )
        self._loglevel = max( min( LOG.critical , loglevel ), LOG.disabled )

    def setclass( self, proc:str )->None:
        """ Set the classname for logging """
        self._classname = proc

    def log( self, level:int , method:str, msg:str , trace=False)->None:
        """ Log a message and any trace requested."""
        if level >= self._loglevel and self._loglevel > 0 :
            query = DbHelper.prep( DbLog.INSERT )
            if trace:
                msg = Trace.callstr( msg , start=2)
            query = DbHelper.bind( query, [ level, self._classname,  method, msg ] )
            query.exec()
            query.finish()
            del query

    def debug( self, msg:str , trace=False):
        """ output a debug message with optional trace"""
        return self.log( LOG.debug , stack()[1].function , msg , trace )

    def info( self, msg:str , trace=False ):
        """ output a Info message with optional trace"""
        return self.log( LOG.info , stack()[1].function , msg , trace)

    def warning(self, msg:str ,trace=True ):
        """ output a Warning message with optional trace"""
        return self.log( LOG.warning , stack()[1].function , msg , trace)

    def critical(self, msg:str , trace=True):
        """ output a critical message with optional trace"""
        return self.log( LOG.critical, stack()[1].function, msg , trace )

    def error( self,  msg:str , trace=True ):
        """ output an error message with option trace """
        return self.log( LOG.critical, stack()[1].function , msg , trace)

    def clear(self, level:int):
        """ Clear the log file and cleanup """
        query = DbHelper.prep( DbLog.SQL_CLEAR )
        query = DbHelper.bind( query , [ level ])
        query.exec()
        query.finish()
        del query
        DbHelper.prep( 'VACUUM;').exec()
