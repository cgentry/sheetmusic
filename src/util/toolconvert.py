# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
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


from   os import path
from   datetime import datetime
from   pathlib import PurePath
import fnmatch
import os
import re
import shutil
import sys

from PySide6.QtWidgets import (
        QApplication,       QDialog, 
        QFileDialog,        QMessageBox,        
    )

from qdb.dbbook       import DbBook
from qdb.keys         import BOOK, BOOKPROPERTY, DbKeys, ImportNameSetting
from qdil.preferences import DilPreferences
from ui.runscript     import UiRunScript
from util.utildir     import get_scriptpath
from util.pdfinfo     import PdfInfo
    
class UiBaseConvert( UiRunScript ):
    """
        UiBaseConvert contains code to process a list of PDF files and store them
        in the sheetmusic directory. Directory prompts should occur in the derived classes
    """
    # The following are only used to give labels to our return status
    RETURN_CANCEL=False
    RETURN_CONTINUE=True
    SCRIPT='_importpdf.sh'

    CONVERT_DEVICE='d'
    CONVERT_SOURCE='s'
    CONVERT_TARGET='t'
    CONVERT_TYPE='y'
    CONVERT_RES='r'


    def __init__(self)->None:
        super().__init__( get_scriptpath(UiBaseConvert.SCRIPT) )
        self.pref = DilPreferences()
        self.status  = self.RETURN_CANCEL
        self.set_output( 'text')

        self.bookType   = self.pref.getValue(DbKeys.SETTING_FILE_TYPE, DbKeys.VALUE_FILE_TYPE)
        self.page_suffix = self.pref.getValue( DbKeys.SETTING_FILE_TYPE, default=DbKeys.VALUE_FILE_TYPE )
        self.music_path = self.pref.getMusicDir()
        self.baseDir = '~'
        self.data = []
        self.duplicateList = []
        
    def setBaseDirectory(self, dir:str):
        if dir is not None:
            self.baseDir = dir

    def baseDirectory(self)->str:
        return ( self.baseDir if self.baseDir else DbKeys.VALUE_LAST_IMPORT_DIR )

    def _is_valid_book_directory( self, bookDir:str )->bool:
        """
            Check if a directory exists for a book, check for pages that exist in directory
        """
        
        return  ( os.path.isdir(bookDir) and len(fnmatch.filter(os.listdir(bookDir), '*.' + self.page_suffix)) > 0 )

    def _cleanup_book_name(self, bookName:str, level:int )->str:
        """ This takes a book name and gets rid of bad characters in prep for filename"""

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
    
    def _fill_in_from_database( self, sourceFile:str)->dict:
        """ This will read data from the database if the file has been imported before
        
            This will override all of the data set from the PDF as it's already been cleaned up.
        """

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

    def _fill_in_all_file_info( self, filelist:list ):
        """ Fill in default information, then get info from current entry if exists """
        
        cleanup_level = self.pref.getValueInt( DbKeys.SETTING_NAME_IMPORT , DbKeys.VALUE_NAME_IMPORT_FILE_2)
        for sourceFile in filelist :      
            currentFile = { 
                BOOK.name:          PurePath( sourceFile ).stem ,
                BOOK.source:        sourceFile , 
                BOOK.numberStarts:  1,
                BOOK.composer:      None,
                BOOK.genre:         None,
                BOOK.fileCreated:   datetime.fromtimestamp( os.path.getctime(sourceFile) ).isoformat(' '),
                BOOK.fileModified:  datetime.fromtimestamp( os.path.getmtime(sourceFile) ).isoformat(' '),
                BOOKPROPERTY.layout:        DbKeys.VALUE_PAGES_SINGLE,
            }
            pdfinfo = PdfInfo()
            if pdfinfo.has_pdf_library():
                currentFile.update( pdfinfo.get_info_from_pdf( sourceFile ))
                cleanup_level = DbKeys.VALUE_NAME_IMPORT_PDF
            currentFile[ BOOK.name] = self._cleanup_book_name( currentFile[ BOOK.name ], cleanup_level )
            currentFile.update( self._fill_in_from_database( sourceFile ))
            
            self.data.append( currentFile )

    def getFileInfo(self, fileList:list )->bool:
        """
            This will go through all of the files and prompt the user
            for properties. If then fills in the information in the data array
        """

        from ui.properties import UiProperties
        fileInfo = UiProperties()
        self.status = self.RETURN_CONTINUE
        self._fill_in_all_file_info(fileList )
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
                self.add_variable( 'SOURCE_FILE', entry[ BOOK.source ])
                self.add_variable( 'TARGET_DIR', entry[ BOOK.name   ])
                self.bookPath = path.join( self.music_path , entry[ BOOK.name ])
                if self.run( ) == self.RETURN_CANCEL :
                    break
                if self.is_debug():
                    return self.RETURN_CANCEL
                self.data[ index ].update( { BOOK.location: self.bookPath} )
                if self._is_valid_book_directory( self.bookPath ):
                    self.data[ index ][ BOOK.totalPages ] = len(fnmatch.filter(os.listdir( self.bookPath ), '*.' + self.bookType))
                else:
                    self.data[ index ][ BOOK.totalPages ] = 0
                self.reset()
        return self.status
   
    def add_final_vars( self ):
        # self.addVariableFlag( self.CONVERT_TYPE , self.bookType )
        # varString = self.pref.getValue(  DbKeys.SETTING_DEFAULT_SCRIPT_VAR, None )
        # if varString is None:
        #     raise RuntimeError("No script variables found")
        # vars = varString.split( DbKeys.VALUE_SCRIPT_SPLIT )
        # ## fun 'macro' expansion. This can take a keyname and fill in from database
        # for index, var in enumerate( vars ):
        #     if var.startswith('::'):
        #         if var == '::script':
        #             vars[ index ] = scriptFilename
        #         else: ## fill in from database
        #             vars[ index ] = self.pref.getValue( var[2:], '' )

        pass

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
                
    def process_files(self)->bool:
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
