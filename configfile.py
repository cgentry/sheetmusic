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

from musicsettings import MusicSettings, MSet
import configparser
import config
from bookmark import Bookmark
from musicutils import toInt


class ConfigFile(config.Config):
    CACHE_SIZE = 5
    VALUE_VERSION = "1.0"

    KEY_DEFAULT = "DEFAULT"        # Default section
    KEY_FILE_TYPE = "fileType"     # default file extension (default only)
    KEY_LOCATION = "location"      # Where we think this directory is

    KEY_TITLE = "title"            # Book title             (default)
    KEY_NAME = "name"              # Names for each bookmark (section)
    KEY_PNAME = "pname"            # The name presentable to the user (section)
    KEY_VERSION = "version"        # configuration version  (default)
    KEY_FINAL_PAGE_NUMBER="final_page"       # Last numbered page in book

    # PAGE NUMBER SECTION
    # Used to pass around page numbers but never saved
    KEY_PAGE = 'page'
    # first Page for each bookmark  (default/section)
    KEY_PAGE_CONTENT = "content_start"
    # last page accessed     (default only)
    KEY_PAGE_LAST_READ = "last_read"
    # page computations for display will be relative to this page
    KEY_PAGES_START = "numbering_starts"
    KEY_PAGES_END = "numbering_ends"

    # STATS (dynamic on file open)
    KEY_TOTAL_PAGES = "total_pages"

    def __init__(self, settings=None):
        super().__init__(settings)
        self.currentBookmark = None
        self._initConfig()

    def _initConfig(self)->None:
        self.empty_lines_in_values = False
        self['DEFAULT'] = {
            self.KEY_FILE_TYPE:    "png",
            self.KEY_PAGE_CONTENT:  '1',
            self.KEY_PAGE_LAST_READ: '1',
            self.KEY_PAGES_START:   "1",
            self.KEY_PAGES_END:     "0",
            self.KEY_TOTAL_PAGES:   '0',
            self.KEY_VERSION:       self.VALUE_VERSION,
            self.KEY_TITLE:         '(name not set)',
        }

    def _endSectionPage(self, sections, index=int) -> str:
        '''
        _endSectionPage will compute the last page entry for a bookmark based on
        the start of the next bookmark. If there are no bookmarks, or this is the
        last bookmark, zero will be returned. The end page is one less from the 
        start of the next bookmark
        '''
        defaultLength = self.getConfigInt(self.KEY_TOTAL_PAGES, value=0)
        if len(sections) > 0:
            if index >= 0 and index+1 < len(sections):
                nextSection = sections[index+1]
                return max(0, self.getConfigInt(self.KEY_PAGE_CONTENT, nextSection, 0) - 1)
        return defaultLength

    def _formatBookmark(self, sectionKey: str, index: int = None, endSectionPage=None) -> Bookmark:
        '''
        _formatBookmark will fill in the bookmark from passed values. If there are missing
        values, it will look them up in the sections list.
        '''
        bookmark = Bookmark(found=False)
        if self.has_section(sectionKey):
            if index is None or endSectionPage is None:
                sections = self.sectionsSorted()
                if index is None:
                    index = sections.index(sectionKey)
                if endSectionPage is None:
                    endSectionPage = self._endSectionPage(sections, index)
            bookmark.setIndex( index )
            bookmark.setName( )
            bookmark.setSection(sectionKey)
            bookmark.setPage(self[sectionKey][ConfigFile.KEY_PAGE_CONTENT])
            bookmark.setEndPage(endSectionPage)
            bookmark.setFound(True)
            bookmark.setEndOfList( ( index <= 0 or index >= self.totalBookmarks()-1 ) )
            #print("Index:", index, ", total Sections:", self.totalBookmarks()-1 )
        return bookmark

    def _bookmarkFromIndex(self, sections, index) -> Bookmark:
        if len(sections) < 0:
            return Bookmark(found=False)
        index = min(len(sections)-1, max(0, index))
        section = sections[index]
        return self._formatBookmark( section, index )
        
    def setTotalPages(self, totalPages)->None:
        self.setConfig(self.KEY_TOTAL_PAGES, totalPages)

    def getTotalPages( self )->int:
        return self.getConfigInt(self.KEY_TOTAL_PAGES, value=0)

    def getBookLayout(self)->str:
        return self.getConfig(MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT))

    def getNumberPagesToDisplay(self) -> int:
        return (1 if self.getBookLayout() == MSet.VALUE_PAGES_SINGLE else 2)

    def getBookmarkForPage(self, thisPage) -> str:
        bookmark = self.getBookmarkClassForPage(thisPage)
        return bookmark.section

    def getBookmarkClassForPage(self, thisPage)->Bookmark:
        """
        getBookmarkClassForPage will take the current page number and search a bookmark that's page
        is >= this page < any other bookmark. It will return the name of the bookmark's
        block or blank if none found
        """
        thisPage = toInt(thisPage)
        foundbookmark = Bookmark(
            page=0, 
            endpage=self.getConfigInt(self.KEY_TOTAL_PAGES, value=0), 
            found=False)
        sections = self.sectionsSorted()

        if not len(sections):
            foundbookmark.setPage(1)
            return foundbookmark

        if thisPage and len(sections):
            lowestBookmarkPage = self.getConfigInt(
                self.KEY_PAGE_CONTENT, sections[0], value=0)
            if thisPage < lowestBookmarkPage:
                foundbookmark.setPage(1)
                return foundbookmark

            index = 0
            for section in sections:
                bookmarkPage = self.getConfigInt(
                    self.KEY_PAGE_CONTENT, section, value=0)
                if not bookmarkPage or bookmarkPage > thisPage:
                    break
                if bookmarkPage <= thisPage and bookmarkPage > foundbookmark.page:
                    foundbookmark = self._formatBookmark(
                        section, index, self._endSectionPage(sections, index))
                if bookmarkPage == thisPage:
                    break
                index = index+1
        return foundbookmark

    def getBookmarkForPageField(self, thisPage, fieldName) -> str:
        bmark = self.getBookmarkForPage(thisPage)
        if bmark != "":
            return self.getConfig(fieldName, bmark)
        return None

    def getBookmarkWithOffset(self, offset)->Bookmark:
        '''
        getBookmarkWithOffset will find the bookmark relative to the current bookmark
        The class value 'currentBookmark' must be preset for computations to work.
        '''
        offset = toInt( offset, 0)
        return self._bookmarkFromIndex(self.sectionsSorted(), self.currentBookmark.index+offset)

    def getPreviousBookmark(self) -> Bookmark:
        return self._bookmarkFromIndex(self.sectionsSorted(), self.currentBookmark.index-1)

    def getNextBookmark(self) -> Bookmark:
        return self._bookmarkFromIndex(self.sectionsSorted(), self.currentBookmark.index+1)

    def getFirstBookmark(self) -> Bookmark:
        return self._bookmarkFromIndex(self.sectionsSorted() , 0 )

    def getLastBookmark(self) -> Bookmark:
        return self._bookmarkFromIndex(self.sectionsSorted() , 99999 )

    def getFirstBookmarkPage(self) -> int:
        bookmark = self.getFirstBookmark()
        if bookmark and bookmark.isFound():
            return bookmark.page
        return None

    def setCurrentBookmark(self, current)->None:
        '''
        save current bookmark information. Accepts either a page or Bookmark class
        '''
        if isinstance(current, Bookmark):
            self.currentBookmark = current
        else:
            self.currentBookmark = self.getBookmarkClassForPage(current)

    def getCurrentBookmark(self)->Bookmark:
        return self.currentBookmark

    def clearCurrentBookmark(self)->None:
        self.currentBookmark = None

    def isCurrentBookmarkSet(self)->bool:
        return self.currentBookmark is not None

    def totalBookmarks(self)->int:
        return len( self.sections() )