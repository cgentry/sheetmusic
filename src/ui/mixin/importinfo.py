"""
Mixins : Information

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from datetime import datetime
from pathlib import PurePath
from typing import Callable
import os
import pathlib

from PySide6.QtWidgets import (QMessageBox)
try:
    from PySide6.QtPdf import QPdfDocument
    IMPORT_INFO_HAS_QPDF_DOCUMENT = True
except ImportError:
    IMPORT_INFO_HAS_QPDF_DOCUMENT = False

from qdb.fields.book import BookField
from qdb.fields.bookproperty import BookPropertyField
from qdb.fields.booksetting import BookSettingField
from qdb.dbbook import DbBook
from qdb.keys import DbKeys
from ui.selectitems import SelectItems


class MixinFileInfo:
    """
        The MIXIN contains general routines for importing content into the system
        from the file itself (a PDF)
        It does not insert or convert content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_base_directory(self, basedir: str):
        """ Set the base directory for importing """
        if basedir is not None:
            self.base_dir = basedir

    def base_directory(self) -> str:
        """ Return base directory. Defaults in DbKeys """
        return (self.base_dir if self.base_dir else DbKeys.VALUE_LAST_IMPORT_DIR)

    def get_info_from_file(self, source_file: str) -> dict:
        """Define dictionary for a file and fill in defaults.
        Information should be overridden by PDF, then DB

        Args:
            source_file (str): Name of source file

        Returns:
            dict: name, source, number_starts, composer, genre
                  fileCreated, fileModified, pdfCreated,
                  pdfModified, update, and layout.
                  (Additional fields may be added)
        """
        created = datetime.fromtimestamp(
            os.path.getctime(source_file)).isoformat(' ')
        modified = datetime.fromtimestamp(
            os.path.getmtime(source_file)).isoformat(' ')
        return {
            BookField.NAME:              PurePath(source_file).stem,
            BookField.SOURCE:            source_file,
            BookField.NUMBER_STARTS:      1,
            BookField.COMPOSER:          DbKeys.VALUE_DEFAULT_COMPOSER,
            BookField.GENRE:             DbKeys.VALUE_DEFAULT_GENRE,
            BookField.FILE_CREATED:       created,
            BookField.FILE_MODIFIED:      modified,
            BookField.PDF_CREATED:        created,
            BookField.PDF_MODIFIED:       modified,
            BookPropertyField.LAYOUT:    DbKeys.VALUE_PAGES_SINGLE,
        }

    def _print_data(self, label: str, data: dict):
        """ Debug routine for use when testing out routines."""
        print(label)
        for key in sorted(data.keys()):
            print(f"\tKEY: '{key:30s}' VALUE: '{data[key]}'")

    def check_for_processed_files(self, file_list: list) -> tuple[list, list]:
        '''
            Check the file_list for processed files and return two lists:
            all files to be processed and the duplicate files to be reprocessed

            file_list is the list of file(s) selected form import (PDFs)
            Check the database to see if they exist (sources_exist) and
            present the user a list of books. Those are added back to the
            file_list if they are selected. If not, they are put in the duplicates_kept
        '''
        duplist = DbBook().sources_exist(file_list)
        duplicates_kept = []

        if len(duplist) > 0:
            select_title = f"{len(duplist)} Books already processed" \
                f"({len(file_list)} books selected)"
            # First, remove duplicates from filelist
            file_list = [src for src in file_list if src not in duplist]
            sim = SelectItems(select_title,
                              "Select files to reprocess")
            _dup_dictionary = {os.path.basename(var): var for var in duplist}
            sim.set_data(_dup_dictionary)
            sim.set_button_text("Include Selected Files",
                                "Skip All Reprocessed Files")
            rtn = sim.exec()
            # Now, merge in selected IF they clicked 'Include'
            if rtn == QMessageBox.Accepted:
                _dup_dictionary = sim.get_checked_list()
                if len(_dup_dictionary) > 0:
                    duplicates_kept = list(_dup_dictionary.values())
                    file_list.extend(list(duplicates_kept))

        return file_list, duplicates_kept


class MixinPDFInfo:
    """ Read document information from the PDF File

        This uses the internal QPdfDocument library functions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_pdf_library(self) -> bool:
        """ Return status of QPdfDocument library """
        return IMPORT_INFO_HAS_QPDF_DOCUMENT

    def open_pdf(self, pdf_document: str):
        """MixinPDFInfo: create a QPdfDocument instance and load the document file"""
        self.pdf_document = QPdfDocument()
        self.pdf_document.load(pdf_document)

    def _calculate_pdf_largest_size(self):
        """ Figure out what is the largest page in pdf """
        _width = 0
        _height = 0

        for page in range(self.pdf_document.pageCount()):
            pdf_point_size = self.pdf_document.pagePointSize(page)
            if pdf_point_size is not None:
                _width = max(pdf_point_size.width(), _width)
                _height = max(pdf_point_size.height(), _height)
        return _width, _height

    def get_info_from_pdf(self, sourcefile: str = None) -> dict:
        """ Fetch PDF info and return in dictionary """
        if self.pdf_document is None:
            if sourcefile is None:
                raise ValueError('No PDF document opened')
            self.open_pdf(sourcefile)

        def set_book_value(key: str, value):
            if value:
                pdf_info[key] = str(value).strip()

        def set_book_meta(key: str, meta_key):
            set_book_value(
                key, str(self.pdf_document.metaData(meta_key)).strip())

        pdf_info = {
            BookField.TOTAL_PAGES: self.pdf_document.pageCount(),
            BookField.NUMBER_ENDS: self.pdf_document.pageCount(),
        }
        set_book_meta(BookField.AUTHOR, QPdfDocument.MetaDataField.Author)
        set_book_meta(BookField.NAME, QPdfDocument.MetaDataField.Title)
        set_book_meta(BookField.PUBLISHER, QPdfDocument.MetaDataField.Producer)

        set_book_value(BookField.PDF_CREATED, self.pdf_document.metaData(
            QPdfDocument.MetaDataField.CreationDate).toString('yyyy-MM-dd HH:mm:ss'))
        set_book_value(BookField.PDF_MODIFIED, self.pdf_document.metaData(
            QPdfDocument.MetaDataField.ModificationDate).toString('yyyy-MM-dd HH:mm:ss'))

        if BookField.NAME not in pdf_info or pdf_info[BookField.NAME] == '':
            pdf_info[BookField.NAME] = str(
                pathlib.Path(sourcefile).stem).strip()
        pdf_info[BookSettingField.KEY_MAX_W], pdf_info[BookSettingField.KEY_MAX_H] = \
            self._calculate_pdf_largest_size()

        self.pdf_document.close()
        self.pdf_document = None
        return pdf_info


class MixinDBInfo:
    """ Read document information from the database, if previously imported """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_info_from_db(self, source_file: str) -> dict:
        """ This will read data from the database if the file has been imported before
            This will override all of the data set from the PDF as it's already been cleaned up.
        """
        def get_book_field(target: str, field: str):
            if field in book and book[field]:
                current_file[target] = book[field]

        current_file = {}
        book = DbBook().getbook_bycolumn(BookField.SOURCE, source_file)
        if book is not None:
            get_book_field(BookField.NAME,          BookField.NAME)
            get_book_field(BookField.TOTAL_PAGES,    BookField.TOTAL_PAGES)
            get_book_field(BookField.COMPOSER,      BookField.COMPOSER)
            get_book_field(BookField.GENRE,         BookField.GENRE)
            get_book_field(BookField.NUMBER_STARTS,  BookField.NUMBER_STARTS)
            get_book_field(BookField.NUMBER_ENDS,    BookField.NUMBER_ENDS)

        return current_file


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
        self.file_list = []  # list of filename strings
        self.duplicate_list = []
        self.ignored_list = []

    def get_filelist(self) -> list[str]:
        """ Return a list of files that are to be processed"""
        return self.file_list

    def get_duplicatelist(self) -> list[str]:
        """ List of files that are reprocessed (duplicates)"""
        return self.duplicate_list

    def get_ignored_list(self) -> list[str]:
        """ List of files that are selected but not being processed """
        return self.ignored_list

    def _apply_filter(self, reprocess_list: list[str]):
        """ split the file_list into 3 based on what user wants to reprocess.

        There are three lists:
        1) file_list :      all the files that should be processed
        2) duplicate_list:  Duplicates that are to be processed (also in file_list)
        3) ignored_files:   Files that will be ignored
           (and not in file_list or duplicate_list)

        These are lists that point to BookField.SOURCE
        """

        self.duplicate_list = [
            proc for proc in reprocess_list if proc in self.file_list]
        self.ignored_list = [
            proc for proc in self.ignored_list
            if proc not in self.duplicate_list and
            proc in self.file_list]
        self.file_list = [
            proc for proc in self.file_list if proc not in self.ignored_list]

    def _reprocess_dialog(self, duplicate_list: list[str]) -> list[str]:
        """ Prompt the user for what files to re-process.
        Return a list of files selected to be reprocessed"""
        if len(duplicate_list) == 1:
            qmsg_box = QMessageBox()
            qmsg_box.setMinimumWidth(400)
            qmsg_box.setIcon(QMessageBox.Question)
            qmsg_box.setWindowTitle('Import Book')
            qmsg_box.setInformativeText(
                f'{os.path.basename( duplicate_list[0])}')
            qmsg_box.setText('Reprocess book?')
            qmsg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            rtn = qmsg_box.exec()
            return duplicate_list if rtn == QMessageBox.Yes else []

        # ELSE: more than one duplicate
        select_title = f'{len(duplicate_list)} Books already processed'
        sim = SelectItems(select_title,
                          "Select files to reprocess")
        _dup_dictionary = {os.path.basename(
            var): var for var in duplicate_list}
        sim.set_data(_dup_dictionary)
        sim.set_button_text("Reprocess Selected Files",
                            "Skip All Processed Files")
        rtn = sim.exec()

        # Get the list of files they want reprocessed
        return sim.get_checked_listvalues()

    def _confirm_dialog(self, file_list: list[str]) -> list:
        sim = SelectItems("Books To Process",
                          "Confirm files to process")
        file_dictionary = {os.path.basename(var): var for var in file_list}
        sim.set_data(file_dictionary)
        sim.set_button_text("Process Selected Files",
                            "Skip All Files")
        sim.exec()

        # Get the list of files they want reprocessed
        return sim.get_checked_listvalues()

    def split_selected(self,
                       selected_files: list[str],
                       check_db_for_source: Callable[[list], list] = None,
                       filter_dialog: Callable[[list], list] = None) -> tuple[list[str], list[str], list[str]]:
        '''
            Split a file list into three:
            * file_list: list of files to be processed (from a openFile dialog)
            * duplicate_list: Duplicate files (also are in file_list)
            * ignored_files:  files removed from file_list

            selected_files is the list of file(s) selected for import (PDFs)
            check_db_for_source is a routine to
                check the database if the source is in the location
            filter_dialog is the dialog to get user selected files for reprocessing

        '''
        if filter_dialog is None:
            filter_dialog = self._reprocess_dialog
        if check_db_for_source is None:
            check_db_for_source = DbBook().sources_exist

        self.file_list = selected_files
        self.duplicate_list = []
        self.ignored_list = check_db_for_source(selected_files)

        if len(self.ignored_list) > 0:
            # duplicates-to-process from list of files-to-ignore
            self.duplicate_list = filter_dialog(self.ignored_list)
        self._apply_filter(self.duplicate_list)

        return self.file_list, self.duplicate_list, self.ignored_list

    def confirm_selected(self, selected_files: list[str]) -> list[str]:
        """ Check the selected files and return the list
        NOTE: not currently implemented """
        return selected_files
