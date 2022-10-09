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

import os
import base64
import pickle
from util.convert     import toBool, toInt
from db.keys        import DbKeys
from db.dbconn      import DbConn
from db.dbsystem    import DbSystem
from PySide6.QtCore import QSettings, QByteArray
from PySide6.QtGui  import QKeySequence

class SystemPreferences(QSettings):
    DEFAULT_ORG = 'OrganMonkey project'
    DEFAULT_APP = 'SheetMusic'
    TEST_APP    = 'SheetMusic_Test'

    def __init__(self, org=DEFAULT_ORG, app=DEFAULT_APP, reset=False):
        super().__init__(org, app)
        if reset:
            self.clear()
            self.saveAll( DbKeys().QSETTINGS_DICT )
        
        ## Save keys to the preferences.
        ## (Note: this saves expanded paths.)
        for key, value in DbKeys().QSETTINGS_DICT.items():
            if value is not None and not self.contains(key):
                self.setValue(key, value)
        self.sync()

    def getAll(self)->dict:
        """
            getAll will only return USER available keys
        """
        rtnDict={}
        for key in DbKeys().QSETTINGS_DICT.keys():
            rtnDict[ key ] = super().value(key )
        return rtnDict

    def saveAll( self, changes:dict):
        """ save will write valid keys into the pref store """
        for key, value in changes.items():
            if key in DbKeys().QSETTINGS_DICT :
                self.setValue( key, value )
        self.sync()

    def getKeys(self)->list:
        """
            Return list of all special system keys
        """
        return DbKeys().PREF_SYS_KEYS

    def getDirectoryDB(self)->str:
        """
            Return the current database directory This does not include the filename
        """
        return os.path.expanduser( self.value( DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB ) )

    def setDirectoryDB(self, newDir:str)->None:
        """
            Set the directory path to the database.
            (This should not include the filename)
        """
        self.setValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB , newDir )

    def getNameDB(self):
        return self.value( DbKeys.SETTING_DEFAULT_MUSIC_FILENAME, DbKeys.VALUE_DEFAULT_DB_FILENAME )

    def setNameDB(self, newFileName:str )->str:
        self.setValue( DbKeys.SETTING_DEFAULT_MUSIC_FILENAME ,  newFileName)

    def getPathDB(self)->str:
        """ 
            Get the full, expanded path to the database
        """
        path = os.path.join( 
            self.value( DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB ), 
            self.value( DbKeys.SETTING_DEFAULT_MUSIC_FILENAME )
        )
        return os.path.expanduser( path)


class DilPreferences( ):
    """
        This handles queries against system properties (database) or system preferences (qsettings)
        Note that you can pass the dbsystem and systempref in order to do unit testing. 
        (Normally, I'd do an inheritence but decided not to in this case)
     """
    def __init__(self, dbsystem=None, systempref=None ):
        super().__init__()
        if dbsystem:
            self.dbsystem = dbsystem
        else:
            self.dbsystem = DbSystem()
        if systempref:
            self.sy = systempref
        else:
            self.sy = SystemPreferences()

    def __del__(self):
        DbConn().connection().commit()

    def getPathDB(self)->str:
        return self.sy.getPathDB()

    def getDirectoryDB(self)->str:
        return self.sy.getDirectoryDB()

    def getValue( self, key:str, default:str=None)->str:
        """
            Get the value from the DbSystem table or, if not found, get the value from the system preferences
        """
        return self.dbsystem.getValue( key , self.sy.value( key , defaultValue=default))

    def getValue64( self, key:str, default:str=None)->bytes:
        b64=self.getValue(key, default=default)
        if b64 is None:
            return None
        return base64.b64decode( b64 ) 

    def getValueBool( self, key:str, default:str=False)->bool:
        return toBool( self.getValue( key, default ))

    def getValueInt( self, key:str, default:int=0)->int:
        return toInt( self.getValue( key, default ))

    def getValuePickle( self, key:str, default:str=None):
        """
            Get a pickled value from the database and restore
            If no value is available then return 'None'
        """
        pkl = self.getValue( key, default ) 
        if pkl is None:
            return None
        return pickle.loads( base64.b64decode( pkl ) )

    def setValuePickle( self, key:str, value:any, conflict:str='OR REPLACE '):
        """
            Save any internal field into the databse by using pickle dump
            and then encoding to ascii
        """
        pval = base64.b64encode( pickle.dumps( value )  ).decode('ascii')
        return self.setValue( key, pval, conflict=conflict )

    def setValue( self, key:str, value:str=None , conflict:str='OR REPLACE ')->str:
        if self.sy.contains(key):
            self.sy.setValue( key , value )
        else:
            self.dbsystem.setValue( key, value, conflict )
        return value 

    def setValue64( self, key:str, value:str=None , conflict:str='OR REPLACE ')->str:
        b64 = base64.b64encode( value )
        return self.setValue( self, key, b64, conflict=conflict )

    def setValueBool( self, key:str, value:any , conflict:str='OR REPLACE ')->bool:
        return self.setValue( key, str( value ), conflict=conflict )

    def getAll(self)->dict:
        return self.sy.getAll() | self.dbsystem.getAll()

    def saveAll(self, changes:dict ):
        """
            Save changes first to the system preferences then to the database
        """
        self.sy.saveAll(changes )
        ## get rid of system stuff
        for key in self.sy.getKeys():
            if key in changes:
                changes.pop( key )
        self.dbsystem.saveAll( changes )

    def update(self, ui):
        ui.format( self.fetchData() )
        ui.exec()
        self.saveAll( self.ui.getChanges() )
    
    def saveMainWindow(self, win):
        '''
        Save window attributes as settings.
        Called when window moved, resized, or closed.
        '''
        
        self.setValuePickle( DbKeys.SETTING_WINDOW_STATE_SAVED, win.saveState() )
        self.setValuePickle( DbKeys.SETTING_WIN_STATE, win.saveState())
        self.setValuePickle( DbKeys.SETTING_WIN_ISMAX, win.isMaximized())
        if not win.isMaximized() == True:
            self.setValuePickle(DbKeys.SETTING_WIN_POS, win.pos())
            self.setValuePickle(DbKeys.SETTING_WIN_SIZE, win.size())
        self.setValueBool( DbKeys.SETTING_WINDOW_STATE_SAVED, True )

    def restoreMainWindow(self, win):
        '''
        Read window attributes from settings,
        using current attributes as defaults (if settings not exist.)

        Called at QMainWindow initialization, before show().
        '''
        if self.getValueBool( DbKeys.SETTING_WINDOW_STATE_SAVED , False):
            win.restoreState( self.getValuePickle(DbKeys.SETTING_WIN_STATE )  )

            isWindowMaximized = self.getValueBool(DbKeys.SETTING_WIN_ISMAX )
            win.restoreGeometry( self.getValuePickle( DbKeys.SETTING_WIN_GEOMETRY) )
            
            win.move(  self.getValuePickle( DbKeys.SETTING_WIN_POS ) )
            win.resize(self.getValuePickle( DbKeys.SETTING_WIN_SIZE ) )
            if isWindowMaximized:
                win.showMaximized()

    def saveShortcut( self, win ):
        pass

    def restoreShortcuts( self, win ):
        values = self.getAll()
        win.setNavigationShortcuts( values )
        win.setBookmarkShortcuts( values )