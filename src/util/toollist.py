
from util.utildir import get_scriptdir, get_user_scriptdir, get_os_class
from os import path, listdir

from ui.runscript import UiScriptSetting, ScriptKeys


class ToolScript():
    """ 
    ToolScript is like a 'struct': it holds the definitions for a script file found. 
    
    This is used to scan for scripts, include files, etc.
    """
    # Thse are keys within the dictionary
    Comment = 'comment'
    Dialog = 'dialog'
    OS = 'os'
    Path = 'path'
    Simple = 'simple'
    Source = 'source'
    System = 'system'
    Title = 'title'
    User = 'user'

    def __init__(self, path: str = None, source: str = None, title: str = None, comment: str = '', dialog: bool = False, simple: bool = False, os:str=None):
        self.tool = {
            ToolScript.Comment: comment,
            ToolScript.Dialog: dialog,
            ToolScript.OS: os,
            ToolScript.Path: path,
            ToolScript.Simple: simple,
            ToolScript.Source: source,
            ToolScript.Title: title,        
        }

    def formatMenuOption(self, label:str=None) -> str:
        if label is None or label not in self.tool or not self.tool[label]:
            label = ToolScript.Path
        return '{}: ({})'.format(self.tool[label], self.tool[ToolScript.Source])

    def hasDialog(self) -> bool:
        return self.tool[ToolScript.Dialog]

    def isSimple(self) -> bool:
        return self.tool[ToolScript.Simple]

    def path(self) -> str:
        return self.tool[ToolScript.Path]
    
    def comment(self)->str:
        return self.tool[ToolScript.Comment]

    def todict(self )->dict:
        return self.tool 
    
    def __str__(self) -> str:
        return "Path: '{}'\nSource: '{}'\nTitle: '{}'\nDialog: '{}'\nComent: '{}'".format(
            self.tool[ToolScript.Path],
            self.tool[ToolScript.Source],
            self.tool[ToolScript.Title],
            self.tool[ToolScript.Dialog],
            self.tool[ToolScript.Comment],
        )


class GenerateListMixin():
    """
    Mixin script search tool used to generate lists of files.
    """

    def filter_entry( self , script_parms:UiScriptSetting )->bool:
        """ OVERRIDE: change this to filter out entries based on contents of script_parms """
        return True
    
    def _resetDictionary(self) -> None:
        self.toolDictionary = {}

    def _scanDirectory(self, scan_dirs: dict) -> dict:
        """ Pass a list of directories to check, get the files within and add them to tool directory """
        self._resetDictionary()
        for source, dir in scan_dirs.items():
            if dir is not None and path.isdir(dir):
                # Loop through all the files within this directory
                for filename in listdir(dir):
                    if filename[:1] != '_' and filename[:1] != '.': 
                        fullFilePath = path.join(dir, filename)
                        if path.isfile(fullFilePath):
                            self.addFile(source, fullFilePath, filename)
        return self.toolDictionary

    def addFile(self, source: str, script_path, filename) -> None:
        """ 
        Read the script file and pull title, comment, req and simple 

        Create a dictionary entry that points to a dictionary of:
            title:  Full title with 'type' added
            path:   full script path
            input:  Has 'dialog' tag
            source:   string of user or system
            os: What OS this is good for - see filter_entry
        """
        
        with open(script_path) as fh:
            script = fh.read()
        self.script_parms = UiScriptSetting(script_path, script, True)

        title = self.script_parms.setting_value(
            ScriptKeys.TITLE, 'Script:{}'.format(filename))
        comment = "<p>{}</p><br/>".format(
            '<br/>'.join(self.script_parms.setting(ScriptKeys.COMMENT, '')))
        running_os = self.script_parms.flag( ScriptKeys.OS  )
        if self.script_parms.is_set( ScriptKeys.OS ): 
            if not self.filter_entry( self.script_parms ):
                return

        seq = 1
        orig = title
        while title in GenerateToolList.toolDictionary:
            title = "{} #{}".format(orig, seq)
            seq = seq + 1
        tool_entry = ToolScript(
            title=title,
            path=script_path,
            source=source,
            comment=comment,
            os = running_os,
            dialog=self.script_parms.is_set(ScriptKeys.DIALOG),
            simple=self.script_parms.is_option(
                ScriptKeys.REQUIRE, ScriptKeys.SIMPLE),
        )
        self.toolDictionary[title] = tool_entry

    def _find_path(self, toolDictionary: dict, search: str, search_field:str=ToolScript.Path ) -> str:
        for key in toolDictionary:
            if toolDictionary[key][search_field].find(search) > -1:
                return toolDictionary[key][ToolScript.Path]
        return None
    
    def find_script(self, script_name: str) -> str:
        """ Find the full script path in the script list
        
        Override to provide different search methods as required 
        """
        return self._find_path(self.list(), script_name, ToolScript.Path)


class GenerateToolList(GenerateListMixin):
    toolDictionary = {}
    toolScanned = False

    def __init__(self):
        self.scriptDir = {
            'system': get_scriptdir(),
            'user': get_user_scriptdir()}

    def list(self) -> dict:
        """ Scan the directories, if required, and return the dictionary """
        self.scanDirectory()
        return GenerateToolList.toolDictionary

    def rescan(self) -> dict:
        """ Clear the 'scanned' status flags and rescan"""
        GenerateToolList.toolScanned = False
        GenerateToolList.toolDictionary = {}
        return self.list()

    def scanDirectory(self) -> bool:
        """ Generate a dictionary of 'title': 'path to file' """

        if not GenerateToolList.toolScanned and len(GenerateToolList.toolDictionary) == 0:
            GenerateToolList.toolScanned = True
            GenerateToolList.toolDictionary = self._scanDirectory(
                self.scriptDir)
            return True
        return False


class GenerateEditList(GenerateListMixin):
    def __init__(self):
        system = get_scriptdir()
        self.scan_list = {
            'pageedit': path.join(system, 'pageedit'),
        }
        self.scanDirectory()

    def scanDirectory(self) -> bool:
        """ Generate a dictionary of 'title': 'path to file' """
        self._editor_list = self._scanDirectory(self.scan_list)
        return True

    def list(self) -> dict:
        """ Scan the directories, if required, and return the dictionary """
        return self._editor_list

    def rescan(self) -> dict:
        """ Clear the 'scanned' status flags and rescan"""
        self.scanDirectory()
        return self._editor_list

  
class GenerateImportList( GenerateListMixin ):
    def __init__(self):
        self.os = get_os_class()
        self.scan_list = {
            'importpdf': path.join(get_scriptdir(), 'importpdf'),
        }
        self.scanDirectory()

    def filter_entry(self, script_parms: UiScriptSetting) -> bool:
        if ( script_parms.is_option( ScriptKeys.OS , self.os ) or 
            script_parms.is_option( ScriptKeys.OS , ScriptKeys.OS_ANY ) ):
            return True
        return False

    def scanDirectory(self) -> bool:
        """ Generate a dictionary of 'title': 'path to file' """
        self._import_list = self._scanDirectory(self.scan_list)
        return True

    def list(self) -> dict:
        """ Scan the directories, if required, and return the dictionary """
        return self._import_list

    def rescan(self) -> dict:
        """ Clear the 'scanned' status flags and rescan"""
        self.scanDirectory()
        return self._import_list

