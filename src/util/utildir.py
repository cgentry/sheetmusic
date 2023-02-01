# Simple utility to get script and util full paths

from os import path

def get_utildir()->str:
    """ Return the path of the utility directory"""
    return path.dirname( path.realpath(__file__) )

def get_scriptdir()->str:
    """ Return the path of the system script directory """
    return path.join( get_utildir(), 'scripts')

def get_scriptinc()->str:
    """ Return the path of the system script include directory """
    return  path.join( get_utildir() , 'scripts', 'include' )

def get_scriptpath( filename:str)->str:
    return path.join( get_utildir(), 'scripts' ,filename )

def get_user_scriptdir()->str:
    """ Return the full path of user scripts or None if directory doesn't exist """
    from qdil.preferences import DilPreferences
    from qdb.keys import DbKeys
    pref = DilPreferences()
    uscripts =  path.realpath( pref.getValue( DbKeys.SETTING_PATH_USER_SCRIPT , DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR))
    if not path.isdir( uscripts ):
        return None
    return uscripts