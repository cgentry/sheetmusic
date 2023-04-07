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

from qdb.dbbook import DbBook
from qdb.dbbooksettings import DbBookSettings
from qdb.dbbookmark import DbBookmark
from qdb.dbsystem import DbSystem
from qdb.keys import DbKeys, BOOK, BOOKPROPERTY, BOOKSETTING
from util.convert import toInt
from PySide6.QtWidgets import QMessageBox
from PySide6.QtPdf import QPdfDocument
from util.pdfclass import PdfDimensions

import fnmatch
import os
import shutil
from typing import Tuple


class DilBook(DbBook):
    """
        DilBook is a data interface layer that will act as the general
        data interface between the program or UI and the database layer

        DilBook handels all the interactions for a book and it's ancilliary tables
        ( Bookmark and Notes )

        Values setup:
            GENERAL:
                numberRecent    : Number of recent books for menu

            ALL DOCUMENTS:
                locationpath        : Normalised directory location for book
                                      get using filepath()
                sourcepath          : Normalised directory for book source
                                      get using source_filepath()

            FOR CONVERT+IMPORTED DOCUMENTS:
                page_prefix         : filename prefix, normally 'page'
                page_suffix         : filename extension, normally 'png'
                formatPagePrefix    : format string, page_prefix + '-nnn'
                formatPage          : format name that consists of formatPagePrefix + . + page_suffix.
                                      Used to get the full path of the book
                formatBookPage      : Used to get a page location in the directory

            FOR PDF IMPORTED DOCUMENTS:
                page_prefix         : None
                page_suffix         : suffix of PDF, normally 'pdf'
                formatPagePrefix    : None
                formatPage          : None
                bookPageForamt      : same as locationpath
    """

    def __init__(self):
        super().__init__()
        self.dbooksettings = DbBookSettings()
        s = DbSystem()
        self.page_prefix = s.getValue(
            DbKeys.SETTING_FILE_PREFIX, DbKeys.VALUE_FILE_PREFIX)
        self.page_suffix = s.getValue(
            DbKeys.SETTING_FILE_TYPE,   DbKeys.VALUE_FILE_TYPE)
        self.numberRecent = s.getValue(DbKeys.SETTING_MAX_RECENT_SIZE, 10)
        self._use_toml_file = s.getValue(DbKeys.SETTING_USE_TOML_FILE, True)
        del s

        self.clear()

    def _formatPrettyName(self, name):
        ''' Only called when you want to split apart a page name to something nicer'''
        pname = name.capitalize()
        if '-' in name:
            splits = pname.rsplit("-", 1)
            if len(splits) == 2:
                pname = splits[0] + ", page " + str(int(splits[1]))
        return pname

    def _splitParms(self, args: dict):
        """
            Split arguments into book and non-book settings
        """
        settings = {}
        book = {}
        book = {x: args[x] for x in self.columnView if x in args}
        settings = {x: args[x] for x in args if x not in self.columnView}
        return settings, book

    def isPDF(self) -> bool:
        return (DbKeys.VALUE_PDF == self.book[BOOK.source_type])

    def isPNG(self) -> bool:
        return not self.isPDF()

    def setPaths(self):
        """
        Split the directory path up into paths used by the Book class

        take a directory path (e.g. /users/yourname/sheetmusic/mybook) and split it up.
        The directory (/users/yourname/sheetmusic/mybook) is the book directory
        the first part (..../sheetmusic) is the home to all your books
        The second part (mybook) is the name of the book
        We then get formatPagePrefix (the page plus three digit extension)
        and the complete path formatter string
        """

        self.locationpath = os.path.normpath(self.book[BOOK.location])
        self.sourcepath = os.path.normpath(self.book[BOOK.source])
        self.formatPagePrefix = "".join([self.page_prefix, "-{0:03d}"])
        self.formatPage = "".join(
            [self.formatPagePrefix, ".", self.page_suffix])
        self.bookPathFormat = os.path.join(self.locationpath, self.formatPage)

    def getFileType(self) -> str:
        """ Return the type of book to process (png or pdf)"""
        return (DbKeys.VALUE_PDF if self.ispdf() else self.page_suffix)

    def ispdf(self, book: dict = None) -> bool:
        if book is None:
            book = self.book
        return (isinstance(book, dict) and BOOK.source_type in book and book[BOOK.source_type] == DbKeys.VALUE_PDF)

    def _check_book(self, book_name: str, open_book: dict | None, onError=QMessageBox.ButtonRole | None) -> QMessageBox.ButtonRole:
        """
        Check to see if the book_name is valid and contains data. If not, it will present a user with a message. 
        Return will be a ButtonRole (accept / cancel )
        """
        dlg = QMessageBox()
        dlg.setIcon(QMessageBox.Warning)
        dlg.setInformativeText(book_name)

        if open_book == None:
            if onError is not None:
                return onError

            dlg.setWindowTitle('Opening sheetmusic')
            dlg.setText("Book is not valid.")
            dlg.exec()
            return dlg.buttonRole(dlg.clickedButton())

        if open_book[BOOK.totalPages] == 0:
            if onError is not None:
                return onError
            dlg.setWindowTitle('Opening book')
            dlg.setText("The book is empty.")
            dlg.exec()
            return dlg.buttonRole(dlg.clickedButton())

        if self.ispdf(open_book):
            if not os.path.isfile(open_book[BOOK.location]):
                dlg.setWindowTitle('Opening directory')
                dlg.setText("Book is not valid. (No PDF)\n{}".format(
                    open_book[BOOK.location]))
                dlg.exec()
                return dlg.buttonRole(dlg.clickedButton())
        else:
            if not os.path.isdir(open_book[BOOK.location]):
                dlg.setWindowTitle('Opening directory')
                dlg.setText("Book directory is not valid.")
                dlg.exec()
                return dlg.buttonRole(dlg.clickedButton())

        return QMessageBox.AcceptRole

    def _fix_book( self ):
        """ Fix any data for the book that may be missing or in error """
        if ( BOOKSETTING.dimensions not in self.book or 
            self.book[ BOOKSETTING.dimensions] is None or 
            not isinstance( self.book[BOOKSETTING.dimensions], PdfDimensions)  or
            not self.book[BOOKSETTING.dimensions].isSet ):
                pdfdoc = QPdfDocument()
                rtn = pdfdoc.load( self.book[ BOOK.source ])
                if rtn != QPdfDocument.Error.None_:
                    return
                dimension = PdfDimensions()
                dimension.checkSizeDocument( pdfdoc )
                self.set_property(BOOKSETTING.dimensions , dimension )

    def open(self, book: str, page=None, fileType="png", onError=None) -> QMessageBox.ButtonRole:
        """
            Close current book and open new one. Use BookView for data

            Each book read will also include all the BookSettings
        """
        self.close()
        open_book = self.getBook(book=book)

        rtn = self._check_book(book, open_book, onError)
        if rtn == QMessageBox.AcceptRole:
            self.book = open_book
            
            self.book.update( self.dbooksettings.getAllSetting( self.book[BOOK.id]))
            self.setPaths()
            self.updateReadDate(self.book[BOOK.book])
            if page is not None:
                self.book[BOOK.lastRead] = page
            self._fix_book()
        return rtn

    def close(self):
        """ closeBook will clear caches, values, and name paths. 
            Values will be saved to the Book or BookSettings tables
        """

        if self.book is not None:
            self.updateReadDate(self.book[BOOK.book])
            self.changes[BOOK.lastRead] = self._thisPage
            if DbKeys.SETTING_KEEP_ASPECT in self.changes:
                self.changes[DbKeys.SETTING_KEEP_ASPECT] = (
                    1 if self.book[DbKeys.SETTING_KEEP_ASPECT] else 0)
            if self.book[DbKeys.SETTING_PAGE_LAYOUT] is not None:
                self.changes[DbKeys.SETTING_PAGE_LAYOUT] = self.book[DbKeys.SETTING_PAGE_LAYOUT]
            self.write_properties()
            self.clearCache()
        self.clear()

    def isOpen(self) -> bool:
        return (self.book is not None)

    def newBook(self, **kwargs) -> dict:
        """
            This will create a new record in the database and save all the book settings
            The return will be the books record (in dict format)
        """
        bookname = kwargs[BOOK.name]
        settings, newBook = self._splitParms(kwargs)
        recId = self.add(**newBook)

        for key, value in settings.items():
            self.dbooksettings.upsertBookSetting(
                id=recId, key=key, value=value)
        return self.getBook(book=bookname)

    def delete_pages(self, book_location) -> bool:
        """ delete the imported sheetmusic pages directory and contents"""
        if not os.path.isdir(book_location):
            return False

        shutil.rmtree(book_location, ignore_errors=True)
        return True

    def delete(self, key, value) -> bool:
        """ Delete a book based on a datbase search. 
            Pass a "key, value" to find and delete the book. This will also delete all notes and bookmarks

            If you match more than one book, it will not delete it
        """
        book = self.getBookByColumn(key, value)
        id = None
        if book is not None and BOOK.id in book:
            id = book[BOOK.id]
            self.delbycolumn(BOOK.id, id)
            self.delete_pages(book[BOOK.location])
            DbBookSettings().deleteAllValues(id, ignore=True)
            DbBookmark().delete_all(id)
        return id is not None

    def updateIncompleteBooksUI(self):
        """
            This will get a list of books that are 'incomplete'
            and prompt, one-by-one
        """
        from ui.properties import UiProperties
        ui = UiProperties()
        for bookName in self.getIncompleteBooks().keys():
            book = self.getBook(book=bookName)
            ui.set_properties(book)
            ui.exec()
            if ui.isReject():
                break
            if ui.isApply():
                if BOOK.name in ui.changes and book[BOOK.name] != ui.changes[BOOK.name]:
                    self.updateName(book[BOOK.name], ui.changes[BOOK.name])
                else:
                    ui.changes[BOOK.name] = bookName
                if len(ui.changes) > 1:
                    self.update(**ui.changes)
        ui.close()
        del ui
        return

    def clear(self):
        """ Clear all the book data that is stored for a book

            Use this after 'close' a book
        """
        self.book = None
        self.changes = {}
        # Set whenever the dirpath alters
        self.bookPathFormat = ""
        self.formatPagePrefix = ""
        # File information: pages, names
        self.dirName = ""
        self.locationpath = ""
        self.sourcepath = None
        self._thisPage = 0
        self._page_content_start = 0
    
    """
            PAGE NUMBER ROUTINES
    """
    @property
    def pagenumber(self) -> int:
        """ Get the current, absolute page number we are on """
        return self._thisPage

    @pagenumber.setter
    def pagenumber(self, pnum) -> int:
        '''
        This is the only place you should change the current page number.
        It will accept a number or a string and force the page number to 
        a valid range (1 -> end of book)
        '''
        pnum = toInt(pnum, self._thisPage)
        if self.isValidPage(pnum):
            self._thisPage = pnum
        else:
            self._thisPage = min(max(1, self._thisPage),
                                 self.get_property(BOOK.totalPages, 999))
        self.book[BOOK.lastRead] = self._thisPage
        return self._thisPage

    @property
    def lastPageRead(self) -> int:
        """ Return the last page read or 1 if not set"""
        if BOOK.lastRead in self.book:
            return toInt(self.book[BOOK.lastRead], 1)
        return 1

    @lastPageRead.setter
    def lastPageRead(self, page: int):
        self.book[BOOK.lastRead] = page

    def isValidPage(self, page: int) -> bool:
        return (page > 0 and page <= self.get_property(BOOK.totalPages, 999))
    
    def isRelativeSet(self) -> bool:
        """ Returns if a relagive page offset has been set.
            Used by internal book routines
        """
        return (self.relative_offset > 1)

    @property
    def relative_offset(self) -> int:
        ''' Return the page that content starts on (book)

            This is from the config setting KEY_PAGE_CONTENT
        '''
        return self.get_property(BOOK.numberStarts, 1)

    @relative_offset.setter
    def relative_offset(self, offset: any) -> bool:
        return self.set_property(BOOK.numberStarts, max(1, toInt(offset, 1)))

    def isPageRelative(self, fromPage=None) -> bool:
        ''' isThisPageRelatve calculates if this page number is within the relative settings'''
        if not self.isRelativeSet():
            return False
        return (toInt(fromPage, self._thisPage) >= self.relative_offset)

    def page_to_absolute(self, relative_pagenumber: int = None) -> int:
        '''Convert a relative page number to an absolute page number'''
        if relative_pagenumber is None:
            relative_pagenumber = self._thisPage
        if not self.isRelativeSet():
            return relative_pagenumber
        return relative_pagenumber+self.relative_offset-1

    def page_to_relative(self, fromPage=None) -> int:
        '''
            Return the relative page number or the absolute page number

            If the page isn't relative, then it will always return the absolute page
            You can check which is which by using isPageRelative()
        '''
        relPage = None
        fromPage = toInt(fromPage, self._thisPage)
        if self.isPageRelative(fromPage):
            offset = self.relative_offset - 1
            relPage = max(0, (fromPage - offset))
        return relPage if relPage and relPage > 0 else fromPage

    def count(self) -> int:
        """ Return the total number of pages in a book """
        return self.get_property(BOOK.totalPages, 0)

    def getLastPageShown(self) -> int:
        if self.get_property(BOOKPROPERTY.layout, system=True) == DbKeys.VALUE_PAGES_SIDE_2:
            return max(self.get_property(BOOK.totalPages)-1, 1)
        return self.get_property(BOOK.totalPages)

    def getFirstPageShown(self) -> int:
        """ Alias function: returns the relative offset for the book"""
        return self.relative_offset

    """ END OF PAGE ROUTINES"""

    def filepath(self, bookPath: str = None) -> str:
        """ Return the bookpath for this book or the normalised bookpath"""
        if bookPath is None:
            return self.locationpath
        return os.path.normpath(bookPath)

    def source_filepath(self) -> str | None:
        """ Return the source path for this book (normalised)"""
        return self.sourcepath()

    def page_filepath(self, page: str | int, required=True) -> str | None:
        """ Return the page's path. If the file doesn't exist, None is returned"""
        imagePath = (self.book[BOOK.location] if self.isPDF(
        ) else self.bookPathFormat.format(toInt(page)))

        if not required or os.path.isfile(imagePath):
            return imagePath
        return None

    def clearCache(self):
        # self.tcache.cache_clear()
        pass

    def getRecent(self):
        self.numberRecent = DbSystem().getValue(DbKeys.SETTING_MAX_RECENT_SIZE, 10)
        return super().getRecent(limit=self.numberRecent)

    def getBooknameByID(self, id: int = None) -> str:
        """
            This will get the book name form the database rather than
            pulling it from our local storage
        """
        if id is None:
            id = self.getID()
        book = self.getBookById(id)
        if book is None:
            raise RuntimeError("No book found for ID: {}".format(id))
        return book[BOOK.name]


    def getNote(self) -> str:
        return self.get_property(BOOK.note)


    """
        PROPERTY FUNCTIONS
    """
    
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
                return DbSystem().getValue(key, default)
            return default
        return self.book[ key ]

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

    def getID(self) -> int:
        """ Convenience function. Return the BOOK id """
        return self.get_property(BOOK.id)
    
    @property
    def title(self) -> str:
        """ Convenience function. Return book name"""
        return self.get_property(BOOK.name)

    @title.setter
    def setTitle(self, newTitle: str) -> bool:
        return self.set_property(BOOK.name, newTitle)

    @property
    def keep_aspect_ratio(self) -> bool:
        """ Return the book aspect ratio stored or True if not set """
        return (self.get_property(BOOK.aspectRatio, 1) == 1)

    @keep_aspect_ratio.setter
    def keep_aspect_ratio(self, aspect: bool) -> bool:
        newAspect = 1 if aspect else 0
        return self.set_property(BOOK.aspectRatio, newAspect)


    def update_properties(self, change_list: dict) -> bool:
        """ Update properties for a book based on dictionary 

            Return True if any changes were made
        """
        self.set_property(BOOK.id, self.book[BOOK.id])
        for key, value in change_list.items():
            self.set_property(key, value)
        if len(self.changes) > 0:
            self.write_properties()
            return True
        return False

    def write_properties(self):
        """
            We have several differenty keystores: some in Book and
            some in BookSettings. We need to know where to put it.
        """
        book_id = self.getID()
        settings, database = self._splitParms(self.changes)
        for key in settings:
            self.dbooksettings.upsertBookSetting(book_id, key, self.changes[key])
        # Because we may have changed the book we need to check on the previous name

        if len(database) > 0:
            database[BOOK.book] = self.title
            self.update(**database)

        self.changes = {}

    def _book_default_values(self, bookDir: str) -> dict:
        rtn = {}
        image_extension = DbSystem().getValue(DbKeys.SETTING_FILE_TYPE, 'png')
        rtn = {
            BOOK.book:  os.path.basename(bookDir),
            BOOK.totalPages:  len(fnmatch.filter(os.listdir(bookDir), '*.' + image_extension)),
            BOOK.source: bookDir,
            BOOK.location: bookDir,
            BOOK.numberStarts: 1,
            BOOK.publisher: '(import images)',
        }

        rtn[BOOK.numberEnds] = rtn[BOOK.totalPages]
        return rtn

    def import_one_book(self, bookDir=dir):
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

        if not bookDir:
            return (book_info, "No directory passed.")

        basedir = os.path.basename(bookDir)

        if self.isLocation(bookDir) or self.isSource(bookDir):
            return (book_info, f'Book already in library: {basedir}')

        if not os.path.isdir(bookDir):
            return (book_info, f"Location '{bookDir}' is not a directory")

        book_info = self._book_default_values(bookDir)
        if book_info[BOOK.totalPages] == 0:
            return (book_info, "No pages for book")
        if self._use_toml_file:
            from qdb.mixin.tomlbook import MixinTomlBook
            book_info.update(MixinTomlBook().read_toml_properties(bookDir))

        rec_id = self.add(**book_info)
        book_info[BOOK.id] = rec_id
        return (book_info, error_msg)

    def import_directory(self, location=dir):
        """
            Import contents of a complete directory

            Return is:
                bool :       Error occured during add
                list:        list dictionaries containing added book info
                ltr:         message to return to user
        """
        addedRecords = []
        if location is None or location == "":
            return (False, addedRecords, "Location is empty")
        if not os.path.isdir(location):
            return (False, addedRecords, "Location '{}' is not a directory".format(location))

        for bookDir in [f.path for f in os.scandir(location) if f.is_dir()]:
            (book_info, error_msg) = self.import_one_book(bookDir)
            if error_msg is not None:
                return (False, addedRecords, error_msg)
            addedRecords.append(book_info)
        addedMessage = "Records added" if len(
            addedRecords) > 0 else "No new records found"
        return (True, addedRecords, addedMessage)
