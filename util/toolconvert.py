# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from fileinput import filename
from os import path, chmod
import tempfile
import sys
import re
import time
import os
from pathlib import PurePath
from functools import singledispatchmethod
from musicsettings import MusicSettings, MSet
from PySide6.QtWidgets import (
        QApplication, QFileDialog, 
        QDialog, QVBoxLayout, QMessageBox,
        QPlainTextEdit, QDialog,QTabWidget, QDialog,
        QLabel, QDialogButtonBox , QCheckBox, QLineEdit )
from PySide6.QtCore import QProcess


class ToolConvert():
    _script = 'convert-pdf.smc'
    
    def _scriptPath( self, file ):
        if file is None:
            return path.expanduser(
                path.join(
                    self.path, 
                    self._script
                )
            )
        return path.expanduser( file )

    @singledispatchmethod
    def setPath(self, value ):
        raise NotImplementedError(f"Cannot set path from type {type(arg)}")

    @setPath.register
    def _( self, settings: MusicSettings ):
        self.path = settings.value( MSet.byDefault( MSet.SETTING_DEFAULT_PATH))
    
    @setPath.register
    def _( self, path:str):
        self.path = path

    def default(self):
        return self._defaultPdfCmd

    def scriptExists( self, file:str=None )->bool:
        return path.exists( self._scriptPath( file ) )

    def readRaw(self, file:str=None, default:bool=True) -> str:
        file = self._scriptPath( file )
        if not path.exists( file ):
            if default :
                return self._defaultPdfCmd
            else:
                return ""
        with open(self._scriptPath(file), 'r') as scriptFile:
            return scriptFile.read()

    def readExpanded( self, settings:MusicSettings, sourceFile:str, file=None, name=None, debug=False, default=True):
        """ Read and expand the conversion template
        
        settings: the preferences settings
        sourceFile: the PDF filename
        name: The name you want to output to be called
        debug: the debug flag. True to make this file not really be run.
        
        """
        script = self.readRaw( file, default)
        return self.expandScript( settings, script, sourceFile, name, debug=debug )

    def writeRaw( self, script, file=None ):
        file = self._scriptPath( file )
        with open(file, 'w') as scriptFile:
            scriptFile.writelines(script)

    def expandScript( self, settings:MusicSettings, script:str, sourceFile:str, name=None, debug=False ):
        """ expand the conversion template passed to us
        
        settings: the preferences settings
        script: the template script
        sourceFile: the PDF filename
        name: The name you want to output to be called
        debug: the debug flag. True to make this file not really be run.

        """
        #   {{source}}   Location of PDF to convert
        #   {{target}}   File Setting ; Default Directory
        #   {{name}}     Name for book. Prompted when run
        #   {{type}}     File Setting ; Filetype
        #   {{device}}   GS setting for 'Filetype'
        #                for PNG this should be 'png16m'
        #   {{debug}}    Set to 'echo' if debug is True
        script = script.strip()
        sourceFile = sourceFile.strip()

        if script != "" and sourceFile != "":
            debugReplace = ""
            if debug:
                debugReplace = "echo "
            if name is None or not name:
                nameReplace = PurePath( sourceFile).stem
            else:
                nameReplace = name
            if debug:
                debugState = '(Running in Debug mode)'
            else:
                debugState = ''
            script = script.replace("{{debug}}" , debugReplace)
            script = script.replace("{{debug-state}}", debugState )
            script = script.replace("{{device}}", settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_GSDEVICE),"png16m")   )  
            script = script.replace("{{name}}"  , nameReplace)
            script = script.replace("{{source}}", sourceFile )
            script = script.replace("{{target}}", settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_PATH), MSet.VALUE_DEFAULT_DIR) )
            script = script.replace("{{type}}"  , settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_TYPE),"png") )
            self.bookPath = os.path.join( 
                settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_PATH), MSet.VALUE_DEFAULT_DIR) ,
                nameReplace 
            )
        return script
    
    _defaultPdfCmd='''#!/bin/bash
#
# Conversion script from PDF to pages
# version 0.1
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

EndScript()
{
    echo "Conversion ending."
}

########################################################
# Command to run
# This command uses GHOSTSCRIPT, which is a free utility
########################################################
echo \"Conversion starting {{debug-state}}\"
echo \"Source file is {{source}}\"
echo .
{{debug}}cd       '{{target}}'  || exit 1
{{debug}}mkdir -p '{{name}}'    || exit 2
echo Input is \"{{source}}\"

{{debug}}gs -dSAFER -dBATCH -dNOPAUSE -r300 -dDeskew -sDEVICE="{{device}}" -sOutputFile="{{name}}/page-%03d.{{type}}" "{{source}}"  || exit 3

'''

class UiConvert():
    # The following codes are used for 'self.status' to expand on 
    # signals from dialogs.
    RETURN_CANCEL=0
    RETURN_CONTINUE=1
    RETURN_SKIP=2

    def __init__(self, settings:MusicSettings)->None:
        if not isinstance(settings, MusicSettings):
            sys.exit("Invalid call to RunConvert. Now settings passed.")
        self.settings = settings
        self.status  = False
        self._process = None
        self.rawScript = ""
        self.script = ""
        self.debugFlag = False

    def getScript(self, inputFile: str, outputName: str, debugFlag=False) -> str:
        toolConvert = ToolConvert()
        toolConvert.setPath(self.settings)
        if not self.rawScript:
            if not toolConvert.scriptExists():
                rtn = QMessageBox.question(
                    None,
                    "",
                    "No script found.\nDo you want to use default script template?",
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.No)
                if rtn == QMessageBox.No:
                    return None
            self.rawScript = toolConvert.readRaw(default=True)

        self.script = toolConvert.expandScript(
            self.settings, self.rawScript, inputFile, outputName, debug=debugFlag)
        self.bookPath = toolConvert.bookPath
        del toolConvert
        return self.script

    def getPDF(self)->str:
        self.fileName,filter = QFileDialog.getOpenFileNames(
            None,
            "Select PDF File",
            dir=path.expanduser('~'),
            filter="(*.pdf *.PDF)",
        )
        
        return self.fileName

    def getOutputName(self, filename:str, showSkipButton:bool=False):
        badMatch = re.compile( '[^ \-\w]')
        def buttonClicked( button ):
            txt = button.text().strip()
            if txt == 'Cancel':
                txtOutput.setText("")
                self.status = self.RETURN_CANCEL
                dlg.reject()
            elif txt == 'Skip':
                self.status = self.RETURN_SKIP
                dlg.reject()
            else: # continue
                self.status = self.RETURN_CONTINUE
                dlg.accept()
        
        def textChanged(txt:str):
            err = ""
            if txt.startswith('../'):
                err = "Name cannot start with a period '../'"
            elif "../" in txt :
                err = "Name cannont contain ../"
            elif txt.endswith('.'):
                err = "Name cannot end with a period"
            else:
                if badMatch.search(txt):
                    err = "Name can only contain letters, numbers, blanks, '-' and '_'"
            if err != "":
                txtError.setText( "<h3>{}</h3>".format(err) )
                btnList['Ok'].setDisabled(True)
            else:
                txtError.clear()
                btnList['Ok'].setDisabled( False )


        btnBox = QDialogButtonBox()
        btnBox.addButton( u'Skip', QDialogButtonBox.ActionRole)
        btnBox.addButton( QDialogButtonBox.Cancel)
        btnBox.addButton( QDialogButtonBox.Ok )
        btnBox.clicked.connect(buttonClicked )
        btnList = self._getButtonList( btnBox )
        if not showSkipButton :
            btnList['Skip'].hide()

        self.lblOutputName = QLabel("Bookname for {}".format( path.basename(filename)) )

        self.outputName = PurePath( filename ).stem
        txtOutput = QLineEdit()
        txtOutput.setText( self.outputName)
        txtOutput.textChanged.connect(textChanged)
        txtOutput.setMinimumWidth(50)
        txtOutput.setMaxLength(127)

        txtError = QLabel()

        self.checkDebug = QCheckBox()
        self.checkDebug.setText("Run in debug mode")
        self.checkDebug.setCheckable(True)
        self.checkDebug.setChecked(self.debugFlag) # this will persist


        dlg = QDialog()
        dlg.setWindowTitle("Output Bookname")
        dlg.setMinimumWidth(500)
        dlg.setMinimumHeight( 250 )
        
        dlgLayout = QVBoxLayout()
        dlgLayout.addWidget( self.lblOutputName )
        dlgLayout.addWidget( txtOutput )
        dlgLayout.addWidget( txtError )
        dlgLayout.addWidget( self.checkDebug )
        dlgLayout.addWidget( btnBox )

        dlg.setLayout( dlgLayout )
        dlg.exec()
        if self.status == self.RETURN_CONTINUE :   
            self.outputName = txtOutput.text().strip()
            self.debugFlag = self.checkDebug.isChecked()
        return self.status

    def exec_(self)->bool:
        fileList = self.getPDF()
        showSkipButton = ( len(fileList) > 1 )
        for self.fileName in fileList:
            self.getOutputName(self.fileName, showSkipButton)
            if self.status == self.RETURN_CANCEL:
                break
            if  self.status == self.RETURN_CONTINUE :
                self._run( self.getScript( self.fileName, self.outputName, self.debugFlag ) )
        return self.status
    
    def _processMessage(self, msgText:str)->None:
        self.text.appendPlainText(msgText)

    def _processStderr(self)->None:
        data = self._process.readAllStandardError()
        msg = bytes(data).decode("utf8")
        self._processMessage(msg)

    def _processStdout(self)->None:
        data = self._process.readAllStandardOutput()
        msg = bytes(data).decode("utf8")
        self._processMessage(msg)

    def _processState(self, state)->None:
        if state == QProcess.Starting:
            self.timeStart = time.perf_counter()
        if state == QProcess.Running:
            self._processMessage("Running script\n{}".format( "=" * 40))

    def _processFinished(self)->None:
        totalTime = time.perf_counter() - self.timeStart
        min, sec = divmod(totalTime, 60)
        hour, min = divmod(min, 60)
        self._processMessage("{}\nScript done. Total time: {:2.0f}:{:02.0f}:{:02.0f}".format("="*40, hour, min, sec) )
        self._process= None
        self.scriptFile.close()
        del self.scriptFile

    def _processError(self, error)->None:
        self.scriptFile.close()
        del self.scriptFile
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

        QMessageBox.critical(None,
            "",
             "Error running script\n" + msg, 
             QMessageBox.StandardButton.Cancel )


    def _getButtonList( self, btnBox:QDialogButtonBox ):
        btnList = {}
        for button in btnBox.buttons():
            btnList[ button.text() ] = button
        return btnList

    def _runButtons(self ):
        btnBox = QDialogButtonBox()
        btnBox.addButton( "Execute", QDialogButtonBox.AcceptRole)
        btnBox.addButton( QDialogButtonBox.Close)
        btnBox.addButton( QDialogButtonBox.Cancel)
        btnList = self._getButtonList( btnBox )
        btnList['Close'].hide()
        return (btnBox,btnList)
    
    def _runTabLayout(self):
        tabLayout = QTabWidget()

        tabLayout.addTab(self.text,"Output")
        tabLayout.setTabText( 0 , "Output")

        tabLayout.addTab(self.textScript, "Script")
        tabLayout.setTabText(1 , "Script")
        return tabLayout

    def _run(self, script ):
        """
        _run is the interface between the dialog box displaying information and the
        actual process that will be executed.
        """
        def buttonClicked(button):
            match button.text().strip():
                case 'Execute':
                    self.status = self.RETURN_CONTINUE
                    self.start_process()
                    btnList['Close'].show()
                    btnList['Cancel'].hide()
                    # don't close dialog box!
                case 'Cancel':
                    self.status = self.RETURN_CANCEL
                    dlgRun.reject()     
                case _:
                    self.status = self.RETURN_CONTINUE
                    dlgRun.accept()

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.textScript = QPlainTextEdit()
        self.textScript.setPlainText( script)

        tabLayout = self._runTabLayout()
        (btnBox, btnList ) = self._runButtons()
        btnBox.clicked.connect( buttonClicked)
    
        runLayout = QVBoxLayout()
        runLayout.addWidget(tabLayout)
        runLayout.addWidget(btnBox)

        dlgRun = QDialog()
        dlgRun.setLayout(runLayout)
        dlgRun.setMinimumHeight(500)
        dlgRun.setMinimumWidth(500)
        dlgRun.exec()
        return self.status

    def start_process(self):
        """
        start_process will setup and execute the shell script that is in the 'script' text box.

        This will let the user make modifications before it is run.
        """
        if self._process is None:  # No process running.
            self._process= QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self._process.readyReadStandardOutput.connect(self._processStdout)
            self._process.readyReadStandardError.connect(self._processStderr)
            self._process.stateChanged.connect(self._processState)
            self._process.errorOccurred.connect(self._processError)
            self._process.finished.connect(self._processFinished)  # Clean up once complete.
            
            ## write script to temporary file
            script = self.textScript.toPlainText().strip()
            self.scriptFile = tempfile.NamedTemporaryFile(mode="w+")
            try:
                shell = self.settings.value( 
                    MSet.byDefault( MSet.SETTING_DEFAULT_SCRIPT), 
                    MSet.VALUE_DEFAULT_SCRIPT)
                vars = MSet.scriptVarSplit( 
                    self.settings.value( 
                        MSet.byDefault( MSet.SETTING_DEFAULT_SCRIPT_VAR), 
                        MSet.VALUE_DEFAULT_SCRIPT_VAR) , 
                    self.scriptFile.name 
                )
                self.scriptFile.write( script  )
                self.scriptFile.flush()
                chmod( self.scriptFile.name , 0o550  )
                self._process.start(shell, vars)
            except Exception as err:
                self.scriptFile.close()

        
if __name__ == "__main__":
    app = QApplication()
    converter = UiConvert( MusicSettings())
    converter.exec_()
    app.quit()
    sys.exit(0)
