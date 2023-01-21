# Simple utility to get script and util full paths

from os import path


def get_utildir()->str:
    return path.dirname( path.realpath(__file__) )

def get_scriptdir()->str:
    return path.join( get_utildir(), 'scripts')

def get_scriptpath( filename:str)->str:
    return path.join( get_utildir(), 'scripts' ,filename )