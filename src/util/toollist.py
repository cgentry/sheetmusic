
import pathlib
from os import path, listdir

from ui.runscript import UiScriptSetting, ScriptKeys

class GenerateToolList():
    toolDictionary = {}
    toolScanned    = False

    def __init__(self):
        self.utilDir   = path.dirname( path.realpath(__file__) )
        self.scriptDir = path.join( self.utilDir, 'scripts')
                
    def list(self)->dict:
        self.scanDirectory()
        return GenerateToolList.toolDictionary

    def rescan(self):
        self.toolScanned = False
        self.toolDictionary = {}
        self.scanDirectory(self )

    def scanDirectory( self):
        """ Generate a dictionary of 'title': 'path to file' """
        if not GenerateToolList.toolScanned and len( GenerateToolList.toolDictionary) == 0:
            GenerateToolList.toolScanned = True
            if path.isdir( self.scriptDir ) :
                for filename in listdir(self.scriptDir):
                    fullFilePath=path.join(self.scriptDir, filename)
                    if path.isfile(fullFilePath):
                        self.addFile( fullFilePath, filename  )

    def addFile( self, script_path , filename):
        with open( script_path ) as f: script = f.read()
        self.script_parms = UiScriptSetting( script_path , script , True )
        title = self.script_parms.settingValue( ScriptKeys.TITLE, 'Script:{}'.format( filename ))
        comment = "<br/><p>{}</p><br/>".format( 
                '<br/>'.join( self.script_parms.setting( ScriptKeys.COMMENT,'') ) )
        input_req = ','.join( self.script_parms.setting( ScriptKeys.REQUIRE , ['(none)']) )
        simple = self.script_parms.isOption( ScriptKeys.REQUIRE , ScriptKeys.SIMPLE )

        seq = 1
        orig = title
        while title in GenerateToolList.toolDictionary :
            title = "{} ({})".format( orig , seq )
            seq = seq + 1
        GenerateToolList.toolDictionary[ title ]= { 
            'path': script_path , 
            ScriptKeys.COMMENT: comment, 
            ScriptKeys.REQUIRE: input_req ,
            ScriptKeys.SIMPLE:  simple 
        }
