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
from qdb.keys import DbKeys, BOOK, BOOKPROPERTY
from util.convert import toInt
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap

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

    def isPDF( self )->bool:
        return ( DbKeys.VALUE_PDF == self.book[ BOOK.source_type] )
    
    def isPNG(self )->bool:
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
        self.sourcepath   = os.path.normpath( self.book[BOOK.source ])
        self.formatPagePrefix = "".join([self.page_prefix, "-{0:03d}"])
        self.formatPage = "".join([self.formatPagePrefix, ".", self.page_suffix])
        self.bookPathFormat = os.path.join(self.locationpath, self.formatPage)

    def getFileType(self) -> str:
        """ Return the type of book to process (png or pdf)"""
        return ( DbKeys.VALUE_PDF if self.ispdf() else self.page_suffix )
    
    def ispdf(self , book:dict=None )->bool:
        if book is None:
            book = self.book
        return ( isinstance( book, dict) and BOOK.source_type in book and book[ BOOK.source_type ] == DbKeys.VALUE_PDF )
        

    def _load_book_setting(self, book, page=None):
        """ Internal: loads the self.book with all database values """
        self.setPageNumber(page)
        self.book = self.getBook(book=book)
        self.setPaths()
        self.book[ BOOK.lastRead ] = self.book[BOOK.lastRead] if page is None else page

    def open(self, book: str, page=None, fileType="png", onError=None):
        """
            Close current book and open new one. Use BookView for data

            Each book read will also include all the BookSettings
        """
        self.newBook = self.getBook(book=book)
        dlg = QMessageBox()
        dlg.setIcon(QMessageBox.Warning)
        dlg.setInformativeText(book)

        btnCancel = dlg.addButton(QMessageBox.Cancel)
        btnDelete = dlg.addButton('Delete', QMessageBox.DestructiveRole)
        btnRetry = dlg.addButton(QMessageBox.Retry)

        if self.newBook == None:
            if onError is not None:
                return onError
            dlg.setWindowTitle('Opening sheetmusic')
            dlg.setText("Book is not valid.")
            dlg.exec()
            return dlg.buttonRole(dlg.clickedButton())
        

        if self.ispdf( self.newBook ) :
            if not os.path.isfile( self.newBook[BOOK.location]):
                dlg.setWindowTitle('Opening directory')
                dlg.setText("Book is not valid. (No PDF)\n{}".format( self.newBook[BOOK.location]))
                dlg.exec()
                return dlg.buttonRole(dlg.clickedButton())
        else:
            if not os.path.isdir(self.newBook[BOOK.location]):
                dlg.setWindowTitle('Opening directory')
                dlg.setText("Book directory is not valid.")
                dlg.exec()
                return dlg.buttonRole(dlg.clickedButton())

        if self.newBook[BOOK.totalPages] == 0:
            if onError is not None:
                return onError
            dlg.setWindowTitle('Opening book')
            dlg.setText("The book is empty.")
            dlg.exec()
            return dlg.buttonRole(dlg.clickedButton())

        self.close()
        self._load_book_setting(book, page)

        return QMessageBox.Ok

    def close(self):
        """ closeBook will clear caches, values, and name paths. 
            Values will be saved to the Book or BookSettings tables
        """

        if self.book is not None:
            self.updateReadDate(self.book[BOOK.book])
            self.changes[BOOK.lastRead] = self.getAbsolutePage()
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

    def delete_pages( self, book_location )->bool:
        """ delete the imported sheetmusic pages directory and contents"""
        if not os.path.isdir( book_location ):
            return False
        
        shutil.rmtree( book_location , ignore_errors=True)
        return True
        
    def delete( self, key, value )->bool:
        """ Delete a book based on a datbase search. 
            Pass a "key, value" to find and delete the book. This will also delete all notes and bookmarks

            If you match more than one book, it will not delete it
        """
        book = self.getBookByColumn(key, value)
        id = None
        if book is not None and BOOK.id in book:
            id = book[ BOOK.id]
            self.delbycolumn( BOOK.id , id )
            self.delete_pages( book[ BOOK.location ])
            DbBookSettings().deleteAllValues( id, ignore=True )
            DbBookmark().delete_all( id )
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
        self.thisPage = 0
        self.firstPage = 0

    def isValidPage(self, page: int) -> bool:
        return (page > 0 and page <= self.get_property(BOOK.totalPages, 999))

    def getNote(self) -> str:
        return self.get_property(BOOK.note)

    def getTitle(self) -> str:
        return self.get_property(BOOK.name)

    def setTitle(self, newTitle: str) -> bool:
        if newTitle != self.getTitle():
            self.set_property(BOOK.name, newTitle)
            return True
        return False

    def getAbsolutePage(self) -> int:
        """ Get the current, absolute page number we are on """
        return self.thisPage

    def getRelativePage(self, fromPage=None) -> int:
        '''
            Return the relative page number or the absolute page number
            if the page isn't relative, then it will always return the absolute page
            You can check which is which by using isPageRelative()
        '''
        relPage = None
        fromPage = toInt(fromPage, self.getAbsolutePage())
        if self.isPageRelative(fromPage):
            offset = self.getRelativePageOffset() - 1
            relPage = max(0, (fromPage - offset))
        return relPage if relPage and relPage > 0 else fromPage

    def getRelativePageOffset(self) -> int:
        ''' getRelativePageOffset returns the int value of the offset, from 1. If 1, there is no offset'''
        return self.get_property(BOOK.numberStarts, 1)

    def setRelativePageOffset(self, offset: any) -> bool:
        if self.getRelativePageOffset() != int(offset):
            self.set_property(BOOK.numberStarts, offset)
            return True
        return False

    def setAspectRatio(self, aspect: bool) -> bool:
        if aspect is not None and self.getAspectRatio() != aspect:
            newAspect = 1 if aspect else 0
            self.book[BOOK.aspectRatio] = newAspect
            self.set_property(BOOK.aspectRatio, newAspect)
            return True
        return False

    def isRelativePageSet(self) -> bool:
        ''' isRelativePageSet just checks to see if they have set a relative page '''
        return (self.getRelativePageOffset() > 1)

    def isPageRelative(self, fromPage=None) -> bool:
        ''' isThisPageRelatve calculates if this page number is within the relative settings'''
        if not self.isRelativePageSet():
            return False
        return (toInt(fromPage, self.getAbsolutePage()) >= self.getRelativePageOffset())

    def convertRelativeToAbsolute(self, fromPage: int = None) -> int:
        '''Convert a relative page number to an absolute page number'''
        if fromPage is None:
            fromPage = self.thisPage
        if not self.isRelativePageSet():
            return fromPage
        return fromPage+self.getRelativePageOffset()-1

    def count(self) -> int:
        """ Return the total number of pages in a book """
        return self.get_property(BOOK.totalPages, 0)

    def getLastPageShown(self) -> int:
        if self.getPropertyOrSystem(BOOKPROPERTY.layout) == DbKeys.VALUE_PAGES_SIDE_2:
            return max(self.get_property(BOOK.totalPages)-1, 1)
        return self.get_property(BOOK.totalPages)

    def incPageNumber(self, inc: int) -> int:
        """ Increment the page number by the passed integer. Number can be positive or negative. """
        return self.setPageNumber(self.thisPage+inc)

    def getContentStartingPage(self) -> int:
        ''' Return the page that content starts on (book)

            This is from the config setting KEY_PAGE_CONTENT
        '''
        return self.get_property(BOOK.numberStarts, 1)

    def setContentStartingPage(self, pageNumber) -> bool:
        pageNumber = toInt(pageNumber)
        if self.firstPage != pageNumber:
            self.firstPage = max(1, pageNumber)
            return True
        return False

    def getFirstPageShown(self) -> int:
        return self.getRelativePageOffset()

    def setPageNumber(self, pnum) -> int:
        '''
        This is the only place you should change the current page number.
        It will accept a number or a string and force the page number to 
        a valid range (1 -> end of book)
        '''
        pnum = toInt(pnum, self.thisPage)
        if self.isValidPage(pnum):
            self.thisPage = pnum
        else:
            self.thisPage = min(max(1, self.thisPage),
                                self.get_property(BOOK.totalPages, 999))
        return self.thisPage

    def filepath(self, bookPath: str = None) -> str:
        """ Return the bookpath for this book or the normalised bookpath"""
        if bookPath is None:
            return self.locationpath
        return os.path.normpath(bookPath)

    def source_filepath( self )->str|None:
        """ Return the source path for this book (normalised)"""
        return self.sourcepath()
    
    def page_filepath(self, page: str|int , required=True) -> str | None:
        """ Return the page's path. If the file doesn't exist, None is returned"""
        imagePath =  ( self.book[BOOK.location] if self.isPDF() else  self.bookPathFormat.format(toInt(page) ) )
        
        if not required or os.path.isfile(imagePath):
            return imagePath
        return None

    def clearCache(self):
        # self.tcache.cache_clear()
        pass

    def getRecent(self):
        self.numberRecent = DbSystem().getValue(DbKeys.SETTING_MAX_RECENT_SIZE, 10)
        return super().getRecent(limit=self.numberRecent)

    def getAspectRatio(self) -> bool:
        return (BOOK.aspectRatio not in self.book or self.book[BOOK.aspectRatio] == 1)

    def getID(self) -> int:
        return self.get_property(BOOK.id)

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

    def get_properties(self) -> dict | None:
        """ Return all of the properties for the book """
        return self.book

    def get_property(self, key: str, default=None) -> str:
        """ Get one property and, if doesn't exist, return default value"""
        return (self.book[key] if self.book is not None and key in self.book else default)

    def getPropertyOrSystem(self, key: str) -> str:
        return ((self.book[key] if self.book is not None and key in self.book else DbSystem().getValue(key)))

    def write_properties(self):
        """
            We have several differenty keystores: some in Book and
            some in BookSettings. We need to know where to put it.
        """
        book_id = self.getID()
        settings, database = self._splitParms(self.changes)
        for key in settings:
            self.dbooksettings.upsertBookSetting(
                id=book_id, key=key, value=self.changes[key])
        # Because we may have changed the book we need to check on the previous name

        if len(database) > 0:
            database[BOOK.book] = self.getTitle()
            self.update(**database)

        self.changes = {}

    def set_property(self, key: str, value=None) -> bool:
        """
            Set property for both the change list and the book
            If anything (other than name) is changed, return True
        """
        self.changes[key] = value
        self.book[key] = value
        return len(self.changes) > 0

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
            return (book_info, 'Book already in library: {}'.format(basedir))

        if not os.path.isdir(bookDir):
            return (book_info, "Location '{}' is not a directory".format(bookDir))

        book_info = self._book_default_values(bookDir)
        if book_info[BOOK.totalPages] == 0:
            return (book_info, "No pages for book")
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
