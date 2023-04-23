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

from os import path
from pathlib import PurePath
import fnmatch
import os

from PySide6.QtWidgets import (
    QApplication,
    QDialog,            QProgressDialog,
    QFileDialog,        QMessageBox,
    QComboBox,          QDialogButtonBox,
    QLabel,             QGridLayout,
    QTextEdit,          QWidget
)
from PySide6.QtCore import Qt
from qdb.keys import BOOK, BOOKMARK, DbKeys, LOG
from qdb.log import DbLog
from qdb.mixin.fieldcleanup import MixinFieldCleanup
from qdb.mixin.tomlbook import MixinTomlBook

from qdil.preferences import DilPreferences
from qdil.book import DilBook
from qdil.bookmark import DilBookmark

from ui.mixin.importinfo import MixinFileInfo, MixinPDFInfo, MixinDBInfo, MixinFilterFiles
from ui.runscript import UiRunScript, UiScriptSetting, ScriptKeys
from ui.simpledialog import SimpleDialog
from ui.util import centerWidgetOnScreen
from util.simpleparse import SDOption
from ui.status import UsingStatusDialog, UiStatus



class ImportSettings():
    """ This holds generic routines for import script settings """
    PREFIX = 'import'

    def importKey(script_path: str) -> str:
        """ Format the script_path value into a unique database key """
        return '{}_{}'.format(ImportSettings.PREFIX, path.basename(script_path))

    def setting(script_path: str) -> dict | None:
        """ get the setting for a script_path """
        return DilPreferences().getValuePickle(ImportSettings.importKey(script_path), None)

    def save(script_path: str, values: dict) -> str:
        """ Save the dictionary into the name of the script. Add a prefix so there is never a conflict"""
        return DilPreferences().setValuePickle(key=ImportSettings.importKey(script_path), value=values, replace=True)

    def save_select(script_path: str):
        """ Set the 'script_path' as the current import file"""
        DilPreferences().setValue(DbKeys.SETTING_IMPORT_SCRIPT, script_path, replace=True)

    def get_select() -> str | None:
        return DilPreferences().getValue(DbKeys.SETTING_IMPORT_SCRIPT, None)


class UiImportSetting():
    """ Handle prompting, saving, return of fields """

    def __init__(self):
        self._changed = False
        self.logger = DbLog('UiImportSetting')

    def setting(self) -> dict | None:
        """ This returns the current selected import. If there is no selected, an error is displayed and None is returned

        use this to get variables to export to the environment
        """
        script = ImportSettings.get_select()
        if script is None:
            QMessageBox.critical(
                None, 'Import Error', 'No import filter is selected', QMessageBox.Cancel)
            return None

        return ImportSettings.setting(script)

    def was_changed(self) -> bool:
        return self._changed

    def edit_setting(self, script_path: str, current_setting: dict | None) -> dict | None:
        """ Open and run a simple dialog from the script then save the setting """
        self.script_parms = UiScriptSetting(script_path)
        if not self.script_parms.is_set(ScriptKeys.DIALOG):
            QMessageBox.critical(None, 'Invalid import script', 'Script does not contain dialog settings\n{}'.format(
                script_path), QMessageBox.Cancel)
            return None
        sd = SimpleDialog()
        sd.parse(self.script_parms.setting(ScriptKeys.DIALOG))
        if sd.exec():
            self._changed = True
            data_dict = {}
            for entry in sd.data:
                data_dict[entry[SDOption.KEY_TAG]] = entry[SDOption.KEY_VALUE]
            ImportSettings.save(script_path, data_dict)
            return sd.data
        self._changed = False
        return current_setting

    def select(self, script_path: str) -> dict:
        """ select saves the script_path as the current one and will display an edit dialog"""
        self._changed = False
        values = ImportSettings.setting(script_path)
        return self.edit_setting(script_path, values)

    def _create_dialog(self):
        self.dlg = QDialog()
        self.dlg.setWindowTitle('Select Input Script')
        self.layout = QGridLayout()
        self.lbl_script = QLabel('Select Script')
        self.cmb_script = QComboBox()
        self.lbl_comment = QLabel('Description')
        self.txt_comment = QTextEdit()

        self.btnbox = QDialogButtonBox()
        self.btnbox.addButton(QDialogButtonBox.Save)
        self.btnbox.addButton(QDialogButtonBox.Cancel)
        self.btnbox.addButton('Edit settings', QDialogButtonBox.ActionRole)
        self.btnbox.accepted.connect(self._btn_accept)
        self.btnbox.rejected.connect(self._btn_reject)
        self.btnbox.clicked.connect(self._btn_clicked)
        self.layout.addWidget(self.lbl_script, 0, 0)
        self.layout.addWidget(self.cmb_script, 0, 1)
        self.layout.addWidget(self.lbl_comment, 1, 0)
        self.layout.addWidget(self.txt_comment, 1, 1)
        self.layout.addWidget(self.btnbox, 2, 1)

        self.dlg.setLayout(self.layout)

    def _picked_importpdf_entry(self, value):
        """ Set the comment text to the comment from the list """
        if value > -1:
            data = self.cmb_script.itemData(value)
            if data is None:
                self.txt_comment.clear()
            else:
                self.txt_comment.setText(data.comment())
        self.cmb_script.setFocus()

    def _btn_reject(self):
        self.dlg.reject()

    def _get_script_current(self) -> str | None:
        index = self.cmb_script.currentIndex()
        if index > -1:
            toolscript = self.cmb_script.itemData(index)
            if toolscript is not None:
                script = toolscript.path()
                return script
        return None

    def _btn_accept(self):
        script = self._get_script_current()
        if script is not None:
            ImportSettings.save_select(script)
        self.dlg.accept()

    def _btn_clicked(self, btn):
        if btn.text() == 'Edit settings':
            script = self._get_script_current()
            if script is not None:
                self.edit_setting(script, ImportSettings.setting(script))

    def pick_import(self):
        """ Pick import simply shows a list and comments, then allows the user to pick one and save it

            Note: this doesn't set the values. That is done later when popped up OR when they click 'Edit'
        """

        from util.toollist import GenerateImportList
        import_list = GenerateImportList().list()
        current = ImportSettings.get_select()

        self._create_dialog()
        if current is None:
            self.cmb_script.addItem('- No import script selected', None)
        self.cmb_script.currentIndexChanged.connect(
            self._picked_importpdf_entry)
        index = 0
        self.cmb_script.setCurrentIndex(-1)
        for key, tscript in import_list.items():
            self.cmb_script.addItem(key, tscript)
            if current is not None and tscript.path() == current:
                self.cmb_script.setCurrentIndex(index)
                self.txt_comment.setText(tscript.comment())
            index += 1
        if current is None:
            self.cmb_script.setCurrentIndex(0)
        self.cmb_script.setFocus()
        centerWidgetOnScreen(self.dlg)
        self.dlg.exec()


class UiBaseConvert(MixinFileInfo, MixinPDFInfo, MixinDBInfo, MixinTomlBook, MixinFieldCleanup, MixinFilterFiles, UiRunScript):
    """
        UiBaseConvert contains code to process a list of PDF files and store them
        in the sheetmusic directory. Directory prompts should occur in the derived classes
    """
    # The following are only used to give labels to our return status
    RETURN_CANCEL = False
    RETURN_CONTINUE = True
    SCRIPT = '_importpdf.sh'

    CONVERT_DEVICE = 'd'
    CONVERT_SOURCE = 's'
    CONVERT_TARGET = 't'
    CONVERT_TYPE = 'y'
    CONVERT_RES = 'r'

    def __init__(self) -> None:
        super().__init__(ImportSettings.get_select())
        self.add_to_environment(ImportSettings.setting(self.script_file))
        self.dilb = DilBook()
        self.pref = DilPreferences()
        self.bookmark = DilBookmark()
        self.status = self.RETURN_CANCEL
        self.set_output('text')
        self.logger = DbLog('UiBaseConvert')

        self.bookType = self.pref.getValue(
            DbKeys.SETTING_FILE_TYPE, DbKeys.VALUE_FILE_TYPE)
        self.page_suffix = self.pref.getValue(
            DbKeys.SETTING_FILE_TYPE, default=DbKeys.VALUE_FILE_TYPE)
        self.music_path = self.pref.getMusicDir()
        self.baseDir = '~'
        self.data = []

    def _is_valid_book_directory(self, bookDir: str) -> bool:
        """
            Check if a directory exists for a book, check for pages that exist in directory
        """
        return (os.path.isdir(bookDir) and len(fnmatch.filter(os.listdir(bookDir), '*.' + self.page_suffix)) > 0)

    def _fill_in_all_file_info(self, sourcelist: list[str]) -> bool:
        """ From the filelist, fill in all the data from files, tomls, etc """
        label_format = '{:4d}: {:<100s} '

        self.data = []
        self.status = self.RETURN_CONTINUE
        
        if len(sourcelist)>0:
            count = 0
            status_dlg = UiStatus()
            status_dlg.setWindowTitle('Get infomration from PDF')
            status_dlg.maximum = len(sourcelist )
            for sourceFile in sourcelist:
                status_dlg.setValue(count)
                count += 1
                status_dlg.title = label_format.format(
                    count, os.path.basename(sourceFile))
                
                self.open_pdf( sourceFile )
                if status_dlg.wasCanceled():
                    self.status = self.RETURN_CANCEL
                    break
                self.open_pdf(sourceFile)  # Open first to give time to load
                status_dlg.information = '...from file'

                # Load in file information first
                currentFile = self.get_info_from_file(sourceFile)

                # PDF info
                status_dlg.information = '...from PDF'
                currentFile.update(self.get_info_from_pdf(sourceFile))

                # TOML PROPERTIES FILE (optional)
                status_dlg.information = '...from config file (.cfg)'
                currentFile.update(self.read_toml_properties_file(sourceFile))

                # cleanup the filename
                currentFile[BOOK.name] = self.clean_field_value(
                    currentFile[BOOK.name])

                # From database
                status_dlg.information = '...from database'
                currentFile.update(self._fill_in_from_database(sourceFile))

                # Add to the data list
                self.data.append(currentFile)
            
        return self.status

    def importFiles(self) -> list[dict]:
        return self.data

    def _setsourcetype( self ):
        """ Set a source_type in the data if none was preset 
        """
        for index, book in enumerate( self.data ):
            if not BOOK.source_type in book or not book[ BOOK.source_type ]:
                if book[ BOOK.source ] == book[ BOOK.location ] or  (book[ BOOK.location ]).lower().endswith( 'pdf'):
                    self.data[ index ][BOOK.source_type ] = DbKeys.VALUE_PDF
                else:
                    self.data[ index ][BOOK.source_type ] = DbKeys.VALUE_PNG
        
    def add_books_to_library(self) -> bool:
        """ Import PDF imports all the PDF content and re-imports previous bookmarks
            This will only add books if we have a good status and there is some data
            to import
        """
        
        counter = 0
        if self.status:
            bookmarks = {}
            for loc in self.getduplicateList():
                bmk = DilBookmark( self.dilb.lookup_book_by_column(BOOK.source, loc) )
                bookmark = bmk.getAll()
                if bookmark is not None:
                    bookmarks[loc] = bookmark
                self.logger.debug('Delete current book entry {}'.format(loc))
                self.dilb.delete(BOOK.source, loc)

            if len(self.data) > 0:
                self._setsourcetype()
                plural = ( 's' if counter > 1 else '' )
                status_dlg = UiStatus()
                status_dlg.setWindowTitle( 'Add book{} to library'.format( plural ))
                status_dlg.maximum = len( self.data )
                label_format = '{:4d}: {:<100s} '
                for book_data in self.data:
                    if status_dlg.wasCanceled():
                        self.status = self.RETURN_CANCEL
                        break

                    status_dlg.setValue(counter)
                    counter += 1
                    status_dlg.title = label_format.format(counter, book_data[BOOK.title ])
                                    
                    self.logger.debug('Add new book {} Location {} Type {}'.format(
                        book_data[BOOK.book], book_data[BOOK.location], book_data[BOOK.source_type]))
                    self.dilb.delete(BOOK.source, book_data[BOOK.source])
                    new_book = self.dilb.newBook(**book_data)
                    if book_data[BOOK.source] in bookmarks:
                        for marks in bookmarks[book_data[BOOK.source]]:
                            self.bookmark.add(
                                new_book[BOOK.id],
                                marks[BOOKMARK.name],
                                marks[BOOKMARK.page]
                            )
                status_dlg.title = '{} Book{} added.'.format( counter , plural )
                status_dlg.information = ""
                status_dlg.buttonText = 'Close'
                status_dlg.setValue( len(self.data) )
                status_dlg.show()
        return (self.status and len(self.data) > 0 )

    def update_file_properties(self) -> bool:
        """
            This will go through all of the files and prompt the user
            for properties. It then fills in the information in the data array
        """

        self.status = self.RETURN_CONTINUE
        from ui.properties import UiProperties
        uiproperties = UiProperties()
        for index, currentFile in enumerate(self.data):
            uiproperties.set_properties(currentFile)
            if uiproperties.exec() != QDialog.Accepted:
                # Cancel the conversion
                self.status = self.RETURN_CANCEL
                self.data = []
                break

            if len(uiproperties.changes) > 0:
                # UPDATE the data and TOML properties file
                currentFile.update(uiproperties.changes)
                self.write_toml_properties(
                    currentFile, currentFile[BOOK.source])
                self.data[index] = currentFile

        return self.status

    def fixDuplicateNames(self):
        """
            Each entry in the list contains a book name and a location.
            If the location doesn't exist but the name does then we need to
            fix the names.
        """
        for index, book_entry in enumerate(self.data):
            self.data[index][BOOK.name] = self.dilb.getUniqueName(
                book_entry[BOOK.name])

    def filelist_to_dictionary(self, fileList: list) -> bool:
        """ Call functions that fill in all the data and cleanup for processing"""
        if fileList is None or len(fileList) == 0:
            self.status = self.RETURN_CANCEL
        else:
            if self._fill_in_all_file_info(fileList) == self.RETURN_CONTINUE:
                if self.update_file_properties() == self.RETURN_CONTINUE:
                    self.fixDuplicateNames()
        return self.status

    def _process_conversion_list(self, fileList: list) -> bool:
        """ Process all of the files in the filelist and run the selected script
        This does not import into the database. for that, call add_books_to_library

        N.B. Use processPdfList for PDF->PDF files
    """

        if self.filelist_to_dictionary(fileList) == self.RETURN_CONTINUE:
            for index, entry in enumerate(self.data):
                self.add_variable('SOURCE_FILE', entry[BOOK.source])
                self.add_variable('TARGET_DIR', entry[BOOK.name])
                self.bookPath = path.join(self.music_path, entry[BOOK.name])
                if self.run(no_dialog=True) == self.RETURN_CANCEL:
                    break
                if self.is_debug():
                    return self.RETURN_CANCEL
                self.data[index].update({BOOK.location: self.bookPath})
                if self._is_valid_book_directory(self.bookPath):
                    self.data[index][BOOK.totalPages] = len(fnmatch.filter(
                        os.listdir(self.bookPath), '*.' + self.bookType))
                else:
                    self.data[index][BOOK.totalPages] = 0
                self.reset()
        return self.status

    def _process_pdf_list( self, filelist: list )->bool:
        if self.filelist_to_dictionary(filelist) == self.RETURN_CONTINUE:
            for index in range(len(self.data)):
                self.data[index][BOOK.source_type] = 'pdf'
                self.data[index][BOOK.location] = self.data[index][BOOK.source]
        return self.status

    def add_final_vars(self):
        pass

    def getListOfPdfFiles(self) -> list[str]:
        self.logger.critical( 'getListOfPdfFiles is not implemented')
        raise NotImplementedError("getListOfPdfFiles is not implemented")
    
    def processDirectoryList( self, data:list[str])->bool:
        self.logger.critical( 'processDirectoryList is not implemented' )
        raise NotImplementedError('processDirectoryList is not implemented')

    def process_files(self) -> bool:
        """
            Handle the splitting of file lists and processing. This calls 
            'processDirectoryList' which should be defined in the derived class
        """
        self.split_selected(self.getListOfPdfFiles())
        return self.processDirectoryList(self.getFileList())

    def _find_files_in_subdir(self, dir):
        """ Fill in all the files within the directory and subdirectory """
        for path, _, files in os.walk(dir):
            for name in files:
                if name.endswith('.pdf') or name.endswith('.PDF'):
                    self.fileNames.append(os.path.join(path, name))
        return self.fileNames

    def get_files_from_directory(self, title:str='Select PDF Directory') -> list[str]:
        """ Prompt the user for a directory then find all PDF files """
        self.fileNames = []
        self.dirname = QFileDialog.getExistingDirectory(
            None,
            title,
            dir=path.expanduser(self.baseDirectory())
        )
        if self.dirname:
            self.setBaseDirectory(self.dirname)
            self._find_files_in_subdir(self.dirname)
        return self.fileNames

    def get_files(self, title: str = 'Select PDF Files') -> list[str]:
        """ Prompt the user for PDF files and return a list """
        (self.fileNames, _) = QFileDialog.getOpenFileNames(
            None,
            title,
            dir=path.expanduser(self.baseDirectory()),
            filter="(*.pdf *.PDF)"
        )

        if not self.fileNames:
            self.fileNames = []
        if len(self.fileNames) > 0:
            self.setBaseDirectory(PurePath(self.fileNames[0]).parents[0])
        return self.fileNames


class UiConvertFilenames(UiBaseConvert):
    """ This is used to reimport a file, or list of files """

    def __init__(self, location=None):
        super().__init__()
        if location is not None:
            self.processFile(location)

    def processFile(self, location) -> bool:
        """ Pass in either a string or a list for PDF conversion """
        if isinstance(location, list):
            return self.processDirectoryList(location)

        return self.processDirectoryList([location])
    
    def getListOfPdfFiles(self)->list[str]:
        return self.get_files()
    
    def processDirectoryList( self, data:list[str])->bool:
        return self._process_conversion_list( data )


class UiConvertPDFDocuments(UiBaseConvert):
    """ Import and convert a single file """

    def __init__(self):
        super().__init__()

    def getListOfPdfFiles(self) -> list[str]:
        return self.get_files()
    
    def processDirectoryList( self, data:list[str])->bool:
        return self._process_conversion_list( data )
       

class UiImportPDFDocuments(UiConvertPDFDocuments):
    """ Import a PDF Document without conversion """

    def getListOfPdfFiles(self) -> list[str]:
        return self.get_files()
    
    def processDirectoryList(self, data:list[str] )->bool:
        return self._process_pdf_list( data )


class UiConvertPDFDocumentDirectory(UiBaseConvert):
    """ Import and convert a directory of PDFs"""


    def getListOfPdfFiles(self) -> list[str]:
        self.get_files_from_directory()

    def processDirectoryList(self, data: list[str]) -> bool:
        return self._process_conversion_list( data )


class UiImportPdfDirectory(UiConvertPDFDocumentDirectory):
    """ Import a directory contents of PDFs without conversion to PNGs """

    def getListOfPdfFiles(self, title=str):
        return self.get_files_from_directory()
    
    def processDirectoryList(self, filelist: list):
        return self._process_pdf_list( filelist )
