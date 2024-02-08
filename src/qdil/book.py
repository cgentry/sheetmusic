"""
DIL inteface for books

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""


import fnmatch
import os
import shutil

from PySide6.QtWidgets import QMessageBox
from PySide6.QtPdf import QPdfDocument

from qdb.dbbook import DbBook
from qdb.dbbookmark import DbBookmark
from qdb.dbbooksettings import DbBookSettings
from qdb.dbsystem import DbSystem
from qdb.fields.book import BookField
from qdb.fields.bookproperty import BookPropertyField
from qdb.fields.booksetting import BookSettingField
from qdb.keys import DbKeys
from qdb.mixin.tomlbook import MixinTomlBook
from qdb.util import DbHelper
from ui.properties import UiProperties
from util.convert import to_int
from util.pdfclass import PdfDimensions

class DilProperties():
    """ Container for holding general book properties """
    PAGE_PREFIX = None
    PAGE_SUFFIX = None
    FPAGE_SUFFIX = None
    FPAGE_PREFIX = None
    USE_TOML = True
    SETUP_PROPERTIES = True

    def __init__(self):
        if DilProperties.SETUP_PROPERTIES:
            s = DbSystem()
            DilProperties.PAGE_PREFIX = s.get_value(
                DbKeys.SETTING_FILE_PREFIX,
                DbKeys.VALUE_FILE_PREFIX)

            DilProperties.PAGE_SUFFIX = s.get_value(
                DbKeys.SETTING_FILE_TYPE,
                DbKeys.VALUE_FILE_TYPE)

            DilProperties.USE_TOML = \
                s.get_value(DbKeys.SETTING_USE_TOML_FILE, True)
            DilProperties.SETUP_PROPERTIES = False
            del s

            DilProperties.FPAGE_PREFIX = "".join([
                DilProperties.PAGE_PREFIX, "-{0:03d}"])
            DilProperties.FPAGE = "".join(
                [DilProperties.FPAGE_PREFIX,
                 ".",
                 DilProperties.PAGE_SUFFIX])

class DilBook(DbBook):
    """
        DilBook is a data interface layer that will act as the general
        data interface between the program or UI and the database layer

        DilBook handels all the interaction_s for a book and it's ancilliary tables
        ( Bookmark and Notes )

        Values setup:
            GENERAL:

            ALL DOCUMENTS:
                path_location        : Normalised directory location for book
                                      get using filepath()
                path_source          : Normalised directory for book source
                                      get using source_filepath()

            FOR CONVERT+IMPORTED DOCUMENTS:
                self_dset.PAGE_PREFIX         : filename prefix, normally 'page'
                page_suffix         : filename extension, normally 'png'
                format_self_dset.PAGE_PREFIX  : format string, self_dset.PAGE_PREFIX + '-nnn'
                format_page         : format format_self_dset.PAGE_PREFIX + . + page_suffix.
                                      Used to get the full path of the book
                formatBookPage      : Used to get a page location in the directory

            FOR PDF IMPORTED DOCUMENTS:
                self_dset.PAGE_PREFIX         : None
                page_suffix         : suffix of PDF, normally 'pdf'
                format_self_dset.PAGE_PREFIX    : None
                format_page          : None
                book_pageFormat      : same as path_location
    """



    def __init__(self):
        super().__init__()
        self.book = None
        self.book_path_format = None
        self.changes = None
        self.path_location = None
        self.path_source = None

        self.dbooksettings = DbBookSettings()
        self._dset = DilProperties()

        self.clear()


    def _book_xlate(self, book: str | int | dict | None) -> dict:
        if book is None:
            return self.book
        if isinstance(book, int):
            return self.getbook_byid(book)
        if isinstance(book, str):
            return self.getbook_bycolumn(BookField.BOOK, book)
        raise ValueError(f'Invalid type passed: {type(book)}')

    def _book_default_values(self, book_dir: str) -> dict:
        rtn = {}
        image_extension = DbSystem().get_value(DbKeys.SETTING_FILE_TYPE, 'png')
        rtn = {
            BookField.BOOK:  os.path.basename(book_dir),
            BookField.TOTAL_PAGES:
                len(fnmatch.filter(os.listdir(book_dir), '*.' + image_extension)),
            BookField.SOURCE: book_dir,
            BookField.LOCATION: book_dir,
            BookField.NUMBER_STARTS: 1,
            BookField.PUBLISHER: '(import images)',
        }

        rtn[BookField.NUMBER_ENDS] = rtn[BookField.TOTAL_PAGES]
        return rtn

    def _format_pretty_name(self, name):
        ''' Only called when you want to split apart a page name to something nicer'''
        pname = name.capitalize()
        if '-' in name:
            splits = pname.rsplit("-", 1)
            if len(splits) == 2:
                pname = splits[0] + ", page " + str(int(splits[1]))
        return pname

    def _split_parms(self, args: dict):
        """
            Split arguments into book and non-book settings
        """
        settings = {}
        book = {}
        book = {x: args[x] for x in self.column_view if x in args}
        settings = {x: args[x] for x in args if x not in self.column_view}
        return settings, book

    def _check_book(self,
                    book_name: str,
                    open_book: dict | None,
                    on_error=QMessageBox.ButtonRole | None) -> QMessageBox.ButtonRole:
        """
        Check to see if the book_name is valid and contains data.
        If not, it will present a user with a message.
        Return will be a ButtonRole (accept / cancel )
        """
        qmsg_box = QMessageBox()
        qmsg_box.setIcon(QMessageBox.Warning)
        qmsg_box.setInformativeText(book_name)

        rtn = QMessageBox.AcceptRole
        if open_book is None:
            if on_error is not None:
                rtn= on_error
            else:
                qmsg_box.setWindowTitle('Opening sheetmusic')
                qmsg_box.setText("Book is not valid.")
                qmsg_box.exec()
                rtn= qmsg_box.buttonRole(qmsg_box.clickedButton())

        elif open_book[BookField.TOTAL_PAGES] == 0:
            if on_error is not None:
                return on_error
            qmsg_box.setWindowTitle('Opening book')
            qmsg_box.setText("The book is empty.")
            qmsg_box.exec()
            rtn= qmsg_box.buttonRole(qmsg_box.clickedButton())

        elif self.isbookpdf(open_book):
            if not os.path.isfile(open_book[BookField.LOCATION]):
                qmsg_box.setWindowTitle('Opening directory')
                qmsg_box.setText(f"Book is not valid. (No PDF)\n{open_book[BookField.LOCATION]}" )
                qmsg_box.exec()
                rtn= qmsg_box.buttonRole(qmsg_box.clickedButton())
        else:
            if not os.path.isdir(open_book[BookField.LOCATION]):
                qmsg_box.setWindowTitle('Opening directory')
                qmsg_box.setText("Book directory is not valid.")
                qmsg_box.exec()
                rtn= qmsg_box.buttonRole(qmsg_box.clickedButton())
        return rtn

    def _fix_book(self):
        """ Fix any data for the book that may be missing or in error """
        if (BookSettingField.KEY_DIMENSIONS not in self.book or
            self.book[BookSettingField.KEY_DIMENSIONS] is None or
            not isinstance(self.book[BookSettingField.KEY_DIMENSIONS], PdfDimensions) or
                not self.book[BookSettingField.KEY_DIMENSIONS].isSet):
            pdfdoc = QPdfDocument()
            rtn = pdfdoc.load(self.book[BookField.SOURCE])
            if rtn != QPdfDocument.Error.None_:
                return
            dimension = PdfDimensions()
            dimension.checkSizeDocument(pdfdoc)
            self.set_property(BookSettingField.KEY_DIMENSIONS, dimension)

    def open(self, book: str, page=None, file_type="png", on_error=None) -> QMessageBox.ButtonRole:
        """
            Close current book and open new one. Use BookView for data

            Each book read will also include all the BookSettings
        """
        del file_type
        self.close()
        open_book = self.getbook(book=book)

        rtn = self._check_book(book, open_book, on_error)
        if rtn == QMessageBox.AcceptRole:
            self.book = open_book

            self.book.update(
                self.dbooksettings.get_all_settings(self.book[BookField.ID]))
            self.set_paths()
            self.update_read_date(self.book[BookField.BOOK])
            if page is not None:
                self.book[BookField.LAST_READ] = page
            self._fix_book()
        return rtn

    def close(self):
        """ closeBook will clear caches, values, and name paths.
            Values will be saved to the Book or BookSettings tables
        """

        if self.book is not None:
            self.update_read_date(self.book[BookField.BOOK])
            self.changes[BookField.LAST_READ] = self._this_page
            if DbKeys.SETTING_KEEP_ASPECT in self.changes:
                self.changes[DbKeys.SETTING_KEEP_ASPECT] = (
                    1 if self.book[DbKeys.SETTING_KEEP_ASPECT] else 0)
            if self.book[DbKeys.SETTING_PAGE_LAYOUT] is not None:
                self.changes[DbKeys.SETTING_PAGE_LAYOUT] = self.book[DbKeys.SETTING_PAGE_LAYOUT]
            self.write_properties()
        self.clear()

    def is_open(self) -> bool:
        """ Return True if a book is currently open """
        return self.book is not None

    def new_book(self, **kwargs) -> dict:
        """
            This will create a new record in the database and save all the book settings
            The return will be the books record (in dict format)
        """
        bookname = kwargs[BookField.NAME]
        settings, new_book = self._split_parms(kwargs)
        record_id = self.add(**new_book)

        for key, value in settings.items():
            self.dbooksettings.upsert_booksettings(
                book=record_id, key=key, value=value)
        return self.getbook(book=bookname)

    def delete_pages(self, book_location) -> bool:
        """ delete the imported sheetmusic pages directory and contents"""
        if not os.path.isdir(book_location):
            return False

        shutil.rmtree(book_location, ignore_errors=True)
        return True

    def delete(self, key, value) -> bool:
        """ Delete a book based on a datbase search.
            Pass a "key, value" to find and delete the book.
            This will also delete all notes and bookmarks

            If you match more than one book, it will not delete it
        """
        book = self.getbook_bycolumn(key, value)
        book_id = None
        if book is not None and BookField.ID in book:
            book_id = book[BookField.ID]
            DbBook().del_by_column(BookField.ID, book_id)
            self.delete_pages(book[BookField.LOCATION])
            self.dbooksettings.delete_all_values(book=book_id, ignore=True)
            DbBookmark().delete_all(book_id)
        return book_id is not None

    def update_incomplete_books_ui(self):
        """
            This will get a list of books that are 'incomplete'
            and prompt, one-by-one
        """
        ui = UiProperties()
        for book_name in self.get_incomplete_books():
            book = self.getbook(book=book_name)
            ui.set_properties(book)
            ui.exec()
            if ui.is_reject():
                break
            if ui.is_apply():
                if ( BookField.NAME in ui.changes and
                    book[BookField.NAME] != ui.changes[BookField.NAME] ):
                    self.update_name(book[BookField.NAME], ui.changes[BookField.NAME])
                else:
                    ui.changes[BookField.NAME] = book_name
                if len(ui.changes) > 1:
                    self.update(**ui.changes)
        ui.close()
        del ui

    def update_properties(self, change_list: dict) -> bool:
        """ Update properties for a book based on dictionary

            Return True if any changes were made
        """
        self.set_property(BookField.ID, self.book[BookField.ID])
        for key, value in change_list.items():
            self.set_property(key, value)
        if len(self.changes) > 0:
            self.write_properties()
            return True
        return False

    def clear(self):
        """ Clear all the book data that is stored for a book

            Use this after 'close' a book
        """
        self.book = None
        self.changes = {}
        # Set whenever the dirpath alters
        self.book_path_format = ""
        # File information: pages, names
        self.dir_name = ""
        self.path_location = ""
        self.path_source = None
        self._this_page = 0
        self._page_content_start = 0

    @property
    def pagenumber(self) -> int:
        """ Get the current, absolute page number we are on """
        return self._this_page

    @pagenumber.setter
    def pagenumber(self, pnum) -> int:
        '''
        This is the only place you should change the current page number.
        It will accept a number or a string and force the page number to
        a valid range (1 -> end of book)
        '''
        pnum = to_int(pnum, self._this_page)
        if self.is_valid_page(pnum):
            self._this_page = pnum
        else:
            self._this_page = min(max(1, self._this_page),
                                 self.get_property(BookField.TOTAL_PAGES, 999))
        self.book[BookField.LAST_READ] = self._this_page
        return self._this_page

    @property
    def last_pageread(self) -> int:
        """ Return the last page read or 1 if not set"""
        if BookField.LAST_READ in self.book:
            return to_int(self.book[BookField.LAST_READ], 1)
        return 1

    @last_pageread.setter
    def last_pageread(self, page: int):
        self.book[BookField.LAST_READ] = page

    def is_valid_page(self, page: int) -> bool:
        """Determine if a page number is valid

        Args:
            page (int): page number to check

        Returns:
            bool: True if exists, false if not
        """
        return 0 < page <= self.get_property(BookField.TOTAL_PAGES, 999)

    def is_relative_set(self) -> bool:
        """ Returns if a relagive page offset has been set.
            Used by internal book routines
        """
        return self.relative_offset > 1

    @property
    def relative_offset(self) -> int:
        ''' Return the page that content starts on (book)

            This is from the config setting KEY_PAGE_CONTENT
        '''
        return self.get_property(BookField.NUMBER_STARTS, 1)

    @relative_offset.setter
    def relative_offset(self, offset: any) -> bool:
        return self.set_property(BookField.NUMBER_STARTS, max(1, to_int(offset, 1)))

    def is_page_relative(self, from_page=None) -> bool:
        ''' isThisPageRelatve calculates if this page number is within the relative settings'''
        if not self.is_relative_set():
            return False
        return to_int(from_page, self._this_page) >= self.relative_offset

    def page_to_absolute(self, relative_pagenumber: int = None) -> int:
        '''Convert a relative page number to an absolute page number'''
        if relative_pagenumber is None:
            relative_pagenumber = self._this_page
        if not self.is_relative_set():
            return relative_pagenumber
        return relative_pagenumber+self.relative_offset-1

    def page_to_relative(self, from_page=None) -> int:
        '''
            Return the relative page number or the absolute page number

            If the page isn't relative, then it will always return the absolute page
            You can check which is which by using is_page_relative()
        '''
        rel_page = None
        from_page = to_int(from_page, self._this_page)
        if self.is_page_relative(from_page):
            offset = self.relative_offset - 1
            rel_page = max(0, (from_page - offset))
        return rel_page if rel_page and rel_page > 0 else from_page

    def count(self) -> int:
        """ Return the total number of pages in a book """
        return self.get_property(BookField.TOTAL_PAGES, 0)

    def get_last_page_shown(self) -> int:
        """ Get the last page that can be shown """
        if self.get_property(BookPropertyField.LAYOUT, system=True) == DbKeys.VALUE_PAGES_SIDE_2:
            return max(self.get_property(BookField.TOTAL_PAGES)-1, 1)
        return self.get_property(BookField.TOTAL_PAGES)

    def get_first_page_shown(self) -> int:
        """ Alias function: returns the relative offset for the book"""
        return self.relative_offset

    #  ====================================
    #        FILE AND PATH METHODS
    #  ====================================
    #

    def filepath(self, book_path: str = None) -> str:
        """ Return the bookpath for this book or the normalised bookpath"""
        if book_path is None:
            return self.path_location
        return os.path.normpath(book_path)

    def source_filepath(self) -> str | None:
        """ Return the source path for this book (normalised)"""
        return self.path_source()

    def page_filepath(self, page: str | int, required=True) -> str | None:
        """ Return the page's path. If the file doesn't exist, None is returned"""
        image_path = (self.book[BookField.LOCATION] if self.is_pdf(
        ) else self.book_path_format.format(to_int(page)))

        if not required or os.path.isfile(image_path):
            return image_path
        return None

    def set_paths(self):
        """
        Split the directory path up into paths used by the Book class

        take a directory path (e.g. /users/yourname/sheetmusic/mybook) and split it up.
        The directory (/users/yourname/sheetmusic/mybook) is the book directory
        the first part (..../sheetmusic) is the home to all your books
        The second part (mybook) is the name of the book
        We then get format_self_dset.PAGE_PREFIX (the page plus three digit extension)
        and the complete path formatter string
        """

        self.path_location = os.path.normpath(self.book[BookField.LOCATION])
        self.path_source = os.path.normpath(self.book[BookField.SOURCE])

        self.book_path_format = os.path.join(
            self.path_location, self._dset.FPAGE )

    #  ====================================
    #          GENERAL METHODS
    #  ====================================
    #

    def recent(self) -> list:
        """ Get the recent books opened, in date/time order.
        Number returned is defined in System table"""
        return super().get_recent(DbSystem().get_value(DbKeys.SETTING_MAX_RECENT_SIZE, 10))

    #  ====================================
    #           PROPERTY METHODS
    #  ====================================
    #

    def get_properties(self) -> dict | None:
        """ Return all of the properties for the book """
        return self.book

    def get_property(self, key: str, default=None, system=False) -> str:
        """ Get one property from the book if set
            If system is True, it will get the system value if the book value isn't set
            default will be returned if there is no value to return
        """
        if self.book is None or key not in self.book:
            if system:
                return DbSystem().get_value(key, default)
            return default
        return self.book[key]

    def set_property(self, key: str, value=None) -> bool:
        """
            Set property for both the change list and the book
            If anything (other than name) is changed, return True
        """
        if key not in self.book or self.book[key] != value:
            self.changes[key] = value
            self.book[key] = value
            return True
        return False

    @property
    def title(self) -> str:
        """ Convenience function. Return book name"""
        return self.get_property(BookField.NAME)

    @title.setter
    def set_title(self, new_title: str) -> bool:
        return self.set_property(BookField.NAME, new_title)

    @property
    def keep_aspect_ratio(self) -> bool:
        """ Return the book aspect ratio stored or True if not set """
        return self.get_property(BookField.ASPECT_RATIO, 1) == 1

    @keep_aspect_ratio.setter
    def keep_aspect_ratio(self, aspect: bool) -> bool:
        new_aspect = 1 if aspect else 0
        return self.set_property(BookField.ASPECT_RATIO, new_aspect)

    def renderbookpdf(self, book: dict | int | str | None = None) -> bool:
        """ Determine if a pf book should be rendered as a PDF. (return false if not a PDF)
            book can be:
                None  - use current book
                int   - lookup book by record ID
                str   = book name
                dict  - a book retrieved by the dbbook class
        """
        if not isinstance(book, dict):
            book = self._book_xlate(book)
        if self.isbookpdf(book):
            return self.dbooksettings.get_bool(
                book=book,
                key=DbKeys.SETTING_RENDER_PDF,
                fallback=True,
                default=DbKeys.VALUE_DEFAULT_RENDER_PDF)
        return False

    def isbookpdf(self, book: dict | int | str | None = None) -> bool:
        """ Determine if book is a PDF
            The book must exist and the dictionary must have values for locations
            The Book is not a PDF iflocation points to a directory
                (images are stored in a directory)
            The book is a pdf if the location extension is 'pdf'
        """
        if not isinstance(book, dict):
            book = self._book_xlate(book)
        if BookField.SOURCE not in book or BookField.LOCATION not in book:
            return False
        if os.path.isdir(book[BookField.LOCATION]):
            return False
        return True

    def is_pdf(self) -> bool:
        """ Return True if currently open book is a PDF """
        return self.isbookpdf(self.book)

    def get_filetype(self) -> str:
        """ Return the type of book to process (png or pdf)"""
        return (DbKeys.VALUE_PDF if self.is_pdf() else self._dset.PAGE_SUFFIX)

    def is_png(self) -> bool:
        """ Return True if book is a png. """
        return not self.is_pdf()

    def get_id( self, book=str|int|dict|None)->int:
        """ Return either the current book id or look one up"""
        if book is None and self.is_open():
            return self.book[ BookField.ID ]
        return super().lookup_book_id( book )

    def write_properties(self):
        """
            We have several differenty keystores: some in Book and
            some in BookSettings. We need to know where to put it.
        """
        book_id = self.get_id()
        db = {}
        for key, value in self.changes.items():
            if key not in self.column_view:
                self.dbooksettings.upsert_booksettings(
                    book_id, key, value, ignore=True)
            else:
                db[key] = value
        if len(db) > 0:
            db[BookField.ID] = book_id
            self.book.update(db)
        self.changes = {}

    def import_one_book(self, book_dir=dir):
        """
        This takes a directory of converted PNG images and adds to the database

        if there is a file called 'properties.cfg' in the directory it used to set
        values for the book This is a 'toml' file and ONLY these keywords are used.
            book = "Name of book"
            genre = "Genre name"
            composer = "composer name"
            numbering_starts = "Start page offset"
            author = "Author name"
            publisher = "Publisher (usually a program)"

        Returns:
            book:   default name stored in database
            pages:  Total number of images found
            error:  String that contains error message or None if no error
        """
        book_info = {}
        error_msg = None

        if not book_dir:
            return (book_info, "No directory passed.")

        basedir = os.path.basename(book_dir)

        if self.is_location(book_dir) or self.is_source(book_dir):
            return (book_info, f'Book already in library: {basedir}')

        if not os.path.isdir(book_dir):
            return (book_info, f"Location '{book_dir}' is not a directory")

        book_info = self._book_default_values(book_dir)
        if book_info[BookField.TOTAL_PAGES] == 0:
            return (book_info, "No pages for book")
        if self._dset.USE_TOML:
            book_info.update(MixinTomlBook().read_toml_properties(book_dir))

        rec_id = self.add(**book_info)
        book_info[BookField.ID] = rec_id
        return (book_info, error_msg)

    def import_directory(self, location=dir):
        """
            Import contents of a complete directory

            Return is:
                bool :       Error occured during add
                list:        list dictionaries containing added book info
                ltr:         message to return to user
        """
        added_records = []
        if location is None or location == "":
            return (False, added_records, "Location is empty")
        if not os.path.isdir(location):
            return (False,
                    added_records,
                    f"Location '{location}' is not a directory")

        for book_dir in [f.path for f in os.scandir(location) if f.is_dir()]:
            (book_info, error_msg) = self.import_one_book(book_dir)
            if error_msg is not None:
                return (False, added_records, error_msg)
            added_records.append(book_info)
        added_message = "Records added" if len(
            added_records) > 0 else "No new records found"
        return (True, added_records, added_message)


    def get_unique_name(self, name: str) -> str:
        """
            If you are adding a book but the name is there but
            its source is different, this will give you a unique name

            You should also check to see if the book is already added by
            checking with 'is_source()'. If it is, delete the entry and addNew
        """
        if self.is_book(name):
            pattern = f'{name}%'
            query = DbHelper.bind(DbHelper.prep(
                "SELECT count(*) as count FROM Book WHERE book LIKE ?"), pattern)
            if query.exec() and query.next():
                count = query.value(0)
            else:
                count = 0
            self._check_error(query)
            query.finish()
            del query
            if count is not None and count > 0:  # shouldn't have gotten here!
                return f"{name} [{1+int(count)}]"
        return name
