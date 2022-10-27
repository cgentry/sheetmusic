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

#
# ToolConvert contains routines that take PDF files and convert to
# scripts. It relies on conversion program (ghostscript) to do the
# conversion. A GUI is written that allows full display and status
# of the process.

from fileinput import filename
from os import path, chmod
from pathlib import PurePath
import fnmatch
import os
import re
import shutil
import sys
import tempfile
import time

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
        QApplication,       QDialog, 
        QDialogButtonBox ,  QFileDialog,
        QMessageBox,        QPlainTextEdit, 
        QTabWidget,         QVBoxLayout
    )

from qdb.dbbook       import DbBook
from qdb.keys         import BOOK, DbKeys, ImportNameSetting
from qdil.preferences import DilPreferences

class ToolConvert():
    _script = 'convert-pdf.smc'
    
    def __init__(self):
        self.pref = DilPreferences()
        self.path = self.pref.getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC )

    def _scriptPath( self, file ):
        if file is None:
            return path.expanduser(
                path.join(
                    self.path, 
                    self._script
                )
            )
        return path.expanduser( file )

    def setPath( self, path:str):
        self.path = path

    def default(self):
        return self.readRaw()

    def scriptExists( self, file:str=None )->bool:
        return path.exists( self._scriptPath( file ) )

    def readRaw(self, file:str=None ) -> str:
        """
            Read and return the raw script from the database
        """
        return self.pref.getValue( DbKeys.SETTING_PDF_SCRIPT )
        
    def readExpanded( self, sourceFile:str, file=None, name=None, debug=False):
        """ Read and expand the conversion template
        
        sourceFile: the PDF filename
        name: The name you want to output to be called
        debug: the debug flag. True to make this file not really be run.
        
        """
        return self.expandScript(  self.readRaw( file ), sourceFile, name, debug=debug )

    def writeRaw( self, script, file=None ):
        file = self._scriptPath( file )
        with open(file, 'w') as scriptFile:
            scriptFile.writelines(script)

    def expandScript( self, script:str, sourceFile:str, name=None, debug=False )->str:
        """ 
        expand the conversion template passed to us
        
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
            debugState = ""
            if debug:
                debugReplace = "echo "
                debugState = '(Running in Debug mode)'
            if name is None or not name:
                name = PurePath( sourceFile).stem
            script = script.replace("{{debug}}" , debugReplace)
            script = script.replace("{{debug-state}}", debugState )
            script = script.replace("{{device}}", self.pref.getValue(DbKeys.SETTING_DEFAULT_GSDEVICE,"png16m") )
            script = script.replace("{{name}}"  , name)
            script = script.replace("{{source}}", sourceFile )
            script = script.replace("{{target}}", self.pref.getValue(DbKeys.SETTING_DEFAULT_PATH_MUSIC, DbKeys.VALUE_DEFAULT_DIR) ) 
            script = script.replace("{{type}}"  , self.pref.getValue(DbKeys.SETTING_FILE_TYPE, DbKeys.VALUE_FILE_TYPE) )
            self.bookPath = os.path.join( 
                self.pref.getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC ),
                name 
            )
        return script
    
class UiBaseConvert():
    """
        UiBaseConvert contains code to process a list of PDF files and store them
        in the sheetmusic directory. Directory prompts should occur in the derived classes
    """
    # The following are only used to give labels to our return status
    RETURN_CANCEL=False
    RETURN_CONTINUE=True


    def __init__(self)->None:
        self.pref = DilPreferences()
        self.status  = self.RETURN_CANCEL
        self._process = None
        self.rawScript = ""
        self.script = ""
        self.debugFlag = False
        self.bookType = self.pref.getValue(DbKeys.SETTING_FILE_TYPE, DbKeys.VALUE_FILE_TYPE)
        self.baseDir = '~'
        self.data = []
        self.duplicateList = []

    def setBaseDirectory(self, dir:str):
        if dir is not None:
            self.baseDir = dir

    def baseDirectory(self)->str:
        return ( self.baseDir if self.baseDir else DbKeys.VALUE_LAST_IMPORT_DIR )

    def getScript(self, inputFile: str, outputName: str, debugFlag=False) -> str:
        toolConvert = ToolConvert()
        ##toolConvert.setPath(self.settings)
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
            self.rawScript = toolConvert.readRaw()

        self.script = toolConvert.expandScript(
            self.rawScript, inputFile, outputName, debug=debugFlag)
        self.bookPath = toolConvert.bookPath
        del toolConvert
        return self.script

    def isBookDirectory( self, bookDir:str )->bool:
        """
            Pass a directory and a type for the books.
        """
        pages = len(fnmatch.filter(os.listdir(bookDir), '*.' + self.page_suffix))
        return pages > 0   

    def _cleanupName(self, bookName:str, level:int )->str:
        ## first ALWAYS replace invalid characters
        bookName = re.sub(r'[\n\t\r]+', '', bookName )          # No newline, returns or tabs
        bookName = re.sub(r'[#%{}<>*?$!\'":@+\\|=/]+', ' ' , bookName)      ## bad characters
        bookName = re.sub(r'\s+',       ' ' , bookName)         ## Only one space when multiples
        bookName = re.sub(r'^[^a-zA-Z\d]+', '' , bookName)      ## Leading char must be Alphanumeric
        
        if level == DbKeys.VALUE_NAME_IMPORT_FILE_1:
            bookName = re.sub( r'[_]*', ' ', bookName )
        if level == DbKeys.VALUE_NAME_IMPORT_FILE_2:
            bookName = re.sub( r'[_]*', ' ', bookName )
            bookName = bookName.title()

        return bookName.strip()
    
    def _getInfoPDF(self, sourceFile , default:int=1):
        endPage = default
        bookName = PurePath( sourceFile ).stem
        importNameSetting = ImportNameSetting()
        cleanupLevel = self.pref.getValueInt( DbKeys.SETTING_NAME_IMPORT, DbKeys.VALUE_NAME_IMPORT_FILE_0 )
        if importNameSetting.useInfoPDF and cleanupLevel == DbKeys.VALUE_NAME_IMPORT_PDF:
            import PyPDF2
            pdf_file = open( sourceFile, 'rb')
            pdf_read = PyPDF2.PdfFileReader(pdf_file)
            endPage =  pdf_read.numPages
            meta     = pdf_read.metadata
            if meta.title is not None:
                bookName = meta.title
            
        bookName = self._cleanupName( bookName , cleanupLevel )
        return { BOOK.numberEnds: endPage , BOOK.name: bookName }

    def _fillInFromCurrent( self, sourceFile:str)->bool:
        book = DbBook().getBookByColumn( BOOK.source , sourceFile )
        if book is None:
            currentFile = {}
        else:
            currentFile = {
                BOOK.name:          book[BOOK.name],
                BOOK.totalPages:    book[BOOK.totalPages],
                BOOK.composer:      book[BOOK.composer],
                BOOK.genre:         book[BOOK.genre ],
                BOOK.numberStarts:  book[BOOK.numberStarts],
                BOOK.numberEnds:    book[BOOK.numberEnds]
            }

        return currentFile


    def _fillInDefaults( self, filelist:list ):
        for sourceFile in filelist :      
            currentFile = { 
                BOOK.source:        sourceFile , 
                BOOK.numberStarts:  1, 
            }
            currentFile.update( self._getInfoPDF( sourceFile ))
            currentFile.update( self._fillInFromCurrent( sourceFile ))
            self.data.append( currentFile )

    def getFileInfo(self, fileList:list )->bool:
        """
            This will go through all of the files and prompt the user
            for properties. If then fills in the information in the data array
        """
        from ui.properties import UiProperties
        fileInfo = UiProperties()
        self.status = self.RETURN_CONTINUE
        self._fillInDefaults(fileList )
        for index, currentFile in enumerate( self.data ) :
            fileInfo.setPropertyList( currentFile )
            if fileInfo.exec() == QDialog.Accepted:
                if len( fileInfo.changes ) > 0:
                    currentFile.update( fileInfo.changes )
                    self.data[index] = currentFile  
            else:
                self.status = self.RETURN_CANCEL
                self.data = []
                break
        return self.status

    def checkForProcessedFiles( self, fileList:list)->list:
        '''
            Check for processed files and present list to user
        '''
        duplist = DbBook().sourcesExist( fileList )
        self.duplicateList = []

        if len( duplist ) > 0 :
            ## First, remove duplicates from filelist
            fileList = [src for src in fileList if src not in duplist ]
            from ui.selectitems import SelectItems 
            sim = SelectItems("Books already processed", "Select files to reprocess" )
            dupDictionary = { os.path.basename( var ) : var for var in duplist }
            sim.setData( dupDictionary )
            sim.setButtonText( "Include files", "Skip All" )
            rtn = sim.exec()
            ## Now, merge in selected IF they clicked 'Include'
            if rtn == QMessageBox.Accepted :
                dupDictionary = sim.getCheckedList()
                if len( dupDictionary) > 0:
                    self.duplicateList = list( dupDictionary.values() )
                    fileList.extend( list( self.duplicateList ) )
                    
        return fileList

    def fixDuplicateNames(self):
        """
            Each entry in the list contains a book name and a location.
            If the location doesn't exist but the name does then we need to
            fix the names.    
        """
        dbb = DbBook()
        musicPath = self.pref.getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        for index, entry in enumerate( self.data ):

            ## Is this location already encoded? If so, we delete the old files
            ## and the database entry.
            if dbb.isSource( entry[ BOOK.source ] ):
                book = dbb.getBookByColumn( BOOK.source , entry[ BOOK.source ])
                dbb.delBook( book[ BOOK.book ])
                shutil.rmtree( book[ BOOK.location ], ignore_errors=True  )

            ## Is the source wasn't encoded but the name is the same
            ## ... if so, we need a different name
            if dbb.isBook( entry[ BOOK.name ]) :
                self.data[ index ][ BOOK.name ] = dbb.getUniqueName( entry[ BOOK.name ] )

    def processDirectoryList(self, fileList:list )->bool:
        if fileList is None or len( fileList ) == 0 :
            return self.RETURN_CANCEL

        fileList = self.checkForProcessedFiles( fileList )
        if self.getFileInfo( fileList ) == self.RETURN_CONTINUE:
            self.fixDuplicateNames()
            for index, entry in enumerate( self.data ):
                baseName = os.path.basename( entry[ BOOK.source ] )
                startMsg = "{}\n{}{}\n{}".format( "="*50 , " "*3 , baseName , "="*50 )
                self._run( startMsg , self.getScript( entry[ BOOK.source ], entry[ BOOK.name ], False) ) 
                if self.status == self.RETURN_CANCEL :
                    break
                self.data[ index ].update( { BOOK.location: self.bookPath} )
                self.data[ index ][ BOOK.totalPages ] = len(fnmatch.filter(os.listdir( self.bookPath ), '*.' + self.bookType))
                if 'debug' in self.data[ index ] :
                    self.data[ index ].pop( 'debug')
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

    def _run(self, startMsg:str, script )->bool:
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
        self._processMessage( startMsg  )

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

    def scriptVars( self , scriptFilename: str ):
        varString = self.pref.getValue(  DbKeys.SETTING_DEFAULT_SCRIPT_VAR, None )
        if varString is None:
            raise RuntimeError("No script variables found")
        vars = varString.split( DbKeys.VALUE_SCRIPT_SPLIT )
        ## fun 'macro' expansion. This can take a keyname and fill in from database
        for index, var in enumerate( vars ):
            if var.startswith('::'):
                if var == '::script':
                    vars[ index ] = scriptFilename
                else: ## fill in from database
                    vars[ index ] = self.pref.getValue( var[2:], '' )

        return vars

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
                shell = self.pref.getValue( DbKeys.SETTING_DEFAULT_SCRIPT , None )
                if shell is None or shell == "":
                    raise RuntimeError("No script found")
                vars = self.scriptVars( self.scriptFile.name )
                self.scriptFile.write( script  )
                self.scriptFile.flush()
                chmod( self.scriptFile.name , 0o550  )
                ### Command should be 'shell vars scriptfilename'
                ###         /bin/bash -c tmp_file
                self._process.start(shell, vars)

            except Exception as err:
                QMessageBox.critical(None,
                "Runtime Error",
                str(err) , 
                QMessageBox.StandardButton.Cancel )
                self.scriptFile.close()

    def getDuplicateList(self)->list:
        """
            This gets a complete list of files that have been 'reprocessed'
        """
        return self.duplicateList


class UiConvertFilenames( UiBaseConvert):
    def __init__(self, location=None ):
        super().__init__()
        if location is not None:
            self.processFile( location )

    def processFile(self, location)->bool:
        """ Pass in either a string or a list for PDF conversion """
        if isinstance( location, list ):
            return self.processDirectoryList( location )
        
        return self.processDirectoryList( [ location ])


class UiConvert(UiBaseConvert):
    
    def __init__(self):
        super().__init__()
    
    def getListOfPdfFiles(self)->str:
        (self.fileName,_) = QFileDialog.getOpenFileNames(
            None,
            "Select PDF File",
            dir=path.expanduser( self.baseDirectory() ),
            filter="(*.pdf *.PDF)",
        )
        if len( self.fileName ) > 0 :
            self.setBaseDirectory( PurePath( self.fileName[0] ).parents[0] )
        return self.fileName
                
    def exec_(self)->bool:
        return self.processDirectoryList( self.getListOfPdfFiles() )

class UiConvertDirectory(UiBaseConvert):
    def __init__(self):
        super().__init__()

    def getDirectory(self)->str:
        self.dirname = QFileDialog.getExistingDirectory(
            None,
            "Select PDF Directory",
            dir=path.expanduser( self.baseDir )
        )
        self.baseDir = self.dirname 
        return self.dirname
               
    def exec_(self)->bool:  
        return self.processDirectoryList( self.getListOfDirs() )

    def getListOfDirs(self ):
        """
            get a list of all files within the directories passed
            
        """
        self.fileName = []
        for path, _ , files in os.walk( self.getDirectory() ):
                for name in files:
                        if name.endswith( '.pdf' ) or name.endswith( '.PDF' ):
                            self.fileName.append( os.path.join( path, name ) )
        return  self.fileName 
        
 
        
if __name__ == "__main__":
    app = QApplication()
    converter = UiConvert()
    converter.exec_()
    app.quit()
    sys.exit(0)
