# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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
# image files should be in a single folder and end in '.png'
# configuration for each book is located in
# config.ini - See ConfigFile in configfile.py
# 


import os
import fnmatch
from musicutils import toInt, toBool
from configfile import ConfigFile
from bookmark import Bookmark
from musicsettings import MusicSettings,MSet
from PySide6.QtWidgets import QMessageBox

class MusicFile:
    '''
    Class will handle the file functions and configuration.
    '''
    CACHE_SIZE = 5

    def __init__(self):
        super().__init__()
        self.clearSettings()
        self.bookConfigIsValid = False
        self.isBookOpen = False
        # config information
        self.setDefaultConfig()

    def _formatPrettyName(self, name):
        ''' Only called when you want to split apart a page name to something nicer'''
        pname = name.capitalize()
        if '-' in name:
            splits = pname.rsplit("-", 1)
            if len(splits) == 2:
                pname = splits[0] + ", page " + str(int(splits[1]))
        return pname

    def setPaths(self, bookPath:str):
        """
        take a directory path (e.g. /users/yourname/sheetmusic/mybook) and split it up.
        The directory (/users/yourname/sheetmusic/mybook) is the book directory
        the first part (..../sheetmusic) is the home to all your books
        The second part (mybook) is the name of the book
        We then get bookPageName (the page plus three digit extension)
        and the complete path formatter string
        """
        self.dirPath = os.path.normpath(bookPath)
        dir_name = os.path.split(self.dirPath)
        self.dirName = dir_name[0]
        self.fileBaseName = 'page'
        self.book = dir_name[1]
        self.bookPageName = "".join( [self.fileBaseName , "-{0:03d}"] )
        self.bookPathFormat = os.path.join(
            self.dirPath, "".join( [self.bookPageName,".",self.getFileType()]) )

    def setFileType(self, ftype: str):
        """ Set the file type. Normally this is 'png' but it's possible to use other formats. """
        self.config.set('DEFAULT', self.config.KEY_FILE_TYPE, ftype)

    def getFileType(self) -> str:
        return self.config.get('DEFAULT', self.config.KEY_FILE_TYPE)

    def openBook(self, bookPath:str, page=None, fileType="png", onError=None):
        bpath = self.getBookPath( bookPath)
        if not os.path.isdir(bpath):
            if onError is not None:
                return onError
            return QMessageBox.warning( None, 
                        "Opening directory",
                         "Directory {} is not valid.".format(bpath),
                         QMessageBox.Retry, 
                         QMessageBox.Cancel )

        totalPages = len(fnmatch.filter(
            os.listdir(bpath), '*.' + self.getFileType()))
        if totalPages > 0:
            self.closeBook()
            self.setPaths(bookPath)
            self.config.setConfig(self.config.KEY_TOTAL_PAGES, totalPages )
            self.totalPages = totalPages
            self.isBookOpen = True
            self.openBookConfig()
            self.totalBookmarks = len(self.config.sections())
            page = toInt( page , self.config['DEFAULT'][self.config.KEY_PAGE_LAST_READ])
            self.setPageNumber(page)
        else:
            if onError is not None:
                return onError
            return QMessageBox.warning( None, 
                    "Opening book",
                    "There are no pages in '{}'.".format(bpath),
                    QMessageBox.Retry, QMessageBox.Cancel )

        return QMessageBox.Ok

    def closeBook(self):
        """ closeBook will clear caches, values, and name paths. 
            Values will be saved to the config file
        """
        if self.isBookOpen:
            self.config.setConfig( self.config.KEY_PAGE_LAST_READ, str(self.getBookPageNumber()))
            self.config.setConfig( self.config.KEY_PAGE_CONTENT,   str(self.firstPage))
            self.config.setConfig( self.config.KEY_TOTAL_PAGES,    str(self.totalPages ) )
            self.config.clearCurrentBookmark()
            self.writeBookConfig()
            self.bookConfigIsValid = False
            self.isBookOpen = False
        self.clearSettings()

    def clearSettings(self):
        # Control information: used to access files
        self.dirPath = ""
        # Set whenever the dirpath alters
        self.bookPathFormat = ""
        self.bookPageName = ""
        # File information: pages, names, bookmarks
        self.book = ''
        self.totalBookmarks = 0
        self.dirName = ""
        self.dirPath = ""
        self.fileBaseName = ""
        self.thisPage = 0
        self.totalPages = 0
        self.thisBookmark = ""
        self.firstPage = 0

    def getBookmarkName( self, bookmark ) -> str:
        return self.getConfig( ConfigFile.KEY_NAME,bookmark, bookmark )

    def saveBookmark(self, name:str=None, layout:str=None, bookpage:int=None, pageshown:int=None)->None:
        ''' Save a bookmark with pagenumber or the page shown
        
        Savebookmark can be passed 
        1. nothing and it will save it with a made-up name and current page
        2. A name and will use the current page
        3. A relative page number OR page number (absolute). Relative has precidence
        '''
        if pageshown is not None and pageshown > 0 :
            pagenumber = self.getBookPageAbsolute( pageshown)
        elif bookpage is None or bookpage==0:
            pagenumber = self.getBookPageNumber()
        else:
            pagenumber = bookpage 

        bookmarkFileName = self.getBookPageName( pagenumber )
        if name is None or not name:
            name = bookmarkFileName
        self.config[bookmarkFileName] = {
            self.config.KEY_NAME:            name,
            self.config.KEY_PAGE_CONTENT:    str(pagenumber),
            self.config.KEY_VERSION:         self.config.VALUE_VERSION,
        }
        if layout:
            self.config[bookmarkFileName][MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)] = layout
        self.writeBookConfig()

    def goPreviousBookmark(self)->Bookmark:
        bookmark = self.config.getPreviousBookmark( )
        if bookmark.isFound():
            self.setPageNumber( bookmark )
        return bookmark

    def goNextBookmark(self)->Bookmark:
        bookmark = self.config.getNextBookmark(  )
        if bookmark.isFound():
            self.setPageNumber( bookmark )
        return bookmark
 
    def checkPageNumber(self) -> int:
        self.thisPage = min( max( 1, self.thisPage) , self.totalPages )
        return self.thisPage

    def getBookTitle(self) -> str:
        return self.config[self.config.KEY_DEFAULT][self.config.KEY_TITLE]
    
    def setBookTitle(self, newTitle:str ) -> bool:
        if newTitle != self.getBookTitle():
            self.config.setConfig( ConfigFile.KEY_TITLE, value = newTitle )
            return True
        return False
    
    def getBookPageName(self, pageNum:any=None) -> str:
        pageNum = toInt( pageNum, self.thisPage)
        return self.bookPageName.format(pageNum)

    def getBookPageNumber(self) -> int:
        """ Get the current, absolute page number we are on """
        return self.thisPage

    def getRelativePageOffset(self) -> int:
        ''' getRelativePageOffset returns the int value of the offset, from 1. If 1, there is no offset'''
        return self.config.getConfigInt(self.config.KEY_PAGES_START , value=0)
    
    def setRelativePageOffset( self, offset:any ) -> bool:
        if self.getRelativePageOffset() != int(offset):
            self.config.setConfig( ConfigFile.KEY_PAGES_START, value=offset)
            return True
        return False

    def setAspectRatio( self, aspect:bool )->bool:
        if self.getAspectRatio() !=  aspect :
            self.config.setConfig( MSet.SETTING_DEFAULT_ASPECT , aspect)
            return True
        return False

    def isRelativePageSet(self) -> bool:
        ''' isRelativePageSet just checks to see if they have set a relative page '''
        return (self.getRelativePageOffset() > 1)

    def isThisPageRelative(self, fromPage=None) -> bool:
        ''' isThisPageRelatve calculates if this page number is within the relative settings'''
        if not self.isRelativePageSet():
            return False
        return( toInt( fromPage , self.getBookPageNumber()) >= self.getRelativePageOffset() )

    def getBookPageAbsolute(self, fromPage:int )->int:
        '''Convert a relative page number to an absolute page number'''
        if not self.isRelativePageSet():
            return fromPage
        return fromPage+self.getRelativePageOffset()-1

    def getBookPageNumberRelative(self, fromPage=None) -> int:
        ''' Return the relative page number or the absolute page number
            
            if the page isn't relative, then it will always return the absolute page
            You can check which is which by using isThisPageRelative()
        '''
        relPage = None
        fromPage = toInt( fromPage , self.getBookPageNumber()) 
        if self.isThisPageRelative(fromPage):
            offset = self.getRelativePageOffset() - 1
            relPage = max(0, (fromPage - offset))
        return relPage if relPage and relPage > 0 else fromPage

    def getBookPagesTotal(self) -> int:
        return self.totalPages

    def getLastPageShown(self) -> int:
        offset = self.getRelativePageOffset()
        lastDisplayPage = self.config.getConfigInt(self.config.KEY_FINAL_PAGE_NUMBER 
            , value=self.totalPages-offset)
        return lastDisplayPage+offset

    def incPageNumber(self, inc:int) -> int:
        """ Increment the page number by the passed integer. Number can be positive or negative. """
        self.setPageNumber( self.thisPage+inc)

    def getConfig(self, key, defaultValue=None, section="DEFAULT"):
        if self.config.has_option( section , key ):
            return self.config[section][key]
        return defaultValue
        
    def setConfig(self, key, value, section="DEFAULT"):
        self.config.setConfig( key, value, section)
        self.writeBookConfig()

    def getContentStartingPage(self) -> int:
        ''' Return the page that content starts on (book)
        
            This is from the config setting KEY_PAGE_CONTENT
            This is fetched by openBookConfig
        '''
        return self.firstPage

    def setContentStartingPage(self, pageNumber )->bool:
        pageNumber = toInt( pageNumber )
        if self.firstPage !=  pageNumber :
            self.firstPage = max(1, pageNumber )
            return True
        return False

    def getFirstPageShown(self) -> int:
        return self.getRelativePageOffset()
        
    def setPageNumber(self, pnum) -> int:
        '''
        This is the only place you should change the current page number.
        It will accept a number or a Bookmark

        Note that this will not save to config
        '''
        lastpnum = self.thisPage
        if pnum is not None:
            if isinstance( pnum, Bookmark ):
                if pnum.isFound():
                    self.thisPage = pnum.page
                    self.config.setCurrentBookmark( pnum )
            else:
                if isinstance(pnum, str):
                    if pnum:
                        self.thisPage = int(pnum)
                else:
                    self.thisPage = pnum
                self.checkPageNumber()
                if lastpnum != self.thisPage:
                    self.config.setCurrentBookmark( self.thisPage)
        return self.thisPage

    def getBookPath(self, bookPath:str=None)->str:
        if bookPath is None:
            return self.dirPath
        else:
            return os.path.normpath(bookPath)

    def getBookPagePath(self, pageNum=None)->str:
        return self.bookPathFormat.format(toInt( pageNum ))

    def setDefaultConfig(self):
        self.config = ConfigFile()
        self.config.setConfig( self.config.KEY_TITLE , self.book )

    def openBookConfig(self):
        """
        openBookConfig will read 'config.ini' file in the current music
        directory. If the file doesn't exist, it will create a basic one
        """
        self.bookConfigIsValid = True
        self.setDefaultConfig()
        configPath = os.path.join(self.dirPath, "config.ini")
        if os.path.isfile(configPath):
            self.config.read(configPath)
        else:
            self.writeBookConfig()

        self.firstPage = self.config.getConfigInt(self.config.KEY_PAGE_CONTENT, value=1 )
        self.setPageNumber( self.config.getConfigInt(self.config.KEY_PAGE_LAST_READ, value = 1) )
        self.config.setConfig(self.config.KEY_LOCATION, self.dirPath )

    def writeBookConfig(self):
        configPath = os.path.join(self.dirPath, "config.ini")
        if self.bookConfigIsValid:
            with open(configPath, 'w') as configfile:
                self.config.write(configfile)
        return True

    def getBookmarkList(self):
        """
        Return a list of all the names for the bookmarks in order."""
        list = []
        for bookmark in self.config.sectionsSorted():
            list.append( self.getBookmarkName( bookmark ))
        return list

    def getNumberBookmarks(self)->int:
        return self.totalBookmarks

    def getAspectRatio(self)->bool:
        return self.config.getConfigBool(MSet.SETTING_DEFAULT_ASPECT, value=True)

    def getProperties(self):
        """
        Return the list of properties to display. The list is always name/value/Mutable/scrollable
        Scrollable is set to ensure that if one of the fields is too large, the scroll bar will
        show in the properties table
        """
        properties = {}
        list = '"' +'", "'.join( self.getBookmarkList()) + '"'
        if self.isBookOpen:
            properties = {
                "Title": [self.getBookTitle(), True , True],
                "Page for first content": [self.getContentStartingPage(), True ,False],
                "Page numbering starts at": [self.getRelativePageOffset(), True , False],
                "Keep aspect ratio for pages": [self.getAspectRatio() , True, False ],
                
                "Total Pages": [self.totalPages, False ,False],
                "Total Bookmarks": [self.totalBookmarks, False , False],
                "List of Bookmarks": [list, False , True],
                "Location": [self.getBookPath(), False , True],
            }
        return properties

    def setMutableProperties(self, title, content, relative, aspect):
        '''
        Set the title, content start, and relative page. If any change occurs, true will be returned'''
        change = ( 
            self.setBookTitle( title ) 
            or self.setContentStartingPage( content ) 
            or self.setRelativePageOffset( relative )
            or self.setAspectRatio( toBool( aspect ) )
        )

        if change :
            self.writeBookConfig()
        return change