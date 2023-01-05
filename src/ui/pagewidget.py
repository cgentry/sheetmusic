# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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

from PySide6.QtCore    import QSize
from PySide6.QtGui     import ( QPixmap, Qt )
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QSizePolicy,
    QWidget, QStackedWidget, QMainWindow, QVBoxLayout)
from qdb.keys          import DbKeys
from ui.borderglow     import BorderGlow


class PageLabelWidget(QLabel):
    END_OF_BOOK=999
    START_OF_BOOK=0
    """ PageLabelWidget is the simple page handler routines for creating a QLabel and 
        populating it with images. It handles aspect ratio and helps keep state for 
        the PageWidget
    """
    def __init__(self, name:str=None):
        super().__init__()
        self.setPageNumber( self.START_OF_BOOK )
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.setMargin(5)
        if ( name is not None ):
                self.setObjectName( name)
        self._keepAspectRatio = True
        self.setStyleSheet("")
        self.clear()

    def setKeepAspectRatio( self, arg_1:bool )->None:
        self._keepAspectRatio = arg_1
        self.setScaledContents( ( not self._keepAspectRatio ) )
    
    def keepAspectRatio(self)->bool:
        return self._keepAspectRatio

    def clear(self)->None:
        """ Clear the label and set page number to None """
        super().clear()
        self._isClear = True
        self.setPageNumber()

    def isClear(self)->bool:
        """ Return the status of the page """
        return self._isClear

    def setImage(self, px:QPixmap, pgNumber:int)->bool:
        self.clear()
        if px is None or px is False or px.isNull():
            self.setPageNumber( self.END_OF_BOOK)
            return False

        if self._keepAspectRatio:
            self.setPixmap( px.scaled( self.size() , aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation ) )
        else:
            self.setPixmap( px )
        self._isClear = False
        self.setPageNumber( pgNumber )
        return True

    def setPageNumber( self, pgNumber:int=None )->None:
        self._pageNumber = pgNumber

    def pageNumber(self)->int:
        return self._pageNumber if self._pageNumber is not None else self.START_OF_BOOK

class PageWidget():
    """ PageWidget will construct and handle two page layouts. 
        It handles all the construction, layout, and page flipping
        functions.
    """
    FORWARD       = True
    BACKWARD      = False
    LAYOUT_SINGLE = DbKeys.VALUE_PAGES_SINGLE
    LAYOUT_DOUBLE = DbKeys.VALUE_PAGES_DOUBLE
    LAYOUT_SIDE   = DbKeys.VALUE_PAGES_DOUBLE
    LAYOUT_STACKED= DbKeys.VALUE_PAGES_STACKED

    def __init__(self, MainWindow:QMainWindow):

        self.borderGlow = BorderGlow()
        self._setupVars( MainWindow )
        self._setSize( MainWindow )
        
        self.createMainPageWidget()
        self.createPages()
        self.createPageLayouts(MainWindow) 

        self.pageWidget = QStackedWidget(MainWindow)
        self.pageWidget.setObjectName(u"pageWidget")

        self.pageWidget.setSizePolicy(self.createPageSizePolicy())
        self.pageWidget.setAutoFillBackground(True)

        self.pageWidget.addWidget( self.mainPageWidget)

    def getMainPageWidget(self):
        return self.pageWidget

    def getPager(self):
        """ Get the main pager widget"""
        return self.mainPageWidget

    def setKeepAspectRatio(self, flag:bool)->None:
        self.left.setKeepAspectRatio( flag )
        self.right.setKeepAspectRatio( flag )

    def keepAspectRatio( self )->bool:
        return self.left.keepAspectRatio()

    def _setSize( self, windowSize )->bool:
        """ Save the size for the main window. This will accept
            QMainWindow, QSize. Do not call this
            directly; resize will call it and it should be called first
        """
        if windowSize is not None:
            if isinstance( windowSize , QMainWindow ):
                windowSize = windowSize.size()
            if isinstance( windowSize, QSize ):
                self.windowWidth = windowSize.width()
                self.windowHeight = windowSize.height()
                return True
        return self.windowWidth is not None and self.windowHeight is not None

    def resize( self, size=None )->None:
        """ This must be called everytime the window is resized and on startup 
            You should pass the qsize or width in. It will be called on creation
            to set sizes correctly
        """
        if self._setSize( size ):
            if self._currentLayoutMode == self.LAYOUT_STACKED:
                self.page_width = self.windowWidth
                self.page_height = self.windowHeight/2 if self._isShowingRightPage else self.windowHeight
            elif self._currentLayoutMode == self.LAYOUT_SIDE:
                self.page_width = self.windowWidth/2 if self._isShowingRightPage else self.windowWidth
                self.page_height = self.windowHeight
            else: # self.LAYOUT_SINGLE
                self.page_width  = self.windowWidth
                self.page_height = self.windowHeight

        if self.page_width and self.page_height:
            self.left.resize( self.page_width , self.page_height  )
            if self._isShowingRightPage:
                self.right.resize( self.page_width , self.page_height )
                 
    def _setupVars(self, MainWindow:QMainWindow ):
        """ Set any variables that should be set before we startup
            This will not create any objects for display
        """
        self.direction = self.FORWARD
        self._isShowingRightPage = False
        self._isShowingLeftPage = False
        self.smartTurn = False
        self._currentLayoutMode = None
        self.windowHeight = None
        self.windowWidth = None
        self.setSmartPageTurn( False )

    def createPageSizePolicy(self)->QSizePolicy:
        """ Create the page size policy used for the page display widget"""
        sizePolicy = QSizePolicy( QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth( self.pageWidget.sizePolicy().hasHeightForWidth())
        return sizePolicy

    def createPages(self):
        """ Create the left and right pages """
        self.left  = PageLabelWidget(u"left")
        self.right = PageLabelWidget(u"right")
  

    def createMainPageWidget(self)->QWidget:
        """ This will create the main widget used to hold the pages"""
        self.mainPageWidget = QWidget()
        self.mainPageWidget.setObjectName(u"mainPageWidget")
        self.mainPageWidget.setEnabled(True)
        self.mainPageWidget.setVisible(True)
        self.mainPageWidget.grabGesture(Qt.SwipeGesture)
        return self.mainPageWidget

    def createSideBySideLayout( self ):
        self.twoPagesSideLayout = QHBoxLayout()
        self.twoPagesSideLayout.setObjectName(u"horizontalLayoutWidget")
        self.twoPagesSideLayout.setContentsMargins(0, 0, 0, 0)

    def createStackedLayout(self):
        self.twoPagesStackedLayout = QVBoxLayout()
        self.twoPagesStackedLayout.setObjectName(u"VerticalLayoutWidget")
        self.twoPagesStackedLayout.setContentsMargins(0, 0, 0, 0)

    def createPageLayouts(self, MainWindow:QMainWindow)->QWidget:
        """ Create the page layouts without adding the page widgets"""
        self.createSideBySideLayout()
        self.createStackedLayout()
    
    def hidePages(self)->None:
        """ Remove both pages from the page layout """
        self._hideLeftPage()
        self._hideRightPage()

    def _hideLeftPage(self)->None:
        """ Hide the left page and remove from current layout """
        self.left.hide()
        if self._isShowingLeftPage:
            self._currentLayout.removeWidget(self.left)
            self._isShowingLeftPage = False

    def _hideRightPage(self)->None:
        """ Hide the right page and remove from current layout """
        self.right.hide()
        if self._isShowingRightPage:
            self._currentLayout.removeWidget(self.right)
            self._isShowingRightPage = False

    def showPages(self)->None:
        self._showLeftPage()
        self._showRightPage()

    def _showLeftPage(self)->None:
        if not self._isShowingLeftPage :
            self._currentLayout.addWidget(self.left, 1)
            self._isShowingLeftPage = True
        self.left.show()

    def _showRightPage(self)->None:
        """ Add and show the right page if this is not a single page layout and
            page not currently showing
        """
        if self._currentLayout != self.LAYOUT_SINGLE:
            if not self._isShowingRightPage:
                self._currentLayout.addWidget(self.right, 1)
                self._isShowingRightPage = True
            self.right.show()

    def pageDisplay(self)->int:
        return self._currentLayoutMode
    
    def setDisplay( self, layout:int=2)->None:
        """ Set the widget layout for display. Options are single, side or stacked. """
        if layout == self.LAYOUT_SINGLE:
            self.setDisplayOnePage()
        elif layout == self.LAYOUT_SIDE:
            self.setDisplayTwoPage()
        elif layout == self.LAYOUT_STACKED:
            self.setDisplayStacked()

    def _removeCurrentLayout(self)->None:
        if self._currentLayoutMode is not None and self._currentLayout is not None:
            self.hidePages()                            # Remove all pages from layout
            QWidget().setLayout( self._currentLayout )  # Set current to dummy widget
            self._currentLayout = None

    def _setLayout( self, layout:int=2)->None:
        """ This will set the page layout to be either side-by-side or stacked 
            If there is a setup mode already set, it will be removed and replaced
        """
        if self._currentLayoutMode != layout :
            self._removeCurrentLayout()
            self._currentLayoutMode = layout

            if layout == self.LAYOUT_SINGLE:
                self.createSideBySideLayout()
                self._currentLayout = self.twoPagesSideLayout

            elif layout == self.LAYOUT_SIDE:
                self.createSideBySideLayout()
                self._currentLayout = self.twoPagesSideLayout

            if layout == self.LAYOUT_STACKED:
                self.createStackedLayout()
                self._currentLayout = self.twoPagesStackedLayout

            else:
                self.createSideBySideLayout()
                self._currentLayout = self.twoPagesSideLayout

            self.mainPageWidget.setLayout( self._currentLayout )

            
    def setDisplayOnePage( self )->None:
        """ Setup a one page display, removing the right page from layout if present """
        self._setLayout(  self.LAYOUT_SINGLE )
        self._showLeftPage()
        self.resize()

    def setDisplayTwoPage( self, showTwoPages:bool=True )->None:
        """ Setup a two page display and make sure left and right are in layout"""
        self._setLayout( self.LAYOUT_SIDE )
        self._showLeftPage()
        self._showRightPage()
        self.resize()

    def setDisplayStacked( self )->None:
        self._setLayout(  self.LAYOUT_STACKED )
        self._showLeftPage()
        self._showRightPage()
        self.resize()
    
    def setSmartPageTurn(self , state:bool)->bool:
        """ Set the smart turn feature and return the previous state """
        rtn = self.smartTurn
        self.smartTurn = state
        return rtn

    def clear(self):
        """ Clear both left and right pages but do not remove them from layout"""
        self.borderGlow.stopBorderGlow()
        self.left.clear()
        self.right.clear()

    def _simpleNextPage( self, px:QPixmap, pg:int):
        self.left.setImage( self.right.pixmap() , self.right.pageNumber() )
        if px is None or px is False or px.isNull():
            self.setDisplayOnePage()
        else:
            self.right.setImage( px , pg )

    def _simplePreviousPage( self, px:QPixmap, pg:int):
        if px is None or px is False or px.isNull():
            self.setDisplayOnePage()
        else:
            self.right.setImage( self.left.pixmap() , self.left.pageNumber() )
            self.left.setImage( px, pg  )

    def _smartPage(self, plw:PageLabelWidget, px:QPixmap, pg:int )->None:
        self.borderGlow.stopBorderGlow()
        plw.setImage( px , pg )
        self.borderGlow.startBorderGlow( plw )

    def loadPages( self, pxLeft:QPixmap, pgLeft:int, pxRight:QPixmap , pgRight:int):
        """ loadPages should be called whenever a book is opened. It setups for
            either 'smart' page turn or for simple page turning.
        """
        self.clear()
        self.resize()
        self.direction = self.FORWARD
        self.left.setImage(  pxLeft, pgLeft )
        self.right.setImage( pxRight, pgRight )

    def staticPage(self , px )->None:
        """ Used only to display a static 'info' page """
        self.setDisplayOnePage()
        self.left.setImage( px , None)

    def nextPage( self, px:QPixmap , pg:int):
        if self.smartTurn and self._isShowingRightPage:
            self._smartPage( self.lowestPageLabelWidget(), px, pg )
        else:
            self._simpleNextPage( px, pg )
        self.direction = self.FORWARD

    def previousPage( self, px:QPixmap , pg:int):
        if self.smartTurn and self._isShowingRightPage:
            self._smartPage( self.highestPageLabelWidget(), px, pg )
        else:
            self._simplePreviousPage( px, pg )
        self.direction = self.BACKWARD

    def getHighestPageShown(self):
        if self._isShowingRightPage:
            return max( self.left.pageNumber() , self.right.pageNumber() )
        return self.left.pageNumber()
    
    def getLowestPageShown(self):
        if self._isShowingRightPage:
            return min( self.left.pageNumber() , self.right.pageNumber() )
        return self.left.pageNumber()
    
    def highestPageLabelWidget(self)->PageLabelWidget:
        if not self._isShowingRightPage or self.left.pageNumber() > self.right.pageNumber():
            return self.left
        return self.right

    def lowestPageLabelWidget(self)->PageLabelWidget:
        if not self._isShowingRightPage or self.left.pageNumber() < self.right.pageNumber():
            return self.left
        return self.right
