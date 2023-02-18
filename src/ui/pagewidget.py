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

# NOTE: There is some weird stuff with 3 pages. C++ deletes PageLabelWidgets
# even when the references are just fine. There are some sloppy fixes to
# get around this. Sorry. I'll continue to try and change this.

from PySide6.QtCore import QSize
from PySide6.QtGui import (QPixmap, Qt, QImage, QScreen )
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QWidget, QStackedWidget, QMainWindow, QVBoxLayout)
from qdb.keys import DbKeys
from ui.borderglow import BorderGlow


class PageDisplayMixin():
    """
        The mixin holds values that are used to control the page displays.

        This does not display"""
    PAGE_NONE = 0
    START_OF_BOOK = 0

    def setPageNumber(self, pgNumber: int = PAGE_NONE) -> None:
        self._pageNumber = pgNumber

    def pageNumber(self) -> int:
        return self._pageNumber if self._pageNumber is not None else self.START_OF_BOOK

    def setKeepAspectRatio(self, arg_1: bool) -> None:
        self._keepAspectRatio = arg_1

    def keepAspectRatio(self) -> bool:
        return self._keepAspectRatio

    def setClear(self, is_clear: bool) -> None:
        self._is_clear = is_clear

    def isClear(self) -> bool:
        """ Return the status of the page """
        return self._is_clear


class PageLabelWidget(QLabel, PageDisplayMixin):

    """ PageLabelWidget is the simple page handler routines for creating a QLabel and 
        populating it with images. It handles aspect ratio and helps keep state for 
        the PageWidget
    """

    def __init__(self, name: str = None):
        super().__init__()
        self.setPageNumber(self.START_OF_BOOK)
        self.setMargin(5)
        if (name is not None):
            self.setObjectName(name)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("")
        self.clear()

        self.setKeepAspectRatio(True)

    def setKeepAspectRatio(self, arg_1: bool) -> None:
        super().setKeepAspectRatio(arg_1)
        self.setScaledContents(not arg_1)

    def clear(self) -> None:
        """ Clear the label and set page number to None """
        super().clear()
        self.setClear(True)
        self.setPageNumber(self.PAGE_NONE)

    def setImage(self, newimage: str | QPixmap, page: int) -> bool:
        """
        Set the image for the label from a filename or a pixal map

        The file must exist or the load will fail. Check before calling
        """
        rtn = False
        if isinstance(newimage, QPixmap):
            rtn= self._set_image_pixmap(newimage, page)
        if isinstance(newimage, str):
            rtn= self._set_qimage_file( newimage , page )
        if rtn:
            self.setClear(False)
            self.setPageNumber(page)
        return rtn
    
    def _set_image_file(self, file_name:str , page: int )->bool:
        px = QPixmap()
        px.load(file_name)
        return self._set_image_pixmap(px, page)

    def _set_qimage_file( self, file_name:str , page: int )->bool:
        qimage = QImage()
        qimage.load( file_name )
        ratio = QApplication.primaryScreen().devicePixelRatio()
        size  = self.size()
        qimage.setDevicePixelRatio( ratio )
        if self.keepAspectRatio():
            qimage = qimage.scaled( int( size.width()*ratio), int(size.height()*ratio) , aspectMode=Qt.KeepAspectRatio , mode=Qt.SmoothTransformation) 
        else:
            qimage = qimage.scaled( int( size.width()*ratio), int(size.height()*ratio) )
        self.setPixmap( QPixmap.fromImage(qimage) ) 
        return True


    def _set_image_pixmap(self, px: QPixmap, pgNumber: int) -> bool:
        self.clear()
        if px is None or px is False or px.isNull() or not isinstance(px, QPixmap):
            return False
        if self.keepAspectRatio():
            new_px = px.scaled(
                self.size(), aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation)
            self.setPixmap(new_px)
            self.setMask(new_px.mask())
        else:
            self.setPixmap(px)
        return True

    def copyImage(self, otherPage):
        self.clear()
        if not otherPage.isClear():
            self.setPixmap(otherPage.pixmap())
            self.setClear(False)
            self.setPageNumber(otherPage.pageNumber())
        return not self.isClear()


class PageWidget():
    """ PageWidget will construct and handle two page layouts. 
        It handles all the construction, layout, and page flipping
        functions.
    """
    FORWARD = True
    BACKWARD = False

    LAYOUT_WIDTH = 'width'
    LAYOUT_HEIGHT = 'height'
    LAYOUT_PAGES = 'count'
    LAYOUT_SETUP = 'setup'
    LAYOUT_CREATE = 'layout'
    ALL_PAGES = 3

    def __init__(self, MainWindow: QMainWindow):
        self.borderGlow = BorderGlow()
        self._setupVars(MainWindow)
        self._set_size(MainWindow)

        self.createMainPageWidget()
        self.createPages()
        self.createPageLayouts(MainWindow)

        self.pageWidget = QStackedWidget(MainWindow)
        self.pageWidget.setObjectName(u"pageWidget")

        self.pageWidget.setSizePolicy(self.createPageSizePolicy())
        self.pageWidget.setAutoFillBackground(True)

        self.pageWidget.addWidget(self.mainPageWidget)

    def getMainPageWidget(self):
        return self.pageWidget

    def getPager(self):
        """ Get the main pager widget"""
        return self.mainPageWidget

    def setKeepAspectRatio(self, flag: bool) -> None:
        self.pageOne.setKeepAspectRatio(flag)
        self.pageTwo.setKeepAspectRatio(flag)
        self.pageThree.setKeepAspectRatio(flag)

    def keepAspectRatio(self) -> bool:
        return self.pageOne.keepAspectRatio()

    def _set_size(self, windowSize) -> bool:
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
                return True
        return self.windowWidth is not None and self.windowHeight is not None

    def resize(self, size=None) -> None:
        """ This must be called everytime the window is resized and on startup 
            You should pass the qsize or width in. It will be called on creation
            to set sizes correctly
        """
        if self._set_size(size) and self._currentLayoutMode:
            if self._set_size(size):
                self.page_width = int(
                    self.windowWidth / self._getLayoutValue(self.LAYOUT_WIDTH))
                self.page_height = int(
                    self.windowHeight / self._getLayoutValue(self.LAYOUT_HEIGHT))
            if self.page_width and self.page_height:
                self.pageOne.resize(self.page_width, self.page_height)
                self.pageTwo.resize(self.page_width, self.page_height)
                self.pageThree.resize(self.page_width, self.page_height)

    def _setupVars(self, MainWindow: QMainWindow):
        """ Set any variables that should be set before we startup
            This will not create any objects for display
        """
        self._layout = {
            DbKeys.VALUE_PAGES_SINGLE:  {
                self.LAYOUT_SETUP:  self.setDisplayOnePage,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES: 1},
            DbKeys.VALUE_PAGES_SIDE_2:  {
                self.LAYOUT_SETUP:  self.setDisplayTwoPageSide,
                self.LAYOUT_WIDTH:  2,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES: 2},
            DbKeys.VALUE_PAGES_SIDE_3:  {
                self.LAYOUT_SETUP:  self.setDisplayThreePagesSide,
                self.LAYOUT_WIDTH:  3,
                self.LAYOUT_HEIGHT: 1,
                self.LAYOUT_PAGES: 3},
            DbKeys.VALUE_PAGES_STACK_2: {
                self.LAYOUT_SETUP:  self.setDisplayTwoPagesStacked,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 2,
                self.LAYOUT_PAGES: 2},
            DbKeys.VALUE_PAGES_STACK_3: {
                self.LAYOUT_SETUP:  self.setDisplayThreePagesStacked,
                self.LAYOUT_WIDTH:  1,
                self.LAYOUT_HEIGHT: 3,
                self.LAYOUT_PAGES: 3},
        }

        self.direction = self.FORWARD
        self._currentLayout = None
        self._currentLayoutMode = None
        self.windowHeight = None
        self.windowWidth = None
        self.smartTurn = False

    def createPageSizePolicy(self) -> QSizePolicy:
        """ Create the page size policy used for the page display widget"""
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pageWidget.sizePolicy().hasHeightForWidth())
        return sizePolicy

    def createPages(self):
        """ Create the left and right pages """
        self.pageOne = PageLabelWidget(u"1")
        self.pageTwo = PageLabelWidget(u"2")
        self.pageThree = PageLabelWidget(u"3")

        self.pageRefs = [self.pageOne, self.pageTwo, self.pageThree]

    def createMainPageWidget(self) -> QWidget:
        """ This will create the main widget used to hold the pages"""
        self.mainPageWidget = QWidget()
        self.mainPageWidget.setObjectName(u"mainPageWidget")
        self.mainPageWidget.setEnabled(True)
        self.mainPageWidget.setVisible(True)
        self.mainPageWidget.grabGesture(Qt.SwipeGesture)
        return self.mainPageWidget

    def createSideBySideLayout(self):
        self.layoutPagesSide = QHBoxLayout()
        self.layoutPagesSide.setObjectName(u"horizontalLayoutWidget")
        self.layoutPagesSide.setContentsMargins(0, 0, 0, 0)

    def createStackedLayout(self):
        self.layoutPagesStacked = QVBoxLayout()
        self.layoutPagesStacked.setObjectName(u"VerticalLayoutWidget")
        self.layoutPagesStacked.setContentsMargins(0, 0, 0, 0)

    def createPageLayouts(self, MainWindow: QMainWindow) -> QWidget:
        """ Create the page layouts without adding the page widgets"""
        self.createSideBySideLayout()
        self.createStackedLayout()

    def hidePages(self) -> None:
        """ Remove both pages from the page layout """
        self._hidePageOne()
        self._hidePageTwo()
        self._hidePageThree()

    def _hidePageOne(self) -> None:
        """ Hide the left page and remove from current layout """
        # self._currentLayout.removeWidget(self.pageOne)
        # self.pageOne = None
        # self.pageOne = PageLabelWidget()
        if self.pageOne.isVisible():
            self._currentLayout.removeWidget(self.pageOne)
        self.pageOne.hide()

    def _hidePageTwo(self) -> None:
        """ Hide the right page and remove from current layout """
        if self.pageTwo.isVisible():
            self._currentLayout.removeWidget(self.pageTwo)
        self.pageTwo.hide()

    def _hidePageThree(self) -> None:
        """ Hide the right page and remove from current layout """
        if self.pageThree.isVisible():
            self._currentLayout.removeWidget(self.pageThree)
        self.pageThree.hide()

    def showPages(self) -> None:
        self._showPageOne()
        self._showPageTwo()
        self._showPageThree()

    def _showPageOne(self) -> None:
        self.pageOne = PageLabelWidget()
        if not self.pageOne.isVisible():
            self._currentLayout.addWidget(self.pageOne, 1)
            self._isShowingLeftPage = True
        self.pageOne.show()

    def _showPageTwo(self) -> None:
        """ Add and show the right page if this is not a single page layout and
            page not currently showing
        """
        if not self.pageTwo.isVisible():
            self._currentLayout.addWidget(self.pageTwo, 1)
        self.pageTwo.show()

    def _showPageThree(self) -> None:
        if not self.pageThree.isVisible():
            self._currentLayout.addWidget(self.pageThree, 1)
        self.pageThree.show()

    def _getLayoutValue(self, key):
        return self._layout[self._currentLayoutMode][key]

    def pageDisplay(self) -> int:
        return self._currentLayoutMode

    def all_pages(self) -> list:
        return [self.pageOne, self.pageTwo, self.pageThree]

    def page_numbers(self):
        """ Return a list of ALL the page numbers"""
        return [self.pageOne.pageNumber(), self.pageTwo.pageNumber(), self.pageThree.pageNumber()]

    def setDisplay(self, layout: str) -> None:
        """ Set the widget layout for display. Options are single, double, triple, side or stacked. """
        if layout in self._layout:
            self._setLayout(layout)
            self._layout[layout][self.LAYOUT_SETUP]()
        else:
            raise ValueError(
                "Internal error: Unknown layout requested {}".format(layout))

    def _removeCurrentLayout(self) -> None:
        if self._currentLayoutMode is not None and self._currentLayout is not None:
            # self.hidePages()                            # Remove all pages from layout
            QWidget().setLayout(self._currentLayout)  # Set current to dummy widget
            self._currentLayout = None

    def _setLayout(self, layout: str) -> None:
        """ This will set the page layout to be either side-by-side or stacked 
            If there is a setup mode already set, it will be removed and replaced
        """
        if self._currentLayoutMode != layout or True:
            self._removeCurrentLayout()
            self.createPages()
            self._currentLayoutMode = layout

            if layout == DbKeys.VALUE_PAGES_SINGLE:
                self.createSideBySideLayout()
                self._currentLayout = self.layoutPagesSide

            elif layout == DbKeys.VALUE_PAGES_SIDE_2:
                self.createSideBySideLayout()
                self._currentLayout = self.layoutPagesSide

            elif layout == DbKeys.VALUE_PAGES_STACK_2:
                self.createStackedLayout()
                self._currentLayout = self.layoutPagesStacked

            elif layout == DbKeys.VALUE_PAGES_SIDE_3:
                self.createSideBySideLayout()
                self._currentLayout = self.layoutPagesSide

            elif layout == DbKeys.VALUE_PAGES_STACK_3:
                self.createStackedLayout()
                self._currentLayout = self.layoutPagesStacked

            else:
                self.createSideBySideLayout()
                self._currentLayout = self.layoutPagesSide

            self.mainPageWidget.setLayout(self._currentLayout)

    def setDisplayOnePage(self) -> None:
        """ Setup a one page display, removing the right page from layout if present """
        self._setLayout(DbKeys.VALUE_PAGES_SINGLE)
        self._showPageOne()
        self.resize()

    def setDisplayTwoPageSide(self, showTwoPages: bool = True) -> None:
        """ Setup a two page display and make sure left and right are in layout"""
        self._setLayout(DbKeys.VALUE_PAGES_SIDE_2)
        self._showPageOne()
        self._showPageTwo()
        self.resize()

    def setDisplayThreePagesSide(self, showThreePagesSide: bool = True) -> None:
        self._setLayout(DbKeys.VALUE_PAGES_SIDE_3)
        self._showPageOne()
        self._showPageTwo()
        self._showPageThree()
        self.resize()

    def setDisplayTwoPagesStacked(self) -> None:
        self._setLayout(DbKeys.VALUE_PAGES_STACK_2)
        self._showPageOne()
        self._showPageTwo()
        self.resize()

    def setDisplayThreePagesStacked(self) -> None:
        self._setLayout(DbKeys.VALUE_PAGES_STACK_3)
        self._showPageOne()
        self._showPageTwo()
        self._showPageThree()
        self.resize()

    def setSmartPageTurn(self, state: bool) -> bool:
        """ Set the smart turn feature and return the previous state """
        rtn = self.smartTurn
        self.smartTurn = state
        return rtn

    def clear(self):
        """ Clear both left and right pages but do not remove them from layout"""
        self.borderGlow.stopBorderGlow()
        self.pageOne.clear()
        self.pageTwo.clear()
        self.pageThree.clear()

    def _rollForward(self, pg: int) -> bool:
        """
            OK, so we have up to 'n' pages loaded but on 'p' pages are 
            displayed. If we have the page already, promote that by 'rolling'
            forward.
            * page must be in list of pages held
            * can't be displaying all of the pages
            * page isn't displayed
        """
        roll = False
        while (pg in self.page_numbers() and
                not self.isShown(pg) and
                self._getLayoutValue(self.LAYOUT_PAGES) != self.ALL_PAGES
               ):
            roll = True
            self.pageOne.copyImage(self.pageTwo)
            self.pageTwo.copyImage(self.pageThree)
            self.pageThree.clear()
        return roll

    def _rollForwardZeros(self, endpage: int):
        if endpage != 0:
            while self.pageOne.pageNumber() == 0:
                self.pageOne.copyImage(self.pageTwo)
                self.pageTwo.copyImage(self.pageThree)
                self.pageThree.clear()

    def _simpleNextPage(self, px: QPixmap, pg: int):
        pageshown = self.numberPages()
        if pageshown == 1:
            self.pageOne.setImage(px, pg)
        elif pageshown == 2:
            self.pageOne.copyImage(self.pageTwo)
            self.pageTwo.setImage(px, pg)
        else:
            self.pageOne.copyImage(self.pageTwo)
            self.pageTwo.copyImage(self.pageThree)
            self.pageThree.setImage(px, pg)

    def numberPages(self) -> int:
        """ Return how many pages will be shown for this layout """
        if self._currentLayoutMode == None:
            return None
        return self._layout[self._currentLayoutMode][self.LAYOUT_PAGES]

    def _simplePreviousPage(self, px: QPixmap, pg: int):
        self.pageThree.copyImage(self.pageTwo)
        self.pageTwo.copyImage(self.pageOne)
        self.pageOne.setImage(px, pg)

    def _smartPage(self, plw: PageLabelWidget, px: QPixmap, pg: int) -> None:
        self.borderGlow.stopBorderGlow()
        plw.setImage(px, pg)
        self.borderGlow.startBorderGlow(plw)

    def loadPages(self, px1: QPixmap, pg1: int, px2: QPixmap, pg2: int, px3: QPixmap, pg3: int):
        """ loadPages should be called whenever a book is opened. It setups for
            either 'smart' page turn or for simple page turning.
        """
        self.clear()
        self.resize()
        self.direction = self.FORWARD
        self.pageOne.setImage(px1, pg1)
        if self.numberPages() > 1:
            self.pageTwo.setImage(px2, pg2)
            if self.numberPages() > 2:
                self.pageThree.setImage(px3, pg3)

    def page_numbers_displayed(self):
        return self.page_numbers()[0:self.numberPages()]

    def _find_page_by_pagenumber(self, page_number: int) -> PageLabelWidget:
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

    def staticPage(self, px) -> None:
        """ Used only to display a static 'info' page """
        self.setDisplayOnePage()
        self.pageOne.setImage(px, None)

    def nextPage(self, px: QPixmap, pg: int, end: bool = False):
        if end and self.isShown(pg):
            return
        if self.smartTurn and self.numberPages() > 1:
            self._smartPage(self.lowestPageLabelWidget(), px, pg)
        else:
            self._simpleNextPage(px, pg)
        self.direction = self.FORWARD

    def previousPage(self, px: QPixmap, pg: int, end: bool = False):
        if end and self.isShown(pg):
            return
        if self.smartTurn and self.numberPages() > 1:
            self._smartPage(self.highestPageLabelWidget(), px, pg)
        else:
            self._simplePreviousPage(px, pg)
        self.direction = self.BACKWARD

    def getHighestPageShown(self):
        return max(self.page_numbers_displayed())

    def getLowestPageShown(self):
        """ Return the lowest page in the array that can be seen"""
        return min(self.page_numbers_displayed())

    def getPageForPosition(self, position):
        return self.page_numbers()[position-1]

    def isShown(self, page: int) -> dict:
        return page in self.page_numbers_displayed()

    def get_widgets_in_page_order(self) -> list[PageLabelWidget]:
        """ 
        Return the widgets in page order

        Created to handle any number of pages. Bit over the top but didn't
        want to rewrite it again.
        """

        pnum = self.numberPages()
        if pnum == 1:
            return [self.pageOne]

        key_pages = {}
        ordered = []

        for page in [self.pageOne, self.pageTwo, self.pageThree][0: pnum]:
            key_pages[page.pageNumber()] = page

        for key in sorted(key_pages):
            ordered.append(key_pages[key])
        return ordered

    def highestPageLabelWidget(self, offset: int = 0) -> PageLabelWidget:
        ordered = self.get_widgets_in_page_order()
        index = max(len(ordered)-1-offset, 0)
        return ordered[index]

    def lowestPageLabelWidget(self) -> PageLabelWidget:
        return self.get_widgets_in_page_order()[0]
