# Simple utility to get script and util full paths

from os import path
import platform

def get_utildir()->str:
    """ Return the path of the utility directory"""
    return path.dirname( path.realpath(__file__) )

def get_scriptdir()->str:
    """ Return the path of the system script directory """
    return path.join( get_utildir(), 'scripts')

def get_user_scriptdir()->str:
    """ Return the full path of user scripts or system if directory doesn't exist """
    from qdil.preferences import DilPreferences
    from qdb.keys import DbKeys
    pref = DilPreferences()
    uscripts =  path.realpath( pref.getValue( DbKeys.SETTING_PATH_USER_SCRIPT , DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR))
    return uscripts if path.isdir( uscripts ) else get_scriptdir()

def get_scriptinc()->str:
    """ Return the path of the system script include directory """
    return  path.join( get_utildir() , 'scripts', 'include' )

def get_user_scriptinc()->str:
    """ return the path for user scripts. If there is no path it returns the system include"""
    return path.join( str(get_user_scriptdir() ), 'include' )

def get_scriptpath( filename:str)->str:
    """ Return the path for system scripts """
    return path.join( str(get_utildir()), 'scripts' ,filename )

def get_os_class( )->str:
    """ Get short abbreviation for what OS we are running"""
    os = platform.platform(terse=True).lower()
    if os.startswith( 'macos'):
        return 'macos'
    if os.__contains__( 'bsd'):
        return 'bsd'
    if os.__contains__('linux'):
        return 'linux'
    if os.__contains__('win'):
        return 'win'
    return os
