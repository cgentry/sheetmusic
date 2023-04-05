from datetime import datetime
from os import path
from pathlib import PurePath
from typing import Callable
import os
import pathlib

from PySide6.QtWidgets import (QMessageBox)

from qdb.dbbook import DbBook
from qdb.keys import BOOK, BOOKPROPERTY, BOOKSETTING, DbKeys
from ui.selectitems import SelectItems

try:
    from PySide6.QtPdf import QPdfDocument
    IMPORT_INFO_HAS_QPDF_DOCUMENT = True
except:
    IMPORT_INFO_HAS_QPDF_DOCUMENT = False


class MixinFileInfo:
    """
        The MIXIN contains general routines for importing content into the system
        from the file itself (a PDF)
        It does not insert or convert content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setBaseDirectory(self, dir: str):
        if dir is not None:
            self.baseDir = dir

    def baseDirectory(self) -> str:
        return (self.baseDir if self.baseDir else DbKeys.VALUE_LAST_IMPORT_DIR)

    def get_info_from_file(self, sourceFile: str) -> dict:
        """ fill in the basic file information. Information should be overridden by PDF, then DB """
        created = datetime.fromtimestamp(
            os.path.getctime(sourceFile)).isoformat(' ')
        modified = datetime.fromtimestamp(
            os.path.getmtime(sourceFile)).isoformat(' ')
        return {
            BOOK.name:              PurePath(sourceFile).stem,
            BOOK.source:            sourceFile,
            BOOK.numberStarts:      1,
            BOOK.composer:          DbKeys.VALUE_DEFAULT_COMPOSER,
            BOOK.genre:             DbKeys.VALUE_DEFAULT_GENRE,
            BOOK.fileCreated:       created,
            BOOK.fileModified:      modified,
            BOOK.pdfCreated:        created,
            BOOK.pdfModified:       modified,
            BOOKPROPERTY.layout:    DbKeys.VALUE_PAGES_SINGLE,
        }

    def _print_data(self, label: str, data: dict):
        """ Debug routine for use when testing out routines."""
        print(label)
        for key in sorted(data.keys()):
            print("\tKEY: '{:30s}' VALUE: '{}'".format(key, data[key]))


    def checkForProcessedFiles(self, fileList: list) -> tuple[list, list]:
        ''' 
            Check the fileList for processed files and return two lists:
            all files to be processed and the duplicate files to be reprocessed

            fileList is the list of file(s) selected form import (PDFs)
            Check the database to see if they exist (sourcesExist) and
            present the user a list of books. Those are added back to the
            fileList if they are selected. If not, they are put in the duplicates_kept
        '''
        duplist = DbBook().sourcesExist(fileList)
        duplicates_kept = []

        if len(duplist) > 0:
            # First, remove duplicates from filelist
            fileList = [src for src in fileList if src not in duplist]
            sim = SelectItems("Books already processed",
                              "Select files to reprocess")
            dupDictionary = {os.path.basename(var): var for var in duplist}
            sim.setData(dupDictionary)
            sim.setButtonText("Include Selected Files", "Skip All Reprocessed Files")
            rtn = sim.exec()
            # Now, merge in selected IF they clicked 'Include'
            if rtn == QMessageBox.Accepted:
                dupDictionary = sim.getCheckedList()
                if len(dupDictionary) > 0:
                    duplicates_kept = list(dupDictionary.values())
                    fileList.extend(list(duplicates_kept))

        return fileList, duplicates_kept


class MixinPDFInfo:
    """ Read document information from the PDF File 

        This uses the internal QPdfDocument library functions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_pdf_library(self) -> bool:
        return IMPORT_INFO_HAS_QPDF_DOCUMENT

    def open_pdf(self, pdf_document:str):
        """MixinPDFInfo: create a QPdfDocument instance and load the document file"""
        self.pdfDocument = QPdfDocument()
        self.pdfDocument.load(pdf_document)

    def _calculate_pdf_largest_size(self):
        _width = 0
        _height = 0

        for page in range(self.pdfDocument.pageCount()):
            pdf_point_size = self.pdfDocument.pagePointSize(page)
            if pdf_point_size is not None:
                _width = max(pdf_point_size.width(), _width)
                _height = max(pdf_point_size.height(), _height)
        return _width, _height
    
    def get_info_from_pdf(self, sourcefile)->dict:
        if self.pdfDocument is None:
            self.open_pdf(sourcefile)

        def setBookValue(key:str, value):
            if value:
                pdf_info[key] = str( value ).strip()

        def setBookMeta(key:str, meta_key):
            setBookValue(key, str( self.pdfDocument.metaData(meta_key)).strip() )

        pdf_info = {
            BOOK.totalPages: self.pdfDocument.pageCount(),
            BOOK.numberEnds: self.pdfDocument.pageCount(),
        }
        setBookMeta(BOOK.author, QPdfDocument.MetaDataField.Author)
        setBookMeta(BOOK.name, QPdfDocument.MetaDataField.Title)
        setBookMeta(BOOK.publisher, QPdfDocument.MetaDataField.Producer)

        setBookValue(BOOK.pdfCreated, self.pdfDocument.metaData(
            QPdfDocument.MetaDataField.CreationDate).toString('yyyy-MM-dd HH:mm:ss'))
        setBookValue(BOOK.pdfModified, self.pdfDocument.metaData(
            QPdfDocument.MetaDataField.ModificationDate).toString('yyyy-MM-dd HH:mm:ss'))
        
        if BOOK.name not in pdf_info or pdf_info[BOOK.name] == '':
            pdf_info[BOOK.name] = str( pathlib.Path(sourcefile).stem ).strip()
        pdf_info[BOOKSETTING.maxWidth ], pdf_info[BOOKSETTING.maxHeight] = self._calculate_pdf_largest_size( )

        self.pdfDocument.close()
        self.pdfDocument = None
        return pdf_info


class MixinDBInfo:
    """ Read document information from the database, if previously imported """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fill_in_from_database(self, sourceFile: str) -> dict:
        """ This will read data from the database if the file has been imported before
            This will override all of the data set from the PDF as it's already been cleaned up.
        """
        def getBookField(target: str, field: str):
            if field in book and book[field]:
                currentFile[target] = book[field]

        currentFile = {}
        book = DbBook().getBookByColumn(BOOK.source, sourceFile)
        if book is not None:
            getBookField(BOOK.name,          BOOK.name)
            getBookField(BOOK.totalPages,    BOOK.totalPages)
            getBookField(BOOK.composer,      BOOK.composer)
            getBookField(BOOK.genre,         BOOK.genre)
            getBookField(BOOK.numberStarts,  BOOK.numberStarts)
            getBookField(BOOK.numberEnds,    BOOK.numberEnds)

        return currentFile


class MixinFilterFiles():
    """ Take a list of files and split into three: 
        files to be processed, 
        duplicate files in the files-to-be-processed list (already processed) 
        files that are duplicates and won't be processed. 
        
        It requires two external functions that can be passed in for testing:
        * check_db_for_source - see the filenames in the list are in the database
        * filter_dialog: prompt the user to select files to be reproessed
        If you dont supply those functions, sensible defaults will be used.
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_list      = []  # list of filename strings
        self.duplicate_list = []
        self.ignored_list   = []

    def getFileList(self) -> list[str]:
        return self.file_list

    def getduplicateList(self) -> list[str]:
        """ List of files that are NOT being reprocessed"""
        return self.duplicate_list
    
    def getIgnoredList(self) -> list[str]:
        return self.ignored_list

    def _apply_filter(self, reprocess_list: list[str]):
        """ split all the files out. reprocess_list are all the files selected to be processed.

        There are three lists:
        1) file_list :      all the files that should be processed
        2) duplicate_list:  Duplicates that are to be processed (also in file_list)
        3) ignored_files:   Files that will be ignored
           (and not in file_list or duplicate_list)
        """

        self.duplicate_list = [ proc for proc in reprocess_list if proc in self.file_list ]
        self.ignored_list   = [ proc for proc in self.ignored_list if proc not in self.duplicate_list and proc in self.file_list ]
        self.file_list      = [ proc for proc in self.file_list if proc not in self.ignored_list ]

        return

    def _reprocess_dialog(self, duplicate_list: list[str]) -> list:
        """ Prompt the user for what files to re-process. Return a list of those files"""
        sim = SelectItems("Books already processed",
                          "Select files to reprocess")
        dupDictionary = {os.path.basename(var): var for var in duplicate_list}
        sim.setData(dupDictionary)
        sim.setButtonText("Reprocess Selected Files",
                          "Skip All Processed Files")
        rtn = sim.exec()

        # Get the list of files they want reprocessed
        return sim.getCheckedListValues()
    
    def split_selected(self,
                    selected_files: list[str],
                    check_db_for_source:Callable[ [list], list  ]=None, 
                    filter_dialog:Callable[ [list], list ]=None) -> tuple[list[str], list, list]:
        ''' 
            Split a file list into three:
            * list of files to be processed (from a openFile dialog)
            * Duplicate files (they also are in files to be processed)
            * ignored files (ones not processed)

            selected_files is the list of file(s) selected form import (PDFs)
            check_db_for_source is the routine to check the database if the source is in the location
            filter_dialog is the dialog to get user selected files for reprocessing

        '''
        
        if filter_dialog is None:
            filter_dialog = self._reprocess_dialog
        if check_db_for_source is None:
            check_db_for_source = DbBook().sourcesExist

        self.file_list = selected_files
        self.ignored_list = check_db_for_source(selected_files)
        self.duplicate_list = []

        if len(self.ignored_list) > 0:
            # duplicates-to-process from list of files-to-ignore
            self.duplicate_list = filter_dialog(self.ignored_list)
            # if len(self.duplicate_list) > 0:
        self._apply_filter(self.duplicate_list)

        return self.file_list, self.duplicate_list, self.ignored_list
