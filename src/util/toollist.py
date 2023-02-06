
from util.utildir import get_scriptdir, get_user_scriptdir
from os import path, listdir

from ui.runscript import UiScriptSetting, ScriptKeys

class ToolScript():
    Path = 'path'
    Source = 'source'
    Title  = 'title'
    Comment = 'comment'
    Dialog  = 'dialog'
    System = 'system'
    User   = 'user'
    Simple = 'simple'

    def __init__(self, path:str=None, source:str=None, title:str=None, comment:str='', dialog:bool=False, simple:bool=False):
        self.tool = {
            ToolScript.Path: path,
            ToolScript.Source: source,
            ToolScript.Title: title,
            ToolScript.Comment: comment,
            ToolScript.Dialog: dialog,
            ToolScript.Simple: simple,
        }

    def formatMenuOption(self)->str:
        return '{}: ({})'.format( self.tool[ ToolScript.Path , ToolScript.Source ])
    
    def hasDialog(self)->bool:
        return self.tool[ ToolScript.Dialog ]
    
    def isSimple(self)->bool:
        return self.tool[ ToolScript.Simple ]
    
    def path(self)->str:
        return self.tool[ ToolScript.Path ]
    
    def __str__(self)->str:
        return "Path: '{}'\nSource: '{}'\nTitle: '{}'\nDialog: '{}'\nComent: '{}'".format(
            self.tool[ ToolScript.Path    ],
            self.tool[ ToolScript.Source  ],
            self.tool[ ToolScript.Title   ],
            self.tool[ ToolScript.Dialog  ],
            self.tool[ ToolScript.Comment ],
        )

class GenerateToolList():
    toolDictionary = {}
    toolScanned    = False

    def __init__(self):
        self.scriptDir = {
            'system' : get_scriptdir() ,
            'user'   : get_user_scriptdir() }

    def list(self)->dict:
        """ Scan the directories, if required, and return the dictionary """
        self.scanDirectory()
        return GenerateToolList.toolDictionary

    def rescan(self)->dict:
        """ Clear the 'scanned' status flags and rescan"""
        GenerateToolList.toolScanned = False
        GenerateToolList.toolDictionary = {}
        return self.list()

    def find_script(self, script_name:str )->str:
        """ Find the full script path in the script list"""
        list = self.list()
        for key in list:
            if list[key]['path'].find( script_name ) > -1 :
                return list[key]['path']
        return None


    def scanDirectory( self)->bool:
        """ Generate a dictionary of 'title': 'path to file' """

        if not GenerateToolList.toolScanned and len( GenerateToolList.toolDictionary) == 0:
            GenerateToolList.toolScanned = True
            for source,dir in self.scriptDir.items():
                if dir is not None and path.isdir( dir ) :
                    for filename in listdir( dir ):
                        if filename[:1] != '_':
                            fullFilePath=path.join(dir, filename)
                            if path.isfile(fullFilePath):
                                self.addFile( source, fullFilePath, filename  )
            return True
        return False

    def addFile( self, source:str, script_path , filename)->None:
        """ 
        Read the script file and pull title, comment, req and simple 

        Create a dictionary that poinst to a dictionary of:
            title:  Full title with 'type' added
            path:   full script path
            input:  Has 'dialog' tag
            source:   string of user or system
        """

        with open( script_path ) as f: script = f.read()
        self.script_parms = UiScriptSetting( script_path , script , True )

        title = self.script_parms.setting_value( ScriptKeys.TITLE, 'Script:{}'.format( filename ))
        comment = "<br/><p>{}</p><br/>".format( 
                '<br/>'.join( self.script_parms.setting( ScriptKeys.COMMENT,'') ) )
        
        seq = 1
        orig = title
        while title in GenerateToolList.toolDictionary :
            title = "{} #{}".format( orig , seq )
            seq = seq + 1
        tool_entry = ToolScript( 
            title=title,
            path=script_path,
            source=source,
            comment=comment,
            dialog=self.script_parms.isSet( ScriptKeys.DIALOG ), 
            simple=self.script_parms.is_option( ScriptKeys.REQUIRE , ScriptKeys.SIMPLE ),
        )
        GenerateToolList.toolDictionary[ title ]= tool_entry
