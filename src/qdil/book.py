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

import os
from collections import OrderedDict
from qdb.dbbook import DbBook
from qdb.dbbooksettings import DbBookSettings
from qdb.dbsystem import DbSystem
from qdb.keys import DbKeys, BOOK, BOOKPROPERTY
from util.convert import toInt
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap


class TinyCache():

    def __init__(self, size=6):
        self.cache = OrderedDict()
        self.size(size)
        self.hits = 0
        self.miss = 0
        self.label('cache')

    def size(self, new_maxsize):
        self.max = new_maxsize

    def label(self, name) -> None:
        self.label = name

    def is_set(self, key):
        return key in self.cache

    def get(self, key):
        if key in self.cache:
            self.hits = self.hits + 1
            self.cache.move_to_end(key, last=False)
            return self.cache[key]
        self.miss = self.miss + 1
        return None

    def set(self, key, value):
        while len(self.cache) >= self.max:
            self.cache.popitem(last=True)  # pop last entry
        self.cache[key] = value
        self.cache.move_to_end(key, last=False)  # Move to first location
        return value

    def cache_clear(self):
        """ Clear will wipe out all entries. You don't really need to call this """
        while len(self.cache) > 0:
            self.cache.popitem()

    def cache_info(self) -> str:
        return "CacheInfo(hits={}, misses={}, maxsize={}, currsize={})".format(
            self.hits, self.miss, self.max, len(self.cache))


class DilBook(DbBook):
    """
        DilBook is a data interface layer that will act as the general
        data interface between the program or UI and the database layer
    """
    CACHE_SIZE = 5

    def __init__(self):
        super().__init__()
        self.tcache = TinyCache(size=self.CACHE_SIZE)
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

    def setPaths(self):
        """
        Split the directory path up into paths used by the Book class

        take a directory path (e.g. /users/yourname/sheetmusic/mybook) and split it up.
        The directory (/users/yourname/sheetmusic/mybook) is the book directory
        the first part (..../sheetmusic) is the home to all your books
        The second part (mybook) is the name of the book
        We then get bookPageName (the page plus three digit extension)
        and the complete path formatter string
        """

        self.dirPath = os.path.normpath(self.book[BOOK.location])
        self.bookPageName = "".join([self.page_prefix, "-{0:03d}"])
        self.pageFormat = "".join([self.bookPageName, ".", self.page_suffix])
        self.bookPathFormat = os.path.join(self.dirPath, self.pageFormat)

    def getFileType(self) -> str:
        return self.page_suffix

    def openBook(self, book: str, page=None, fileType="png", onError=None):
        """
            Close current book and open new one. Use BookView for data

            Each book read will also include all the BookSettings
        """
        self.newBook = super().getBook(book=book)

        if self.newBook == None:
            if onError is not None:
                return onError
            return QMessageBox.warning(None,
                                       "Opening sheetmusic",
                                       "Book {} is not valid.".format(book),
                                       QMessageBox.Retry,
                                       QMessageBox.Cancel
                                       )

        if not os.path.isdir(self.newBook[BOOK.location]):
            return QMessageBox.warning(None,
                                       "Opening directory",
                                       "Book directory '{}' is not valid.".format(
                                           self.newBook[BOOK.location]),
                                       QMessageBox.Retry,
                                       QMessageBox.Cancel)

        if self.newBook[BOOK.totalPages] == 0:
            if onError is not None:
                return onError
            return QMessageBox.warning(None,
                                       "Opening book",
                                       "There are no pages in '{}'.".format(
                                           self.book[BOOK.name]),
                                       QMessageBox.Retry, QMessageBox.Cancel)

        self.closeBook()
        self.book = self.newBook
        rows = self.dbooksettings.getAll(book)
        for row in rows:
            self.book[row['key']] = row['value']
        self.setPaths()
        page = self.book[BOOK.lastRead] if page is None else page
        self.setPageNumber(page)

        return QMessageBox.Ok

    def closeBook(self):
        """ closeBook will clear caches, values, and name paths. 
            Values will be saved to the Book or BookSettings tables
        """

        if self.book is not None:
            super().updateReadDate(self.book[BOOK.book])
            self.changes[BOOK.lastRead] = self.getAbsolutePage()
            if DbKeys.SETTING_KEEP_ASPECT in self.changes:
                self.changes[DbKeys.SETTING_KEEP_ASPECT] = (
                    1 if self.book[DbKeys.SETTING_KEEP_ASPECT] else 0)
            if self.book[DbKeys.SETTING_PAGE_LAYOUT] is not None:
                self.changes[DbKeys.SETTING_PAGE_LAYOUT] = self.book[DbKeys.SETTING_PAGE_LAYOUT]
            self.writeProperties()
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
        recId = super().addBook(**newBook)

        for key, value in settings.items():
            self.dbooksettings.upsertBookSetting(
                id=recId, key=key, value=value)
        return super().getBook(book=bookname)

    def updateIncompleteBooksUI(self):
        """
            This will get a list of books that are 'incomplete'
            and prompt, one-by-one
        """
        from ui.properties import UiProperties
        ui = UiProperties()
        for bookName in super().getIncompleteBooks().keys():
            book = super().getBook(book=bookName)
            ui.setPropertyList(book)
            ui.exec()
            if ui.isReject():
                break
            if ui.isApply():
                if BOOK.name in ui.changes and book[BOOK.name] != ui.changes[BOOK.name]:
                    super().updateName(book[BOOK.name], ui.changes[BOOK.name])
                else:
                    ui.changes[BOOK.name] = bookName
                if len(ui.changes) > 1:
                    super().update(**ui.changes)
        ui.close()
        del ui
        return

    def addBookDirectoryUI(self):
        """
            This will interface with:
                promptForDirectoryTo Scan: get the directory to check out
                Add all directories
                Prompt to see if they want us to correct new entries.
                Get all the book information
            """
        from ui.addbookdir import AddBookDirectory
        abd = AddBookDirectory()
        (added, message) = self.addBookDirectory(
            abd.promptForDirectoryToScan())
        if added:
            if abd.questionAddDetail(message):
                self.updateIncompleteBooksUI()

    def clear(self):
        # Control information: used to access files
        self.book = None
        self.dirPath = ""
        self.changes = {}
        # Set whenever the dirpath alters
        self.bookPathFormat = ""
        self.bookPageName = ""
        # File information: pages, names
        self.dirName = ""
        self.dirPath = ""
        self.thisPage = 0
        self.firstPage = 0

    def isValidPage(self, page: int) -> bool:
        return (page > 0 and page <= self.getProperty(BOOK.totalPages, 999))

    def getNote(self) -> str:
        return self.getProperty(BOOK.note)

    def getTitle(self) -> str:
        return self.getProperty(BOOK.name)

    def setTitle(self, newTitle: str) -> bool:
        if newTitle != self.getTitle():
            self.setProperty(BOOK.name, newTitle)
            return True
        return False

    def getBookPageName(self, pageNum: any = None) -> str:
        pageNum = toInt(pageNum, self.thisPage)
        return self.bookPageName.format(pageNum)

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
        return self.getProperty(BOOK.numberStarts, 1)

    def setRelativePageOffset(self, offset: any) -> bool:
        if self.getRelativePageOffset() != int(offset):
            self.setProperty(BOOK.numberStarts, offset)
            return True
        return False

    def setAspectRatio(self, aspect: bool) -> bool:
        if aspect is not None and self.getAspectRatio() != aspect:
            newAspect = 1 if aspect else 0
            self.book[BOOK.aspectRatio] = newAspect
            self.setProperty(BOOK.aspectRatio, newAspect)
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

    def getTotal(self) -> int:
        """ Return the total number of pages in a book """
        return self.getProperty(BOOK.totalPages, 0)

    def getLastPageShown(self) -> int:
        if self.getPropertyOrSystem(BOOKPROPERTY.layout) == DbKeys.VALUE_PAGES_SIDE_2:
            return max(self.getProperty(BOOK.totalPages)-1, 1)
        return self.getProperty(BOOK.totalPages)

    def incPageNumber(self, inc: int) -> int:
        """ Increment the page number by the passed integer. Number can be positive or negative. """
        return self.setPageNumber(self.thisPage+inc)

    def getContentStartingPage(self) -> int:
        ''' Return the page that content starts on (book)

            This is from the config setting KEY_PAGE_CONTENT
        '''
        return self.getProperty(BOOK.numberStarts, 1)

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
                                self.getProperty(BOOK.totalPages, 999))
        return self.thisPage

    def getBookPath(self, bookPath: str = None) -> str:
        if bookPath is None:
            return self.dirPath
        else:
            return os.path.normpath(bookPath)

    def getPageString(self, pageNum: int = None) -> str:
        if pageNum == None:
            pageNum = self.getAbsolutePage()
        return self.pageFormat.format(toInt(pageNum))

    def getBookPagePath(self, pageNum=None) -> str:
        return self.bookPathFormat.format(toInt(pageNum))

    def get_page_file(self, page: str) -> str | None:
        if self.isValidPage(page):
            imagePath = self.getBookPagePath(page)
            if os.path.isfile(imagePath):
                return imagePath
        return None
    
    def clearCache(self):
        # self.tcache.cache_clear()
        pass


    def getPixmap(self, pageNum: str) -> QPixmap:
        """ read the file and convert it into a pixal map.
            NOTE: Obsolete method. Function moved into PageWidget
        """
        px = None
        file_path = self.get_page_file(pageNum)
        if file_path is not None:
            if self.tcache.is_set(file_path):
                return self.tcache.get(file_path)
            px = QPixmap(file_path)
            px = QPixmap()
            px.setDevicePixelRatio(2)
            px.load(file_path)
            self.tcache.set(file_path, px)
        return px

    def getRecent(self):
        self.numberRecent = DbSystem().getValue(DbKeys.SETTING_MAX_RECENT_SIZE, 10)
        return super().getRecent(limit=self.numberRecent)

    def getAspectRatio(self) -> bool:
        return (BOOK.aspectRatio not in self.book or self.book[BOOK.aspectRatio] == 1)

    def getID(self) -> int:
        return self.getProperty(BOOK.id)

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

    def getAll(self):
        return self.book

    def getProperty(self, key: str, default=None) -> str:
        return (self.book[key] if self.book is not None and key in self.book else default)

    def getPropertyOrSystem(self, key: str) -> str:
        return ((self.book[key] if self.book is not None and key in self.book else DbSystem().getValue(key)))

    def writeProperties(self):
        """
            We have several differenty keystores: some in Book and
            some in BookSettings. We need to know where to put it.
        """
        book_id = self.getID()
        book_name = self.getTitle()
        settings, database = self._splitParms(self.changes)
        for key in settings:
            self.dbooksettings.upsertBookSetting(
                id=book_id, key=key, value=self.changes[key])
        # Because we may have changed the book we need to check on the previous name

        if len(database) > 0:
            database[BOOK.book] = self.getTitle()
            self.update(**database)

        self.changes = {}

    def setProperty(self, key: str, value=None) -> bool:
        """
            Set property for both the change list and the book
            If anything (other than name) is changed, return True
        """
        self.changes[key] = value
        self.book[key] = value
        return len(self.changes) > 0

    def getProperties(self):
        """
        Return the list of properties to display. The list is always name/value/Mutable/scrollable
        Scrollable is set to ensure that if one of the fields is too large, the scroll bar will
        show in the properties table
        """
        properties = {}
        if self.book is not None:
            properties = {
                "Title":                        [self.getTitle(), True, True],
                "Page for first content":       [self.getContentStartingPage(), True, False],
                "Page numbering starts at":     [self.getRelativePageOffset(), True, False],
                "Keep aspect ratio for pages":  [self.getAspectRatio(), True, False],

                "Total Pages":                  [self.getTotal(), False, False],
                "Location":                     [self.getBookPath(), False, True],
            }
        return properties

    def editProperties(self, ui):
        ui.setPropertyList(self.book)
        rtn = ui.exec()

        if rtn:
            for key, value in ui.changes.items():
                self.setProperty(key, value)

        if len(self.changes) > 0:
            self.writeProperties()
        return rtn
