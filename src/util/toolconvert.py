"""
Utility functions : conversion interfaces

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from os import path
from pathlib import PurePath
import fnmatch
import os

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,        QMessageBox,
    QComboBox,          QDialogButtonBox,
    QLabel,             QGridLayout,
    QTextEdit
)
from constants import ProgramConstants
from qdb.fields.bookmark import BookmarkField
from qdb.keys import DbKeys
from qdb.log import DbLog
from qdb.mixin.fieldcleanup import MixinFieldCleanup
from qdb.mixin.tomlbook import MixinTomlBook

from qdb.fields.book import BookField
from qdil.dil import Dils

from ui.mixin.importinfo import (
    MixinFileInfo, MixinPDFInfo, MixinDBInfo, MixinFilterFiles)
from ui.properties import UiProperties
from ui.runscript import UiRunScript
from ui.scripthelpers import UiScriptSetting, ScriptKeys
from ui.simpledialog import SimpleDialog
from ui.status import UiStatus
from ui.util import center_on_screen
from util.simpleparse import SDOption
from util.toollist import GenerateImportList
from util.convert import encode, decode


class ImportSettings():
    """ This holds generic routines for import script settings """

    @staticmethod
    def import_key(script_path: str) -> str:
        """ Format the script_path value into a unique database key """
        return f'import_{path.basename(script_path)}'

    @staticmethod
    def setting(script_path: str) -> dict | None:
        """ get the setting for a script_path """
        dil = Dils()
        return decode(
            code=DbKeys.ENCODE_PICKLE,
            value=dil.prefs.get_value(
                key=ImportSettings.import_key(script_path),
                default=None))

    @staticmethod
    def save(script_path: str, values: dict) -> str:
        """ Save the dictionary into the name of the script.
        Add a prefix so there is never a conflict"""
        dil = Dils()
        return dil.prefs.set_value(
            key=ImportSettings.import_key(script_path),
            replace=True,
            value=encode(values, code=DbKeys.ENCODE_PICKLE))

    @staticmethod
    def save_select(script_path: str):
        """ Set the 'script_path' as the current import file"""
        dil = Dils()
        dil.prefs.set_value(DbKeys.SETTING_IMPORT_SCRIPT, script_path, replace=True)

    @staticmethod
    def get_select() -> str | None:
        """ Return the import script location """
        dil = Dils()
        return dil.prefs.get_value(DbKeys.SETTING_IMPORT_SCRIPT, None)


class UiImportSetting():
    """ Handle prompting, saving, return of fields """

    def __init__(self):
        self._changed = False
        self.script_parms = None

        self.dlg = QDialog()
        self.cmb_script = QComboBox()
        self.txt_comment = QTextEdit()
        self.logger = DbLog('UiImportSetting')

    def setting(self) -> dict | None:
        """ This returns the current selected import.
        If there is no selected, an error is displayed and None is returned

        use this to get variables to export to the environment
        """
        script = ImportSettings.get_select()
        if script is None:
            QMessageBox.critical(
                None, 'Import Error', 'No import filter is selected', QMessageBox.Cancel)
            return None

        return ImportSettings.setting(script)

    def was_changed(self) -> bool:
        """ Return true if setting was edited """
        return self._changed

    def edit_setting(self, script_path: str, current_setting: dict | None) -> dict | None:
        """ Open and run a simple dialog from the script then save the setting """
        self.script_parms = UiScriptSetting(script_path)
        if not self.script_parms.is_set(ScriptKeys.DIALOG):
            QMessageBox.critical(None,
                                 'Invalid import script',
                                 f'Script does not contain dialog settings\n{script_path}',
                                 QMessageBox.Cancel)
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
        layout = QGridLayout()
        btnbox = QDialogButtonBox()

        self.dlg.setWindowTitle('Select Input Script')

        btnbox.addButton(QDialogButtonBox.Save)
        btnbox.addButton(QDialogButtonBox.Cancel)
        btnbox.addButton('Edit settings', QDialogButtonBox.ActionRole)
        btnbox.accepted.connect(self._btn_accept)
        btnbox.rejected.connect(self._btn_reject)
        btnbox.clicked.connect(self._btn_clicked)

        layout.addWidget(QLabel('Select Script'), 0, 0)
        layout.addWidget(self.cmb_script, 0, 1)
        layout.addWidget(QLabel('Description'), 1, 0)
        layout.addWidget(self.txt_comment, 1, 1)
        layout.addWidget(btnbox, 2, 1)

        self.dlg.setLayout(layout)

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
        """ Pick import simply shows a list and comments,
            allows the user to pick one and save it

            Note: this doesn't set the values.
            That is done later when popped up OR when they click 'Edit'
        """
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
        center_on_screen(self.dlg)
        self.dlg.exec()

class SheetmusicInfo( MixinFileInfo,
                    MixinPDFInfo,
                    MixinDBInfo,
                    MixinTomlBook):
    """ Pull in information from different sources for file """
    def __init__(self) -> None:
        super().__init__(ImportSettings.get_select())
        self.maid = MixinFieldCleanup()

    def get_sheetmusic_info( self , source_file:str)->dict:
        """Read in all the properties from the file, pdf, and toml

        Args:
            source_file (str): Filename

        Returns:
            dict: key, value of properties
        """
        self.open_pdf(source_file)  # Open first to give time to load
        # Load in file information first
        current_file = self.get_info_from_file(source_file)

        # PDF info
        current_file.update(self.get_info_from_pdf(source_file))

        # TOML PROPERTIES FILE (optional)
        current_file.update(
        self.read_toml_properties_file(source_file))

        # cleanup the filename
        current_file[BookField.NAME] = self.maid.clean_field_value(
            current_file[BookField.NAME])

        # From database
        current_file.update(self.get_info_from_db(source_file))

        return current_file

class UiBaseConvert(MixinFilterFiles,
                    UiRunScript):
    """
        UiBaseConvert contains code to process a list of PDF files and store them
        in the sheetmusic directory. Directory prompts should occur in the derived classes
    """
    # The following are only used to give labels to our return status
    SCRIPT = '_importpdf.sh'

    CONVERT_DEVICE = 'd'
    CONVERT_SOURCE = 's'
    CONVERT_TARGET = 't'
    CONVERT_TYPE = 'y'
    CONVERT_RES = 'r'

    def __init__(self) -> None:
        #pylint: disable=R0902
        super().__init__(ImportSettings.get_select())
        self.add_to_environment(ImportSettings.setting(self.script_file))
        self.dil = Dils()
        self.music_info = SheetmusicInfo()
        self.logger = DbLog('UiBaseConvert')

        self.status = ProgramConstants.RETURN_CANCEL
        self.set_output('text')

        self.book_type = self.dil.prefs.get_value(
            DbKeys.SETTING_FILE_TYPE, DbKeys.VALUE_FILE_TYPE)
        self.page_suffix = self.book_type
        self.music_path = self.dil.prefs.musicdir
        self.base_dir = '~'
        self.data = []
        #pylint: enable=R0902

    def _is_valid_book_directory(self, book_dir: str) -> bool:
        return (os.path.isdir(book_dir) and
                len(fnmatch.filter(os.listdir(book_dir), '*.' + self.page_suffix)) > 0)

    def _fill_in_all_file_info(self, sourcelist: list[str]) -> bool:
        """Take a list of files and gather information.
        The internal self.data is filled in with dictionary entries
        containing details of all the files.

        Args:
            sourcelist (list[str]): list of filenames

        Returns:
            bool: True if should continue
        """
        label_format = '{:4d}: {:<100s} '

        self.data = []
        self.status = ProgramConstants.RETURN_CONTINUE

        if len(sourcelist) > 0:
            count = 0
            status_dlg = UiStatus()
            status_dlg.setWindowTitle('Get infomration from PDF')
            status_dlg.maximum = len(sourcelist)
            for source_file in sourcelist:
                status_dlg.set_value(count)
                count += 1
                status_dlg.title = label_format.format(
                    count, os.path.basename(source_file))

                # Add to the data list
                self.data.append(
                    self.music_info.get_sheetmusic_info( source_file ) )

        return self.status

    def import_files(self) -> list[dict]:
        """Return a list of dictionary entries of
        files to import.

        Returns:
            list[dict]: see ui.MixinFileInfo.get_info_from_file
                for basic field list
        """
        return self.data

    def _setsourcetype(self):
        """Loop through all of the books in self.data
        Check the 'type' field, then source and location.
        If the location ends with 'pdf', set type to a PDF
        otherwise, we think it s a PNG
        """
        for index, book in enumerate(self.data):
            if not BookField.SOURCE_TYPE in book or not book[BookField.SOURCE_TYPE]:
                if book[BookField.SOURCE] == book[BookField.LOCATION] or \
                        (book[BookField.LOCATION]).lower().endswith('pdf'):
                    self.data[index][BookField.SOURCE_TYPE] = DbKeys.VALUE_PDF
                else:
                    self.data[index][BookField.SOURCE_TYPE] = DbKeys.VALUE_PNG

    def add_books_to_library(self) -> bool:
        """ Import PDF imports all the PDF content and re-imports previous bookmarks
            This will only add books if we have a good status and there is some data
            to import
        """

        counter = 0
        if self.status:
            bookmarks = {}
            for loc in self.get_duplicatelist():
                bookmark = self.dil.books.lookup_book_by_column(
                    BookField.SOURCE, loc)
                if bookmark is not None:
                    bookmarks[loc] = bookmark
                self.logger.debug('fDelete current book entry {loc}')
                self.dil.books.delete(BookField.SOURCE, loc)

            if len(self.data) > 0:
                self._setsourcetype()
                plural = ('s' if counter > 1 else '')
                status_dlg = UiStatus()
                status_dlg.setWindowTitle(f"Add book{plural} to library")
                status_dlg.maximum = len(self.data)
                label_format = '{:4d}: {:<100s} '
                for book_data in self.data:
                    if status_dlg.was_canceled():
                        self.status = ProgramConstants.RETURN_CANCEL
                        break

                    status_dlg.set_value(counter)
                    counter += 1
                    status_dlg.title = label_format.format(
                        counter, book_data[BookField.TITLE])
                    # pylint: disable=C0209
                    self.logger.debug('Add new book {} Location {} Type {}'.format(
                        book_data[BookField.BOOK],
                        book_data[BookField.LOCATION],
                        book_data[BookField.SOURCE_TYPE]))
                    # pylint: enable=C0209
                    self.dil.books.delete(
                        BookField.SOURCE, book_data[BookField.SOURCE])
                    new_book = self.dil.books.new_book(**book_data)
                    if book_data[BookField.SOURCE] in bookmarks:
                        for marks in bookmarks[book_data[BookField.SOURCE]]:
                            self.dil.booksmarks.add(
                                new_book[BookField.ID],
                                marks[BookmarkField.NAME],
                                marks[BookmarkField.PAGE]
                            )
                status_dlg.title = f'{counter} Book{plural} added.'
                status_dlg.information = ""
                status_dlg.button_text = 'Close'
                status_dlg.set_value(len(self.data))
                status_dlg.show()
        return (self.status and len(self.data) > 0)

    def update_file_properties(self) -> bool:
        """
            This will go through all of the files and prompt the user
            for properties. It then fills in the information in the data array
        """

        self.status = ProgramConstants.RETURN_CONTINUE
        uiproperties = UiProperties()
        for index, current_file in enumerate(self.data):
            uiproperties.set_properties(current_file)
            if uiproperties.exec() != QDialog.Accepted:
                # Cancel the conversion
                self.status = ProgramConstants.RETURN_CANCEL
                self.data = []
                break

            if len(uiproperties.changes) > 0:
                # UPDATE the data and TOML properties file
                current_file.update(uiproperties.changes)
                self.music_info.write_toml_properties(
                    current_file,
                    current_file[BookField.SOURCE])
                self.data[index] = current_file

        return self.status

    def fix_dup_names(self):
        """
            Each entry in the list contains a book name and a location.
            If the location doesn't exist but the name does then we need to
            fix the names.
        """
        for index, book_entry in enumerate(self.data):
            self.data[index][BookField.NAME] = self.dil.books.get_unique_name(
                book_entry[BookField.NAME])

    def filelist_to_dictionary(self, file_list: list) -> bool:
        """Process files and convert to dictionary
        This wraps calls to functions:
            _fill_in_all_file_info (create dictionaries of attributes)
            update_file_properties: interative file updates
            fix_dup_names: make sure no duplicate names entered.

        Args:
            file_list (list): filename list to process

        Returns:
            bool: True to continue, False to cancel
        """
        if file_list is None or len(file_list) == 0:
            self.status = ProgramConstants.RETURN_CANCEL
        else:
            if self._fill_in_all_file_info(file_list) == ProgramConstants.RETURN_CONTINUE:
                if self.update_file_properties() == ProgramConstants.RETURN_CONTINUE:
                    self.fix_dup_names()
        return self.status

    def _process_conversion_list(self, file_list: list) -> bool:
        """ Process all of the files in the filelist and run the selected script
        This does not import into the database. for that, call add_books_to_library

        N.B. Use processPdfList for PDF->PDF files
    """

        if self.filelist_to_dictionary(file_list) == ProgramConstants.RETURN_CONTINUE:
            for index, entry in enumerate(self.data):
                self.add_variable('SOURCE_FILE', entry[BookField.SOURCE])
                self.add_variable('TARGET_DIR', entry[BookField.NAME])
                book_path = path.join(
                    self.music_path, entry[BookField.NAME])
                if self.run(no_dialog=True) == ProgramConstants.RETURN_CANCEL:
                    break
                if self.is_debug():
                    return ProgramConstants.RETURN_CANCEL
                self.data[index].update({BookField.LOCATION: book_path})
                if self._is_valid_book_directory(book_path):
                    self.data[index][BookField.TOTAL_PAGES] = len(fnmatch.filter(
                        os.listdir(book_path), '*.' + self.book_type))
                else:
                    self.data[index][BookField.TOTAL_PAGES] = 0
                self.reset()
        return self.status

    def _process_pdf_list(self, filelist: list) -> bool:
        if self.filelist_to_dictionary(filelist) == ProgramConstants.RETURN_CONTINUE:
            for _, datum in enumerate(self.data):
                datum[BookField.SOURCE_TYPE] = 'pdf'
                datum[BookField.LOCATION] = datum[BookField.SOURCE]
        return self.status

    def add_final_vars(self):
        pass

    def get_list_of_pdf_files(self) -> list[str]:
        """This will return a complete list of all the pdfs in the system
        NOTE: currently not implementd.

        Raises:
            NotImplementedError: Function not implemented

        Returns:
            list[str]: list of pdf filenames
        """
        self.logger.critical('get_list_of_pdf_files is not implemented')
        raise NotImplementedError("get_list_of_pdf_files is not implemented")

    def process_directory_list(self, data: list[str]) -> bool:
        """ This will process directories and scan for files
        All files will then be processed one-by-one

        Args:
            data (list[str]): directores

        Raises:
            NotImplementedError: Currently not implented

        Returns:
            bool: True if processed, false if not
        """
        del data
        self.logger.critical('process_directory_list is not implemented')
        raise NotImplementedError('process_directory_list is not implemented')

    def process_files(self) -> bool:
        """
            Handle the splitting of file lists and processing. This calls
            'process_directory_list' which should be defined in the derived class
        """
        self.split_selected(self.get_list_of_pdf_files())
        return self.process_directory_list(self.get_filelist())

    def _find_files_in_subdir(self, search_dir:str)->list:
        """ Fill in all the files within the directory and subdirectory """
        file_names = []
        for file_path, _, files in os.walk(search_dir):
            for name in files:
                if name.endswith('.pdf') or name.endswith('.PDF'):
                    file_names.append(os.path.join(file_path, name))
        return file_names

    def get_files_from_directory(self, title: str = 'Select PDF Directory') -> list[str]:
        """ Prompt the user for a directory then find all PDF files """
        file_names = []
        dirname = QFileDialog.getExistingDirectory(
            None,
            title,
            dir=path.expanduser(self.music_info.base_directory())
        )
        if dirname:
            self.music_info.set_base_directory(dirname)
            self._find_files_in_subdir(dirname)
        return file_names

    def get_files(self, title: str = 'Select PDF Files') -> list[str]:
        """ Prompt the user for PDF files and return a list """
        file_names, _ = QFileDialog.getOpenFileNames(
            None,
            title,
            dir=path.expanduser(self.music_info.base_directory()),
            filter="(*.pdf *.PDF)"
        )

        if not file_names:
            file_names = []
        if len(file_names) > 0:
            self.music_info.set_base_directory(PurePath(file_names[0]).parents[0])
        return file_names


class UiConvertFilenames(UiBaseConvert):
    """ This is used to reimport a file, or list of files """

    def __init__(self, location=None):
        super().__init__()
        if location is not None:
            self.process_file(location)

    def process_file(self, location) -> bool:
        """ Pass in either a string or a list for PDF conversion """
        if isinstance(location, list):
            return self.process_directory_list(location)

        return self.process_directory_list([location])

    def get_list_of_pdf_files(self) -> list[str]:
        return self.get_files()

    def process_directory_list(self, data: list[str]) -> bool:
        return self._process_conversion_list(data)


class UiConvertPDFDocuments(UiBaseConvert):
    """ Import and convert a single file """

    def get_list_of_pdf_files(self) -> list[str]:
        return self.get_files()

    def process_directory_list(self, data: list[str]) -> bool:
        return self._process_conversion_list(data)


class UiImportPDFDocuments(UiConvertPDFDocuments):
    """ Import a PDF Document without conversion """

    def get_list_of_pdf_files(self) -> list[str]:
        return self.get_files()

    def process_directory_list(self, data: list[str]) -> bool:
        return self._process_pdf_list(data)


class UiConvertPDFDocumentDirectory(UiBaseConvert):
    """ Import and convert a directory of PDFs"""

    def get_list_of_pdf_files(self) -> list[str]:
        self.get_files_from_directory()

    def process_directory_list(self, data: list[str]) -> bool:
        return self._process_conversion_list(data)


class UiImportPdfDirectory(UiConvertPDFDocumentDirectory):
    """ Import a directory contents of PDFs without conversion to PNGs """

    def get_list_of_pdf_files(self) -> list[str]:
        return self.get_files_from_directory()

    def process_directory_list(self, data: list) -> bool:
        return self._process_pdf_list(data)
