# This Python file uses the following encoding: utf-8
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

# NOTE: There is some weird stuff with 3 pages. C++ deletes SheetMusicWidgets
# even when the references are just fine. There are some sloppy fixes to
# get around this. Sorry. I'll continue to try and change this.

from PySide6.QtCore import QSize
from PySide6.QtGui import ( Qt )
from PySide6.QtWidgets import (
    QHBoxLayout, QSizePolicy,QWidget, 
    QMainWindow, QVBoxLayout)
from qdb.keys import DbKeys
from qdb.log  import DbLog
from ui.borderglow import BorderGlow
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget
from util.pdfclass import PdfDimensions

class BottomSheet():
    """ Base functions for sheetmusic. 
    """
    FORWARD = True
    BACKWARD = False

    LAYOUT_WIDTH = 'width'
    LAYOUT_HEIGHT = 'height'
    LAYOUT_PAGES = 'count'
    LAYOUT_SETUP = '©up'
    LAYOUT_CREATE = 'layout'
    ALL_PAGES = 3

    def __init__(self, MainWindow: QMainWindow, name:str ):
        self.pageRefs = []
        self.border_glow = BorderGlow()
        self._setupVars(MainWindow)
        self._set_size(MainWindow)
        self.logger = DbLog( 'BottomSheet')

        self.createMainPageWidget( name )
        self._dimensions = None

    def _setupVars(self, MainWindow: QMainWindow):
        """ Set any variables that should be set before we startup
            This will not create any objects for display
        """
        self._layout = {
            DbKeys.VALUE_PAGES_SINGLE:  {
                self.LAYOUT_SETUP:  self.createSideBySideLayout,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES:  1},
            DbKeys.VALUE_PAGES_SIDE_2:  {
                self.LAYOUT_SETUP:  self.createSideBySideLayout ,
                self.LAYOUT_WIDTH:  2,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES:  2},
            DbKeys.VALUE_PAGES_SIDE_3:  {
                self.LAYOUT_SETUP:  self.createSideBySideLayout,
                self.LAYOUT_WIDTH:  3,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES:  3},
            DbKeys.VALUE_PAGES_STACK_2: {
                self.LAYOUT_SETUP:  self.createStackedLayout,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 2,
                self.LAYOUT_PAGES: 2},
            DbKeys.VALUE_PAGES_STACK_3: {
                self.LAYOUT_SETUP:  self.createStackedLayout,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 3,
                self.LAYOUT_PAGES:  3},
        }

        self.direction = self.FORWARD
        self._currentLayout = None
        self._currentLayoutMode = None
        self.windowHeight = None
        self.windowWidth = None
        self.page_width = None
        self.page_height = None
        self.smartTurn = False
        self._pdfmode = False
    
    """ -----------------------------------------------
            ACTION / CREATION METHODS
        -----------------------------------------------
    """
    def _add_page_widget( self, page:int)->None:
        """ Add the page widget to the layout if it isn't there already """
        if not self.pageRefs[ page ].isVisible():
            if self._currentLayout.indexOf( self.pageRefs[page].widget() ) < 0 :
                self._currentLayout.insertWidget(page , self.pageRefs[page].widget() ,  0 )
        self.pageRefs[ page ].show()

    def createMainPageWidget(self, name:str) -> QWidget:
        """ This will create the main widget used to hold the pages"""
        self.mainPageWidget = QWidget()
        self.mainPageWidget.setObjectName( name)
        self.mainPageWidget.setEnabled(True)
        self.mainPageWidget.setVisible(True)
        self.mainPageWidget.grabGesture(Qt.SwipeGesture)
        self.mainPageWidget.setSizePolicy( self.createPageSizePolicy( self.mainPageWidget))
        return self.mainPageWidget
    
    def createPages(self ):
        """ Create all of the page content display widgets
            content generator must take one parm: label and
            return a display widget that conforms to the
            interface 'ISheetMusicDisplay'
        """
        
        self.pageRefs = [ self.content_generator( f"page-{ index+1 }" ) for index in  range( BottomSheet.ALL_PAGES ) ]
        for page in self.pageRefs:
            page.widget().setStyleSheet("background: black")
            page.widget().hide()
                            
    def createPageSizePolicy(self, widget) -> QSizePolicy:
        """ Create the page size policy used for the display widget"""
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        return sizePolicy

    def createSideBySideLayout(self)->QHBoxLayout:
        self.layoutPagesSide = QHBoxLayout()
        self.layoutPagesSide.setObjectName(u"horizontalLayoutWidget")
        self.layoutPagesSide.setContentsMargins(0, 0, 0, 0)
        return self.layoutPagesSide

    def createStackedLayout(self)->QVBoxLayout:
        self.layoutPagesStacked = QVBoxLayout()
        self.layoutPagesStacked.setObjectName(u"VerticalLayoutWidget")
        self.layoutPagesStacked.setContentsMargins(0, 0, 0, 0)
        return self.layoutPagesStacked


    def _set_size(self, windowSize:QMainWindow|QSize) -> bool:
        """ Save the size for the main window. This will accept
            QMainWindow, QSize. Do not call this
            directly; resize will call it and it should be called first
        """
        if windowSize is not None:
            if isinstance(windowSize, QMainWindow):
                windowSize = windowSize.size()
            if isinstance(windowSize, QSize):
                self.windowWidth = windowSize.width()
                self.windowHeight = windowSize.height()
        return self.windowWidth is not None and self.windowHeight is not None 

    def _size_pages( self ):
        self.page_width = int(
                self.windowWidth / self._getLayoutValue(self.LAYOUT_WIDTH))
        self.page_height = int(
                self.windowHeight / self._getLayoutValue(self.LAYOUT_HEIGHT))
        if self.page_width and self.page_height:
            for index in range( self.numberPages() ):
                self.pageRefs[ index ].resize(self.page_width, self.page_height)

    def resize(self, size:QSize|None = None) -> None:
        """ This must be called everytime the window is resized and on startup 
            You should pass the qsize or width in. It will be called on creation
            to set sizes correctly
        """
        if self._set_size( size ) and self._currentLayoutMode :
            self._size_pages()

    def show(self)->None:
        """ Display the pages, resize to fit and force the main widget to display"""
        self.showPages()
        self.mainPageWidget.show()
    
    def showPages(self, maxpages:int=0) -> None:
        """ Show all the pages and issue a resize """
        if maxpages == 0 or maxpages > self.numberPages() :
            maxpages = self.numberPages()
        for index in range( maxpages ):
            self._add_page_widget( index )

    def _hidePage( self, page:int)->None:
        """ Index is offset from zero """
        
        if self.pageRefs[ page ].isVisible():
            self._currentLayout.removeWidget(self.pageRefs[page])
        self.pageRefs[ page ].hide()

    def hidePages(self , maxpage:int=0) -> None:
        """ Remove all from the page layout """
        if maxpages == 0 or maxpages > len( self.pageRefs ):
            maxpages = len( self.pageRefs )
        for page in range( 0, maxpage ):
            self._hidePage( page )

    def clear(self):
        """ Clear all pages (displayed or not), but do not remove them from layout"""
        self.border_glow.stopBorderGlow()
        for page in self.pageRefs:
            page.clear()

    """ -----------------------------------------------
            PROPERTY METHODS
        -----------------------------------------------
    """
    def dimensions( self )->PdfDimensions:
        if self._dimensions is None:
            self.setDimensions( PdfDimensions() )
        return self._dimensions 

    def setDimensions( self, dimensions:PdfDimensions):
        self._dimensions = dimensions
        for page in self.pageRefs:
            page.widget().dimensions = self.dimensions 
  
    def setKeepAspectRatio(self, flag: bool) -> None:
        for page in self.pageRefs:
            page.setKeepAspectRatio(flag)
            page.widget().setKeepAspectRatio(flag)

    def keepAspectRatio(self) -> bool:
        """ Only return the flag from page one
            All pages have the same flag set and page one is always displayed"""
        return self.pageRefs[0].keepAspectRatio()

    def _getLayoutValue(self, key):
        return self._layout[self._currentLayoutMode][key]

    def _removeCurrentLayout(self) -> None:
        if self._currentLayoutMode is not None and self._currentLayout is not None:
            # self.hidePages()                            # Remove all pages from layout
            QWidget().setLayout(self._currentLayout)  # Set current to dummy widget
            self._currentLayout = None

    def _setLayout(self, layout: str) -> None:
        """ This will set the page layout to be either side-by-side or stacked 
            If there is a setup mode already set, it will be removed and replaced
        """
        if self._currentLayoutMode != layout :
            self._currentLayoutMode = layout
            self._removeCurrentLayout()
            self._currentLayout = self._layout[ layout ][ self.LAYOUT_SETUP ]()
            self.createPages()
            numpages = self.numberPages()
            for index in range( numpages ):
                self._currentLayout.insertWidget( index, self.pageRefs[ index ].widget() )
            self.showPages( numpages )
            self.mainPageWidget.setLayout(self._currentLayout)
            self._size_pages()

    def setDisplay(self, layout: str) -> None:
        """ Set the widget layout for display. Options are single, double, triple, side or stacked. """
        if layout in self._layout:
            self._setLayout(layout)
        else:
            raise ValueError(
                "Internal error: Unknown layout requested {}".format(layout))

    def setSmartPageTurn(self, state: bool) -> bool:
        """ Set the smart turn feature and return the previous state """
        rtn = self.smartTurn
        self.smartTurn = state
        return rtn

    @property
    def usepdf(self)->bool:
        return self._pdfmode 
    
    def setPdfDisplayMode( self, state:bool)->None:
        self._pdfmode = state
        for page in self.pageRefs:
            page.pdfdisplaymode = state


    """ -----------------------------------------------
            PAGE MOVEMENT METHODS
        -----------------------------------------------
    """
    def _rollForward(self, page_number: int) -> bool:
        """
            OK, so we have up to 'n' pages loaded but on 'p' pages are 
            displayed. If we have the page already, promote that by 'rolling'
            forward.
            * page must be in list of pages held
            * can't be displaying all of the pages
            * page isn't displayed
        """
        roll = False
        while (page_number in self.page_numbers() and
                not self.isShown(page_number) and
                self.numberPages() != self.ALL_PAGES
               ):
            roll = True
            self.pageRefs[0].copy(self.pageRefs[1])
            self.pageRefs[1].copy(self.pageRefs[2])
            self.pageRefs[2].clear()
        return roll

    def _rollForwardZeros(self, endpage: int):
        if endpage != 0:
            while self.pageRefs[0].pageNumber() == 0:
                self.pageRefs[0].copy(self.pageRefs[1])
                self.pageRefs[1].copy(self.pageRefs[2])
                self.pageRefs[2].clear()

    def _simpleNextPage(self, content: object, page_number: int):
        pageshown = self.numberPages()
        if pageshown == 1:
            self.pageRefs[0].setContentPage(content, page_number)
        elif pageshown == 2:
            self.pageRefs[0].copy(self.pageRefs[1])
            self.pageRefs[1].setContentPage(content, page_number)
        else:
            self.pageRefs[0].copy(self.pageRefs[1])
            self.pageRefs[1].copy(self.pageRefs[2])
            self.pageRefs[2].setContentPage(content, page_number)

    def _simplePreviousPage(self, content: object, page_number: int):
        self.pageRefs[ 2 ].copy(self.pageRefs[ 1 ])
        self.pageRefs[ 1 ].copy(self.pageRefs[ 0 ])
        self.pageRefs[ 0 ].setContentPage(content, page_number)

    def _smartPage(self, plw: ISheetMusicDisplayWidget, content: object, page_number: int) -> None:
        self.border_glow.stopBorderGlow()
        plw.setContentPage(content, page_number)
        self.border_glow.startBorderGlow(plw.widget())

    def loadPages(self, 
                  content_1: object, page_number1: int, 
                  content_2: object, page_number2: int, 
                  content_3: object, page_number3: int):
        """ loadPages should be called whenever a book is opened. It setups for
            either 'smart' page turn or for simple page turning.
        """
        self.logger.debug( 'Load {} {} {}'.format( page_number1, page_number2, page_number3))
        self.pageRefs[0].dimensions = self.dimensions
        self.pageRefs[0].setContentPage(content_1, page_number1)
        self.pageRefs[1].dimensions = self.dimensions
        self.pageRefs[1].setContentPage(content_2, page_number2)
        self.pageRefs[2].dimensions = self.dimensions
        self.pageRefs[2].setContentPage(content_3, page_number3)
        self.direction = self.FORWARD
        self._size_pages()

    def nextPage(self, content: object, page_number: int, end: bool = False):
        if not end or not self.isShown(page_number):
            if self.smartTurn and self.numberPages() > 1:
                self._smartPage(self.lowestSheetMusicWidget(), content, page_number)
            else:
                self._simpleNextPage(content, page_number)
        self.direction = self.FORWARD

    def previousPage(self, content: object, page_number: int, end: bool = False):
        if not end or not self.isShown(page_number):
            if self.smartTurn and self.numberPages() > 1:
                self._smartPage(self.highestSheetMusicWidget(), content, page_number)
            else:
                self._simplePreviousPage(content, page_number)
        self.direction = self.BACKWARD

    """ -----------------------------------------------
            PAGE NUMBER INFORMATION METHODS
        -----------------------------------------------
    """
    def current_pages(self)->list[str]:
        """ Return a list of printable page descriptions (Used for debugging/logging)"""
        rtn = []
        if self._currentLayout is not None:
            for i in range( self._currentLayout.count() ) :
                item = self._currentLayout.itemAt( i ).widget()
                desc = "Item {}: type: {} Objectname: {}".format( i , type(item) ,item.objectName() )
                rtn.append( desc )
        return rtn

    def page_numbers(self)->list[int]:
        return [ page.pageNumber() for page in self.pageRefs ]
    
    def page_numbers_displayed(self)->list[int]:
        """ Return all the page numbers currently displayed """
        return self.page_numbers()[0:self.numberPages()]

    def getLowestPageShown(self):
        """ Return the lowest page in the array that can be seen"""
        return min(self.page_numbers_displayed())

    def getHighestPageShown(self):
        return max(self.page_numbers_displayed())

    def getPageForPosition(self, position)->int:
        return self.page_numbers()[position-1]

    def numberPages(self) -> int:
        """ Return how many pages will be shown for this layout """
        if self._currentLayoutMode == None:
            return 0
        return self._layout[self._currentLayoutMode][self.LAYOUT_PAGES]

    """ -----------------------------------------------
            PAGE FIND METHODS
        -----------------------------------------------
    """
    def _find_page_by_pagenumber(self, page_number: int) -> ISheetMusicDisplayWidget|None:
        """ find the pagelabelwidget that is displayed and return to caller """
        search_list = self.page_numbers_displayed()
        if page_number in search_list:
            return self.all_pages[search_list.index(page_number)]
        return None

    def set_pagelabel_stylesheet(self, page_number: int, style: str = "") -> bool:
        """ pagelabelwidget and set the stylesheet """
        page = self._find_page_by_pagenumber(page_number)
        if page:
            page.setStyleSheet(style)

    def isShown(self, page: int) -> bool:
        return page in self.page_numbers_displayed()

    """ -----------------------------------------------
            Object Access METHODS
        -----------------------------------------------
    """
    def get_widgets_in_page_order(self) -> list[ISheetMusicDisplayWidget]:
        """ 
        Return the widgets in page order

        Created to handle any number of pages. Bit over the top but didn't
        want to rewrite it again.
        """
        pnum = self.numberPages()
        if pnum == 1:
            return [self.pageRefs[ 0 ]]

        key_pages = {}
        ordered = []

        for page in [self.pageRefs[ 0 ], self.pageRefs[ 1 ], self.pageRefs[ 2 ]][0: pnum]:
            key_pages[page.pageNumber()] = page

        for key in sorted(key_pages):
            ordered.append(key_pages[key])
        return ordered

    def highestSheetMusicWidget(self, offset: int = 0) -> ISheetMusicDisplayWidget:
        ordered = self.get_widgets_in_page_order()
        index = max(len(ordered)-1-offset, 0)
        return ordered[index]

    def lowestSheetMusicWidget(self) -> ISheetMusicDisplayWidget:
        return self.get_widgets_in_page_order()[0]
    
    def getPager(self):
        """ Get the main pager widget"""
        return self.mainPageWidget

    def all_pages(self) -> list:
        """ Return a list of all the page widgets"""
        return self.pageRefs
