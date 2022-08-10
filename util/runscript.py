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

from os import chmod
import tempfile
import time

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication, 
    QMessageBox)

class UiRunScript():
    def __init__(self, script:str, vars:list=None, outputDestination=None) -> None:
        """
            Script must be plain text
            vars must be a list of options to pass to the script
            outputDestination must be a text output where messages will be sent or None

            if outputDestination is 'None' then no output will be shown
            if outputDestination is 'stdout', it will use simple print statements to console

        """
        self._process = None
        self.state = None
        self.setScript( script, vars )
        self.setOutput( outputDestination )
        

    def setScript( self, script:str , vars:list=None)->bool:
        self.script = script
        if vars is None:
            vars = []
        else:
            self.vars = vars
        return not( self.script is None or self.script.isspace() )

    def setOutput( self, outputDestination=None):
        self.use = None
        if not outputDestination is None:
            if outputDestination == 'stdout':
                self.use = 'stdout'
            else:
                self.text = outputDestination
                if hasattr( self.text , 'appendPlainText') and callable(getattr( self.text , 'appendPlainText') ):
                    self.use = 'plain'
                elif hasattr( self.text , 'appendText') and callable(getattr( self.text , 'appendText') ):
                    self.use = 'text'

    def start_process(self):
        """
        start_process will setup and execute the shell script that is in the 'script' text box.

        This will let the user make modifications before it is run.
        """
        if self.script is None or not self.script and self.script.isspace() :
            raise Exception("No script was provided")
        if self._process is None:  # No process running.
            self._process= QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self._process.readyReadStandardOutput.connect(self._processStdout)
            self._process.readyReadStandardError.connect(self._processStderr)
            self._process.stateChanged.connect(self._processState)
            self._process.errorOccurred.connect(self._processError)
            self._process.finished.connect(self._processFinished)  # Clean up once complete.
            
            ## write script to temporary file
            self.scriptFile = tempfile.NamedTemporaryFile(mode="w+")
            try:
                self.vars.append( self.scriptFile.name )
                self.scriptFile.write( self.script  )
                self.scriptFile.flush()
                chmod( self.scriptFile.name , 0o550  )
                self._processMessage(self.shell, self.vars )
                self._process.start(self.shell, self.vars)
            except Exception as err:
                self.scriptFile.close()
                raise err

    def getStatus(self):
        """
        Call this to get the current state of the process
        """
        if self.state is None:
            return QProcess.NotRunning
        return self.state

    def _processStderr(self)->None:
        data = self._process.readAllStandardError()
        stderr = "ERROR: " + bytes(data).decode("utf8")
        self._processMessage(stderr)

    def _processStdout(self)->None:
        data = self._process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self._processMessage(stdout)

    def _processState(self, state)->None:
        self.state = state
        if state == QProcess.Starting:
            self.timeStart = time.perf_counter()
        if state == QProcess.Running:
            self._processMessage("Running script\n{}".format( "=" * 40))

    def _processFinished(self)->None:
        totalTime = time.perf_counter() - self.timeStart
        min, sec = divmod(totalTime, 60)
        hour, min = divmod(min, 60)
        self._processMessage("{}\nScript done. Total time: {:2.0f}:{:02.0f}:{:02.0f}".format("="*40, hour, min, sec) )
        self.scriptFile.close()
        del self.scriptFile
        self._process= None

    def _processError(self, error):
        """
        If a process error occurs then a popup message box will be shown
        """
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

    def _processMessage(self, msgText:str)->None:
        """ processMessage will output the current state to a text box
        
            It can either output to a plain or regular text edit box
            If you sent 'stdout' it will print to the console instead.
        """
        if self.use == 'plain':
            self.text.appendPlainText(msgText)
        if self.use == 'text':
            self.text.appendText(msgText)
        if self.use == 'stdout':
            print( "Script: {}".format( msgText ))

    

