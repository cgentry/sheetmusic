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

## runscript will run the system shell and pass it several variables
## The first variable will be the shell script. Other variables can be
## passed in a list. For example, if you have a file 'doit.sh' and you
## you want to pass it two filenames (/dir/a.txt and /dir/b.txt) you would
## call the runner as:
##      myrun = UiRunScript( 'doit.sh', [ '/dir/a.txt' , '/dir/b.txt'])
##      myrun.run()
##
## This will handle several tags within the script:
##      #:title  Title of the script to put into the top label
##               (ignored for shell scripts at this point)
##      #:comment This can be a multi-line comment. that will be
##              displayed in the box before it begins
##      #:width  How WIDE to set the dialog. Max is 2048, min 500
##      #:heigth Just how HIGH do you want the box. Max is 1024, min 500
##      #:inc    file to include (for settings)
##               allows you to have global settings for flag, setting, etc.
##               File must be relative to the tool directory ( inc/file )
##      #:flag   keywords that control how parameters are passed
##          example: #:flag file f prefix dash dir d version v
##
##          prefix  - either 'dash' or 'blank'  default DASH
##          file    - tag used for passing file entry
##          dir     - tag used for passing directory entry
##          version - tag used for versioning
##          dbfile  - tag used for passing database file
##
##      #:setting setting values
##          dbfile   where db is located (path)
##          version  current code version
##
##      #:require what (optional) values must be entered
##          file    if there is a file-prompt, make file required
##          dir     if there is a dir-prompt,  make directory required
##
##      RESERVED WORDS FOR TAGS:
##          title, comment, width, height, inc, flag, prefix, file, dir, version, dbfile, setting

from os import chmod
import tempfile
import time

from os import path, chmod
from pathlib import PurePath
import tempfile
import time

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
        QDialogButtonBox,       QDialog, 
        QMessageBox,        QPlainTextEdit, 
        QTabWidget,         QVBoxLayout,
        QWidget,            QLineEdit,
        QFileDialog,        QCheckBox,
        QHBoxLayout,
    )
from PySide6.QtGui  import QFont, QTextCursor

from qdb.keys          import DbKeys, ProgramConstants
from util.convert      import toInt
from qdil.preferences  import DilPreferences, SystemPreferences

from PySide6.QtCore    import Qt
import re

class ScriptKeys:
    COMMENT     = 'comment'
    DBFILE      = 'dbfile'
    DEBUG       = 'debug'
    DIR         = 'dir'
    DIR_PROMPT  = 'dir-prompt'
    FILE        = 'file'
    FILE_FILTER = 'file-filter'
    FILE_PROMPT = 'file-prompt'
    FLAG        = 'flag'
    HEIGHT      = 'height'
    INCLUDE     = 'inc'
    MUSIC       = 'music'
    NOFRAME     = 'noframe'
    ONTOP       = 'ontop'
    OPTIONS     = 'options'
    OS          = 'os'
    PYTHON      = 'python'
    PYTHONRUN   = 'pythonrun'
    PREFIX      = 'prefix'
    QT          = 'qt'
    REQUIRE     = 'require'
    SCRIPT      = 'scriptdir'
    SCRIPTRUN   = 'scriptrun'
    SIMPLE      = 'simple'
    SYSTEM      = 'system'
    TITLE       = 'title'
    VARS        = 'vars'
    VERSION     = 'version'
    WIDTH       = 'width'

class UiScriptSetting():
    SEARCH_TAGS='\s*#:([a-z-]+)\s+([^\n\r]*)'
    SEARCH_KEYWORDS='\s*(\w+)\s*(\w+)\s*'
    def __init__(self, filename:str , lines=None , deep:bool=True):
        self._fname = filename
        self._dict  = { 
            ScriptKeys.DBFILE :   ['D'] , 
            ScriptKeys.DIR:       ['d'] , 
            ScriptKeys.DEBUG:     ['X'] ,
            ScriptKeys.FILE:      ['f'] , 
            ScriptKeys.MUSIC:     ['M'], 
            ScriptKeys.OS:        ['S'],
            ScriptKeys.PREFIX:    ['-'],
            ScriptKeys.PYTHON:    ['P'],
            ScriptKeys.PYTHONRUN: ['R'],
            ScriptKeys.QT:        ['Q'],
            ScriptKeys.SCRIPT:    ['Z'],
            ScriptKeys.SCRIPTRUN: ['Y'],
            ScriptKeys.VERSION:   ['v']}
        if lines is None:
            with open( filename ) as f: script = f.read()
            self.parse( script , deep)
        else:
            self.parse( lines , deep )

    def parseOptionLine( self, line:str ):
        matches = re.findall( UiScriptSetting.SEARCH_KEYWORDS , line )
        for match in matches:
            self.setFlag( match[0] , match[1] )
        if self.flag( 'prefix', 'dash') == 'dash' :
            self.setFlag( 'prefix' , '-')
        elif self.flag('prefix' ) == 'blank':
            self.setFlag( 'prefix' , '')

    def parseSettingLine( self , line:str):
        """ This parses lines made up of keyword keyword keyword"""
        settings = line.split()
        for setting in settings:
            self._dict[ setting ] = [ True ]

    def isOption( self, type:str , option  )->bool:
        """ Determine if 'option' is within the 'type' line. 
            Typically used for system or require options
        """
        return self.settingValue( type ).find( option ) > -1 

    def getOptions( self, key:str=ScriptKeys.VARS )->list:
        """ Return a list of options for a keyword. Can be used for system """
        return self.settingValue( key ).split()

    def include(self, filename ):
        pass

    def parse(self, lines, deep):
        """ Parse will Parse all the lines and create a key/list entry"""
        if isinstance( lines, list ):
            matches = re.findall(  UiScriptSetting.SEARCH_TAGS , "\n".join( lines ) )
        else:
            matches = re.findall(  UiScriptSetting.SEARCH_TAGS , lines  )
        if len( matches) > 0 :
            for match in matches:
                if match[0] in self._dict:
                    self._dict[ match[0] ].append( match[1].strip() )
                else:
                    self._dict[ match[0] ] = [ match[1].strip()]
            if ScriptKeys.FLAG in self._dict :
                for line in self._dict[ ScriptKeys.FLAG ]:
                    self.parseOptionLine( line )
            if deep:
                lines = self.setting( ScriptKeys.INCLUDE , [] )
                for line in lines :
                    print("Include file", line)

    def flag( self, key:str , default=None)->str:
        if self._dict is not None and key in self._dict :
            return self._dict[ key ][0]
        return default
    
    def setFlag( self, key, value )->None:
        self._dict[key] = [value.strip()]

    def isSet( self , key:str )->bool:
        """ Determine if 'key' is within the dictionary """
        return self._dict is not None and key in self._dict

    def setting( self, key:str , default=[] )->list:
        """ Return the list that is entered for the dictionary 'key' """
        if self.isSet( key ):
            return self._dict[ key ]
        if isinstance( default, list ):
            return default
        return [ default ]
    
    def settingValue( self, key:str , default='' )->str:
        return self.setting( key, default )[0]

    def settings(self)->dict:
        return self._dict
    
class RunScriptBase():
    """
    Contains the process functions for running shell scripts 
    
    ATTRIBUTES:
    ===========
    _process : QProcess
        Contains process object when script is running
    script_file : str
        full path to script to be run. Can be name of tempfile
    script_parms : UiScriptSetting object
        Created when script file is set. Use to pull parms from script
    _shell : str
        Contains shell program path for script execution
    process_state : QProcess.ProcessState
        Save the ProcessState when change is signalled
    _temp_file  : tempfile.NamedTemporaryFile
        Either None (no temp file) or temp file data for closure
    vars  : list
        List of parms to pass to shell script. For example: ['-D', '/where/is/dbfile' , '-X' ]

    OVERRIDES:
    ==========
    output_message( msgText:str , override=None)->None
        Output msgText to the user. Used during script execution
    notify_start( )->None
        Called when processing starts
    notify_end()->None
        Called when processing completes
    notify_script_change( script_file:str )->None
        When the script is changed, this is called. 
    addFinalVars()->None
        Derived class can add other parms to list (Prefer to end)
    """


    RETURN_CANCEL   =False
    RETURN_CONTINUE =True
    OUT_PLAIN =     'plain'
    OUT_STDOUT=     'stdout'
    OUT_NONE  =     'none'

    def __init__(self):
        """ Initialise all values used in program to None """
        self._process       = None
        self.script_file    = None
        self.script_parms   = None
        self._shell         = None
        self._process_state = None
        self._temp_file     = None

    def __del__(self):
        self._close_temporary_file()

    def output_message(self, msgText:str , override=None)->None:
        """ override - optional 
            Outputs messages to the user as the program runs
            All our message processing for output runs through here.
        """
        pass

    def notify_start( self ):
        """ override - optional 
            Call when the program is about to start
        """
        pass
 
    def notify_end( self ):
        """ override 
            Call when the program has completed
        """
        pass

    def notify_script_change( self, script_name:str )->None:
        ''' override '''
        pass

    def processStatus(self, msg ):
        ''' override '''
        pass

    def addFinalVars():
        """ override- optional Child class last chance to add more variables """

        pass

    def _close_temporary_file(self):
        if self._temp_file is not None:
            self._temp_file.close()
            self._temp_file = None

    def _create_temporary_file( self ):
        """ Generate a temporary file from the scriptText and set flag"""
        try:
            self._temp_file = tempfile.NamedTemporaryFile(mode="w+")
            self._temp_file.write( self._scriptText  )
            self._temp_file.flush()
            self.script_file = self._temp_file.name
            chmod( self.script_file , 0o550  )
        except Exception as err:
            QMessageBox.critical(None,
                "",
                "Error creating temporary file\n" + str(err), 
                QMessageBox.StandardButton.Cancel )
            self._close_temporary_file()
            return False
        return True

    def varFlag( self , tag:str )->str:
        return "{}{}".format( 
            self.script_parms.settingValue(ScriptKeys.PREFIX,'-'), 
            self.script_parms.settingValue(tag, tag) ) 
    
    def addVariableFlag(self, tag:str , front=False)->None:
        """ 
        Add just the tag to self.vars based on UiScriptSetting 

        For example, if you want 'debug' and call it as:
        addVariableFlag( ScriptKeys.DEBUG ) it will add ['-X']
        """
        if front:
            self.vars.insert( 0, self.varFlag( tag) )
        else:
            self.vars.append( self.varFlag( tag ))

    def addVariable( self, tag:str, value:str , front=False)->None:
        """
        Add the tag and value to the self.vars list based on UiScriptSetting values
        
        An example: if you want to have the script file added, you waould call it as
            addVariable( ScriptKeys.SCRIPT , self.script_file )
        and it would add:
            ['-Z' , '/script/file/path' ]
        """
        if front :
            self.vars.insert( 0 , value )
            self.addVariableFlag( 0, tag )
        else:
            self.vars.append(  self.varFlag( tag ))
            self.vars.append(  value )

    prefkeys = {
        'pdf-res':      [ 'E' , DbKeys.SETTING_FILE_RES ],
        'pdf-type':     [ 'I' , DbKeys.SETTING_FILE_TYPE ],
        'pdf-device':   [ 'G' , DbKeys.SETTING_DEFAULT_GSDEVICE ],
        'backup':       [ 'U' , DbKeys.SETTING_LAST_BACKUP ],             
    }
    def addSystemToVars(self):
        """ Add to vars list based on '#:system' tag in script file """
        if self.script_parms.isSet( ScriptKeys.SYSTEM):
            import platform
            import PySide6
            import sys
            sy = SystemPreferences()
            pref = DilPreferences()
            for key in self.script_parms.getOptions( ScriptKeys.SYSTEM) :
                if key in self.prefkeys:
                    flag=self.prefkeys[key][0]
                    val=pref.getValue( self.prefkeys[key][1] )
                    self.addVariable( flag , val )
                    continue

                if key ==ScriptKeys.DBFILE:
                    self.addVariable( key , pref.getPathDB() )

                if key == ScriptKeys.MUSIC :
                    self.addVariable( key , pref.getMusicDir() )

                if key == ScriptKeys.VERSION:
                    self.addVariable( key , ProgramConstants.version )

                if key == ScriptKeys.QT:
                    self.addVariable( key , PySide6.__version__)

                if key == ScriptKeys.PYTHON:
                    self.addVariable( key , platform.python_version() ),
                
                if key == ScriptKeys.PYTHONRUN:
                    self.addVariable( key , sys.executable )

                if key == ScriptKeys.OS:
                    self.addVariable( key , platform.platform( terse=True)) 

                if key == ScriptKeys.SCRIPTRUN:
                    self.addVariable( key , self._shell )

    def addDebugToVars(self, debug:bool=False ):
        if debug:
            self.addVariableFlag( ScriptKeys.DEBUG , front=False)

    def addScriptToVars( self ):
        """ Add script to the very first position in the variables being passed """
        self.vars.insert( 0 , self.script_file )

    def saveScript( self, script , isFile:bool=True )->bool:
        """ Save the script to file and setup script parameter class """
        self.script_file = script
        if isFile :
            if not path.isfile( script ):
                QMessageBox.critical(None,
                "",
                    "Script not found:\n" + script, 
                    QMessageBox.StandardButton.Cancel )
                return False
            with open( self.script_file ) as f: self._scriptText = f.read()

        self.script_parms = UiScriptSetting( self.script_file , self._scriptText , isFile )
        return True
  
    def setScript( self, script:str , vars:list=None, isFile:bool=True)->bool:
        """ 
        Save the script and notify child we changes script status
        
        This closes previous file, resets the variables passed to shell script
        and will notify the child class of the script change.
        """
        self._close_temporary_file()
        self.vars = vars if vars is not None else []
        if script is None or len(script) < 2:
            QMessageBox.critical(None,
                "",
                "Empty script passed", 
                QMessageBox.StandardButton.Cancel )
            return False
        
        self.saveScript( script , isFile )
        self.addSystemToVars()
        self.addVariable( ScriptKeys.SCRIPT , path.dirname( self.script_file ) )
        self.notify_script_change( ( script if isFile else None) )
        return True
    
    def reset(self):
        """ This clears the variables, resets the key ones from the script """
        self.vars = []
        self.addSystemToVars()
        self.addVariable( ScriptKeys.SCRIPT , path.dirname( self.script_file ) )

    def start_process(self):
        """
        start_process will setup and execute the shell script that is in the self._scriptfile.

        Only one process can run at a time. self_process hold the QProcess state.
        """

        if self._process is None:  # No process running.
            self._process= QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self._process.readyReadStandardOutput.connect(self._processStdout)
            self._process.readyReadStandardError.connect(self._processStderr)
            self._process.stateChanged.connect(self._processState)
            self._process.errorOccurred.connect(self._processError)
            self._process.finished.connect(self._processFinished)  # Clean up once complete.
            
            try:
                self.addScriptToVars()
                self.addFinalVars()
                self._process.start(self.shell(), self.vars)
            except Exception as err:
                self._close_temporary_file()
                raise err

    def getStatus(self):
        """
        Call this to get the current state of the process
        """
        if self._process_state is None:
            return QProcess.NotRunning
        return self._process_state

    def _processStderr(self)->None:
        data = self._process.readAllStandardError()
        stderrMsg = "ERROR: " + bytes(data).decode("utf8")
        self.output_message(stderrMsg)

    def _processStdout(self)->None:
        data = self._process.readAllStandardOutput()
        stdoutMsg = bytes(data).decode("utf8").strip()
        if stdoutMsg.__contains__('code>'):
            self.output_message( stdoutMsg, override='html')
        else:
            self.output_message(stdoutMsg)

    def _processState(self, state)->None:
        self._process_state = state
        if state == QProcess.Starting:
            self.timeStart = time.perf_counter()
        if state == QProcess.Running:
            self.notify_start()
    
    def _processFinished(self)->None:
        totalTime = time.perf_counter() - self.timeStart
        min, sec = divmod(totalTime, 60)
        hour, min = divmod(min, 60)
        self.notify_end( "Script done. Total time: {:2.0f}:{:02.0f}:{:02.0f}".format( hour, min, sec))
        self._close_temporary_file()
        self._process= None

    def _processError(self, error):
        """
        If a process error occurs then a popup message box will be shown
        """
        self._close_temporary_file()
        match error:
            case QProcess.FailedToStart:
                msg = "Program didn't start. Check script for errors."
            case QProcess.Crashed:
                msg = "Process crashed."
            case QProcess.Timedout:
                msg = "While waitFor calls, timeout"
            case QProcess.WriteError:
                msg = "While writing from script"
            case QProcess.ReadError:
                mesg = "While reading from script"
            case _:
                msg = "General script error"
                if isinstance( error , str ):
                    msg = "{}\n{}".format( msg , error )
                
        QMessageBox.critical(None,
            "",
             "Error running script\n" + msg, 
             QMessageBox.StandardButton.Cancel )
        
    def setShell(self, shellCommand )->bool:
        """ setShell sets the command to anything passed and returns true if there was a value"""
        self._shell = shellCommand
        return ( self._shell is not None and len(self._shell) > 0 )

    def setShellPref(self )->bool:
        """ SetShell will set the shell command from the system preferences setting"""
        self.pref = DilPreferences()
        self._shell = self.pref.getValue( DbKeys.SETTING_DEFAULT_SCRIPT , None )
        return ( self._shell is not None and len(self._shell)>0)
        
    def setSystemShell(self )->bool:
        """ setSystemShell willl (eventually) look at the system type and fill in how to 
            run the program. For now, it only works on UNIX systems that have a standard
            shell program (like /bin/bash)
        """
        shlist = ['/bin/bash', '/bin/zsh', '/bin/sh', '/usr/local/bin/bash', '/usr/local/bin/zsh', '/usr/local/bin']
        for i in range( 0 , len( shlist ) ):
            if path.exists( shlist[i] ):
                self.setShell( shlist[0])
                return True
        return False

    def shell(self)->str:
        """ shell will retrieve the shell setting from whatever we have set 
            If none has been set explicity, then get first the shell from preferences,
            then a shell from the system list
            IF none are found, 'None' is returend.
        """
        if self._shell is None:
            if not self.setShellPref() and not self.setSystemShell():
                self._shell = None
                QMessageBox.critical(None,
                "Runtime Error",
                "No shell program found to run script" , 
                QMessageBox.StandardButton.Cancel )
        return self._shell

class DialogSettings( ):
    """
        Set either the window title or create space in the area of the buttons 
    """

    def __init__(self):
        self._bottomText = None
        
    def generate( self , script_parms:UiScriptSetting, buttons:QDialogButtonBox ):
        if script_parms.isOption( ScriptKeys.REQUIRE, ScriptKeys.NOFRAME ):
            self._bottomWidget = QWidget()
            self._bottomText = QLineEdit()
            self._bottomText.setReadOnly( True )

            self._bottomLayout = QHBoxLayout()
            self._bottomLayout.addWidget( self._bottomText )
            self._bottomLayout.addWidget( buttons )
            self._bottomWidget.setLayout( self._bottomLayout )
            return self._bottomWidget
        return buttons
    
    def set( self, script_parms:UiScriptSetting, dlg:QDialog  ):
        """ set will set the title, frame setting, and the ontop hint."""
        title = script_parms.settingValue( ScriptKeys.TITLE , 'Script' )
        if self._bottomText is not None:
            self._bottomText.setText( title )
        else:
            dlg.setWindowTitle( title )

        dlg.setWindowFlag( Qt.FramelessWindowHint , script_parms.isOption( ScriptKeys.REQUIRE , ScriptKeys.NOFRAME ))
        if script_parms.isOption( ScriptKeys.REQUIRE , ScriptKeys.ONTOP ):
            dlg.setWindowFlag( Qt.WindowStaysOnTopHint, True)


class UiRunScript( RunScriptBase ):
    """
        Run a script based on values in the script file. This does not provide any prompting for files/dirs/etc.

        Tags that are used
        ==================
            #:comment multi-line comment displayed before execution
            #:require debug ontop noframe
            #:title   Script title for user
            #:width   int
            #:height  int

        Attributes (well, important ones)
        =================================
        btnDebug : QCheckBox
            Displayed if script '#:require' contains 'debug'
        text - QPlainTextEdit
            Set to read-only, contains output from program: title, comments, stdout and stderr
        textScriptName  : QLineEdit
            Set read-only, contains script name and final runtime status
        textScript : QPlainTextEdit
            Contains contents of script
        tabLayout : QTabWidget
            Contains two tabs: Output and Script. Double click Script to show runtime variables
        dlgW : int
            Width of dialog box
        dlgH : int
            Height of dialog box
        
        """

    def __init__(self, script:str, vars:list=None, isFile=True,outputDestination='plain') -> None:
        """
        Setup the runscript values

        script can be text of script to run or a file path.
        vars is  a aof options to pass as variables to script
        isFile : true when passed a filename rather than a script
        outputDestination must be a 'none', 'stdout' or 'plain'
        """
        super().__init__()
        self.debug_mode = False
        self.createTextFields()
        if self.setScript( script, vars, isFile=isFile ):
            width  = min( 2048, toInt( self.script_parms.settingValue(ScriptKeys.WIDTH , '600' ) ,600 ) )
            height = min( 1024, toInt( self.script_parms.settingValue(ScriptKeys.HEIGHT, '700' ) ,700 ) )
            self.setSize( width, height )
            self.setOutput( outputDestination )
            self.status = self.RETURN_CONTINUE
        else:
            self.status = self.RETURN_CANCEL

    def notify_start(self):
        """ Clear the general text field when process starts """
        self.text.clear()

    def notify_end(self, endMessage:str )->None:
        """ Write the end message on the text file line and move cursor to top of output """
        self.output_message("Script complete.")
        self.textScriptName.setText( endMessage  )
        self.text.moveCursor( QTextCursor.Start )

    def output_message(self, msgText:str , override=None)->None:
        """ output_message will output the current state to the text in output tab
        
        It can either output to a plain or regular text edit box
        If you sent 'stdout' it will print to the console instead.
        """
        use = self.use if override is None else override
        if use == 'plain':
            self.text.insertPlainText(msgText)
        elif use == 'text':
            self.text.appendPlainText(msgText)
        elif use == 'html':
            self.text.appendHtml( msgText )
        elif use == 'stdout':
            print( "Script: {}".format( msgText ))

    def notifyScriptTitleComment(self)->bool:
        """ If the script has #:title / #:comment entries, display in output box """
        if self.script_parms.isSet( ScriptKeys.TITLE ):
            title = self.script_parms.settingValue( ScriptKeys.TITLE )
            if len( title  ) > 0 :
                tl = len( title )
                self.output_message('<b>{}<br/>&nbsp;{}<br/>{}</b>'.format( 
                    '='*tl, title , '='*tl ), 'html')
        if self.script_parms.isSet( ScriptKeys.COMMENT ):
            self.output_message( "<br/><p>{}</p><br/>".format( 
                '<br/>'.join( self.script_parms.setting( ScriptKeys.COMMENT,'')) ), 
            'html')
        return True
        
    def notify_script_change( self, script_name:str )->None:
        self.textScript.setPlainText( self._scriptText )
        if script_name is not None :
            self.textScriptName.setText( 'File: {}'.format( script_name ) )
        else:
            self.textScriptName.setText( self.script_parms.settingValue( ScriptKeys.TITLE, 'Script passed by program') )
       
    def setOutput( self, outputDestination=None):
        self.use = 'stdout'
        if outputDestination in ['plain',  'text', 'none' ] :
            self.use = outputDestination
        
    def _getButtonList( self, btnBox:QDialogButtonBox ):
        btnList = {}
        for button in btnBox.buttons():
            btnList[ button.text() ] = button
        return btnList

    def _runButtons(self ):
        btnBox = QDialogButtonBox()
        btnBox.addButton( 'Execute', QDialogButtonBox.AcceptRole)
        btnBox.addButton( QDialogButtonBox.Close)
        btnBox.addButton( QDialogButtonBox.Cancel)
        btnList = self._getButtonList( btnBox )
        btnList['Close'].hide()
        return (btnBox,btnList)

    def _debugButton(self):
        """ Debug will be shown if there is a debug in the script, otherwise it will be hidden """
        self.btnDebug = QCheckBox('Debug')  # Added later to display
        self.btnDebug.setObjectName('Debug')
        self.btnDebug.setCheckable( True )
        self.btnDebug.setChecked( False )
        self.btnDebug.setHidden( not self.script_parms.isOption( ScriptKeys.REQUIRE , ScriptKeys.DEBUG ) )
        return self.btnDebug

    def _runTabLayout(self):
        tabLayout = QTabWidget()
        vlayout = QVBoxLayout()
        vlayout.addWidget( self.textScriptName )
        vlayout.addWidget( self._debugButton() )
        vlayout.addWidget( self.text )
        w = QWidget()
        w.setLayout( vlayout )
        tabLayout.addTab( w ,"Output")
        tabLayout.setTabText( 0 , "Output")

        tabLayout.addTab(self.textScript, "Script")
        tabLayout.setTabText(1 , "Script")
        
        return tabLayout

    def createTextFields(self):
        plainFont = QFont()
        plainFont.setFixedPitch( True )
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.textScriptName = QLineEdit()
        self.textScriptName.setReadOnly( True )

        self.textScript = QPlainTextEdit()
        self.textScript.setFont( plainFont )
    
    def actionSingleClickTab( self, index )->None:
        if index != 1 and self.tabLayout.tabText(1) != 'Script':
            self.actionDoubleClickTab( 1 )

    def actionDoubleClickTab( self, index )->None:
        """ If the user double clicks on the script tab, it will show script parameters """
        if index == 1:
            if self.tabLayout.tabText(index) == 'Script':
                self._script_save = self.textScript.toPlainText()
                self.tabLayout.setTabText(index, 'Runtime')
                self.textScript.clear()
                self.textScript.insertPlainText("Shell command: {}\n".format( self.shell() ) )
                self.textScript.insertPlainText("Script file: {}\n\n".format(self.script_file ))
                self.textScript.insertPlainText("Variables passed to shell by position:\n")
                for i in range( 0, len( self.vars ) ):
                    self.textScript.insertPlainText("   {}: '{}'\n".format( i+1 , self.vars[i]))
            else:
                self.tabLayout.setTabText(index, 'Script')
                self.textScript.setPlainText( self._script_save )
                del self._script_save

    def isDebug( self )->bool:
        return self.debug_mode
    
    def run(self, startMsg:str="Hit Execute button to run program" )->bool:
        """
        run is the interface between the dialog box displaying information and the
        actual process that will be executed.

        It returns True to continue, False to Cancel
        """

        def buttonClicked(button):
            match button.text().strip():
                case 'Execute':
                    self.status = self.RETURN_CONTINUE
                    btnList['Execute'].setDisabled(True)
                    self.debug_mode = self.btnDebug.isChecked()
                    self.addDebugToVars( self.debug_mode  )
                    self.text.clear()
                    self.output_message("Starting program<br/>{}<br/>".format( "-"*50),'html')
                    self.start_process()
                    btnList['Close'].show()
                    btnList['Cancel'].hide()
                    # don't close dialog box!
                case 'Cancel':
                    self.status = self.RETURN_CANCEL
                    btnList['Execute'].setEnabled(True)
                    dlgRun.reject()     
                case _:
                    self.status = self.RETURN_CONTINUE
                    dlgRun.accept()

        if self.status == self.RETURN_CONTINUE:
            self.tabLayout = self._runTabLayout()
            self.tabLayout.tabBarDoubleClicked.connect( self.actionDoubleClickTab )
            self.tabLayout.tabBarClicked.connect( self.actionSingleClickTab )
            (btnBox, btnList ) = self._runButtons()
            btnBox.clicked.connect( buttonClicked)
    
            self.titler = DialogSettings()
            runLayout = QVBoxLayout()
            runLayout.addWidget(self.tabLayout)
            runLayout.addWidget( self.titler.generate( self.script_parms, btnBox ) )

            dlgRun = QDialog()
            dlgRun.setLayout(runLayout)
            dlgRun.setMinimumHeight(500)
            dlgRun.setMinimumWidth(500)
            self.titler.set( self.script_parms , dlgRun )
            dlgRun.resize( self.dlgW , self.dlgH )
            self.notifyScriptTitleComment()
            self.output_message( startMsg  )
            dlgRun.exec()
        
        return self.status

    def setSize( self , w:int, h:int )->None:
        self.dlgW = w
        self.dlgH = h

class UiRunScriptFile( UiRunScript ):
    """
    Run a script that may require a filename / Directory

    Tags that are used (in addtion to UiRunScript)
    ==============================================
        #:file-prompt  message
        #:file-filter ( type, type )
        #:dir-prompt   message
        #:require      file dir noframe ontop
    
    if file or directory are required, the tag
        #:require
    should contain the required values: file dir
    If no require, the files are considered optional
    """

    def __init__(self, script: str, vars:list=None, isFile:bool=True, outputDestination='plain') -> None:
        super().__init__(script, vars, isFile, outputDestination)
        
        if self.status:
            self.createFloatWindow()
            self.promptFileDir(  )
            self.floatHide()

    def __del__(self):
        if ProgramConstants.ismacos and hasattr( self, '_floatText'):
            del self._floatText
        super().__del__()

    def createFloatWindow(self):
        if ProgramConstants.ismacos:
            self._floatText = QPlainTextEdit()
            self._floatText.setWindowFlag( Qt.FramelessWindowHint , True)
            self._floatText.setWindowFlag( Qt.WindowStaysOnTopHint, True)
            self._floatText.setPlainText("")
            self._floatText.setGeometry( 10,10,200,75 )

    def floatText( self, txt:str )->None:
        if ProgramConstants.ismacos:
            self._floatText.setPlainText( txt )
            self._floatText.show()

    def floatHide(self)->None:
        if ProgramConstants.ismacos:
            self._floatText.hide()

    def requiredFieldError(self, msg:str)->bool:
        """ Prompt with an error giving them another chance
            unless the dialog box is gone
        """
        title = self.script_parms.settingValue( ScriptKeys.TITLE )

        self.status = QMessageBox.question(None,
            "Tool Script",
              "Script '{}'\n{}".format( title, msg ),
             QMessageBox.Retry, QMessageBox.Cancel )
        self.status = self.status == QMessageBox.Retry 
        return self.status

    def promptFileDir(self):
        while ( not self.promptFile() ):
            if not self.requiredFieldError( 'File is required.'):
                return

        while ( not self.promptDir() ):
            if not self.requiredFieldError( 'Directory is required.'):
                return

        return self.status


    def promptFile( self )->bool:
        prompt = self.script_parms.settingValue( ScriptKeys.FILE_PROMPT, '')
        filter = self.script_parms.settingValue( ScriptKeys.FILE_FILTER, '')
        required = self.script_parms.isOption( ScriptKeys.REQUIRE, 'file')

        if prompt == '':
            return not required

        dlg = QFileDialog(caption=prompt, filter=filter)
        dlg.setFileMode( QFileDialog.ExistingFile )
        self.floatText( prompt )
        if dlg.exec() :
            filenames = dlg.selectedFiles()
            if len( filenames ) > 0 :
                filename = filenames[0]
                if not path.isfile( filename ):
                    return not required
                self.output_message( "{}: {}".format( prompt, filename ) )
                self.addVariable( ScriptKeys.FILE , filename , front=False)
                return True
        self.output_message( "{}: (none)".format( prompt) )
        return not required

    def promptDir( self )->bool:
        prompt = self.script_parms.settingValue( ScriptKeys.DIR_PROMPT, '')
        required = self.script_parms.isOption( ScriptKeys.REQUIRE, 'dir')

        if prompt == '':
            return not required

        self.floatText( prompt )
        newDirName = QFileDialog.getExistingDirectory(None, prompt )
            
        if newDirName :
            if not path.isdir( newDirName ):
                return not required
            self.output_message( "{}: {}".format( prompt, newDirName) )
            self.addVariable( ScriptKeys.DIR , newDirName, front=False)
            return True
        self.output_message( "{}: (none)".format( prompt) )
        return not required

class UiRunSimpleNote( RunScriptBase ):
    """
    Display a simple plain text message to the user, run the script and only show a close button.
    
    Tags that are used:
    ==============================================
        #:require   file dir noframe ontop
        #:title     name to display to user
        #:width     n
        #:height    n

    """
    def __init__(self, script:str, vars:list=None, isFile=True,outputDestination='plain') -> None:
        """
        Setup the runscript values

        script can be text of script to run or a file path.
        vars is  a aof options to pass as variables to script
        isFile : true when passed a filename rather than a script
        outputDestination must be a 'none', 'stdout' or 'plain'
        """
        super().__init__()


        if self.setScript( script, vars, isFile=isFile ):
            width  = min( 2048, toInt( self.script_parms.settingValue(ScriptKeys.WIDTH , '600' ) ,600 ) )
            height = min( 1024, toInt( self.script_parms.settingValue(ScriptKeys.HEIGHT, '700' ) ,700 ) )
            self.setSize( width, height )
            self.setOutput( outputDestination )
            self.createOutputFields()
            self.status = self.RETURN_CONTINUE
        else:
            self.status = self.RETURN_CANCEL

 
    def notify_start(self):
        """ Clear the general text field when process starts """
        self.text.clear()

    def notify_end(self, endMessage:str )->None:
        """ Move cursor to top of output """
        self.output_message("Script complete.")
        self.text.moveCursor( QTextCursor.Start )

    def output_message(self, msgText:str , override=None)->None:
        """ output_message will output the current state to the text in output tab
        
        It can either output to a plain or regular text edit box
        If you sent 'stdout' it will print to the console instead.
        """
        use = self.use if override is None else override
        if use == 'plain':
            self.text.insertPlainText(msgText)
        elif use == 'text':
            self.text.appendPlainText(msgText)
        elif use == 'html':
            self.text.appendHtml( msgText )
        elif use == 'stdout':
            print( "Script: {}".format( msgText ))
   
    def setOutput( self, outputDestination=None):
        self.use = 'stdout'
        if outputDestination in ['plain',  'text', 'none' ] :
            self.use = outputDestination

    def createOutputFields(self)->bool:
        self.titler = DialogSettings()
        plainFont = QFont()
        plainFont.setFixedPitch( True )
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont( plainFont )

        self.btnBox = QDialogButtonBox()
        self.btnBox.addButton( QDialogButtonBox.Close)

        self.layout = QVBoxLayout()
        self.layout.addWidget( self.text )
        self.layout.addWidget( self.titler.generate( self.script_parms, self.btnBox ) )

        return True


    def run(self, startMsg:str="Hit Execute button to run program" )->bool:
        """
        run is the interface between the dialog box displaying information and the
        actual process that will be executed.

        It returns True to continue, False to Cancel
        """
        def buttonClicked(button):
            self.status = self.RETURN_CONTINUE
            dlgRun.accept()

        self.btnBox.clicked.connect( buttonClicked)
        if self.status == self.RETURN_CONTINUE:

            dlgRun = QDialog()
            dlgRun.setLayout(self.layout )
            dlgRun.setMinimumHeight(500)
            dlgRun.setMinimumWidth(500)
            dlgRun.resize( self.dlgW , self.dlgH )
            self.titler.set( self.script_parms , dlgRun )
            self.text.clear()
            self.output_message("Starting program<br/>{}<br/>".format( "-"*50),'html')
            self.start_process()

            dlgRun.exec()

        return self.status

    def setSize( self , w:int, h:int )->None:
        self.dlgW = w
        self.dlgH = h