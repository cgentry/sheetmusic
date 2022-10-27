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

"""
    SheetMusic is a program to display music on a monitor. It uses
    PNGs (normally) and flips pages. A simple program in Python and QT
"""

import gc
from genericpath import isfile
import sys
import os
import logging
from tkinter import N

from PySide6.QtCore     import QEvent, QObject, Qt, QTimer, QDir, QTimer
from PySide6.QtWidgets  import QApplication, QMainWindow,  QMessageBox, QDialog, QLabel, QFileDialog

from qdb.dbconn         import DbConn
from qdb.dbsystem       import DbSystem
from qdb.keys           import BOOK, BOOKPROPERTY, BOOKMARK, DbKeys
from qdb.setup          import Setup

from qdil.preferences   import DilPreferences, SystemPreferences
from qdil.book          import DilBook
from qdil.bookmark      import DilBookmark

from ui.main            import UiMain
from ui.properties      import UiProperties
from ui.bookmark        import UiBookmark
from ui.file            import Openfile, Deletefile, DeletefileAction, Reimportfile

from util.convert       import toBool

class MainWindow(QMainWindow):
    timer_interval = 25
    colour_pallet = [ '#236dc9','#236dc9','#1c58a1','#174781','#133968','#102e54',
                      '#0d2544','#0b1e37','#09182c','#081424','#07101d','#060d18',
                      '#000000' ]

    def __init__(self):
        super().__init__()
        self.is_forward = False
        self.is_backward = False
        self.page_left = None
        self.page_right = None
        self.smart_pages = False
        
        self.border_label = None
        self.border_colour_index = 0

        self.border_timer = QTimer()
        self.border_timer.setInterval( self.timer_interval )
        self.border_timer.setSingleShot(True)
        self.border_timer.timeout.connect(self.onTimer)

        self.loadUi()
        self.book = DilBook()
        self.system = DbSystem()
        self.bookmark = DilBookmark()
        self.logger = logging.getLogger('main')
        

    def loadUi(self)->None:
        self.pref = DilPreferences()
        self.settings = self.pref.getAll()
        self.ui = UiMain()
        self.ui.setupUi(self)

    def _pageLabel( self, label:QLabel, bookpage )->bool:
        label.clear()
        if bookpage > self.book.getTotal():
            return True
        px = self.book.getPixmap(bookpage )
        if px is None or px is False or px.isNull():
            
            label.setText("<h1>IMAGE NOT AVAILABLE</h1>")
            msg = "Could not open page {}.\nTry to re-import at lower resolution".format( bookpage )
            QMessageBox.critical(None, "Image Error", msg , QMessageBox.Close )
            return False
        keepAspectRatio = self.book.getAspectRatio()
        label.setScaledContents( ( not keepAspectRatio ) )
        if keepAspectRatio:
            size = self.ui.mainWindow.size()
            if self.ui.isRightPageShown():
                size.setWidth( size.width()/2 )
            label.resize( size )
            px = px.scaled( size , aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation )
        label.setPixmap( px )
        return True

    def setBorderColour(self):
        if self.border_label is not None:
            if self.border_colour_index < len( self.colour_pallet ):
                backgroundColour =  "background: {};".format( self.colour_pallet[ self.border_colour_index ] )
                self.border_colour_index = self.border_colour_index+1
                self.border_label.setStyleSheet( backgroundColour )
                self.border_timer.start()
            else:
                self.clearBorderColour()

    def clearBorderColour(self):
        self.border_colour_index = 0
        if self.border_label is not None:
            self.border_label.setStyleSheet("")
            self.border_label = None

    def pageImageLeft(self, pagenumber)->bool:
        """ Display the left page image """
        self.page_left = pagenumber 
        return self._pageLabel( self.ui.left ,self.page_left )

    def pageImageRight(self, pagenumber )->bool:
        """ Display the right page image when doing two page display"""
        if self.ui.isRightPageShown():
            self.page_right = pagenumber
            return self._pageLabel( self.ui.right ,self.page_right )
        return True

    def showOnePage( self, pagenumber ):
        return self.pageImageLeft( pagenumber )

    def showSmartPages( self, pagenumber ):
        if self.page_left < self.page_right:
            if self.is_forward:
                rtn = self.pageImageLeft( pagenumber )
                self.border_label = self.ui.left
            if self.is_backward:
                rtn = self.pageImageRight( pagenumber)
                self.border_label = self.ui.right
        else:
            if self.is_forward:
                rtn = self.pageImageRight( pagenumber )
                self.border_label = self.ui.right
            if self.is_backward:
                rtn = self.pageImageLeft( pagenumber )
                self.border_label = self.ui.left
        self.setBorderColour()
        return rtn
        

    def showTwoPages( self, pagenumber , absolute=True):
        if absolute or self.page_left is None or self.page_right is None or not self.smart_pages:
            return self.pageImageLeft( pagenumber ) and self.pageImageRight(pagenumber+1)
        return  self.showSmartPages( pagenumber )
        

    def showPages(self, delay:bool=False, absolute=True)->bool:
        """ Show left and right pages (if enabled) This will also allow "page-flip"
            display. 
            Absolute is: 
                    True: show page n and n+1
                    False: If showing two pages:
                        left goes to page n+1, gets border (when page_odd is true)
                        right toes to page n+1, gets border (when page_odd is false)
                    page_odd is flipped back and forth but reset when True
            """
        if self.book.isOpen() :
            if absolute: # simple page display, no page movement
                self.is_forward = False
                self.is_backward = False
            self.blockSignals( True )
            page = self.book.getAbsolutePage()
            self.clearBorderColour()
            try:
                if self.ui.isRightPageShown():
                    if absolute or not self.smart_pages or page == 1 or page >= self.book.getTotal() :
                        pages_shown = self.showTwoPages( page , absolute=True )
                        if self.smart_pages:
                            self.book.setPageNumber( page+1)
                    else:
                        pages_shown = self.showSmartPages( page )
                else:
                     pages_shown = self.showOnePage( page )

                if  pages_shown :
                    self.updateStatusBar()
            except:
                self.closeBook()
            finally:
                gc.collect(2)
                self.blockSignals( False )
        return self.book.isOpen()

    def updatePageNumbers(self, absolutePageNumber:int=None )->None:
        if  self.book.isPageRelative(absolutePageNumber):
            self.ui.lblPageAbsolute.setText( " |{:4d} |".format( absolutePageNumber ))
            lbl = "Page"
        else:
            self.ui.lblPageAbsolute.clear()
            lbl = "Book page"
        self.ui.lblPageRelative.setText( "{}: {:d}".format( lbl, self.book.getRelativePage(absolutePageNumber)))
        
    def updateBookmarkMenuNav( self, bookmark=None ):
        if self.bookmark.getTotal() < 1 :
            self.ui.actionPreviousBookmark.setDisabled(True)
            self.ui.actionNextBookmark.setDisabled(True)
        if bookmark is not None:
            self.ui.actionPreviousBookmark.setDisabled( self.bookmark.isFirst( bookmark) )
            self.ui.actionNextBookmark.setDisabled( self.bookmark.isLast( bookmark ))

    def updateStatusBar(self)->None:
        absolutePageNumber = self.book.getAbsolutePage()

        if  self.book.isPageRelative(absolutePageNumber):
            self.ui.lblPageAbsolute.setText( " |{:4d} |".format( absolutePageNumber))
            lbl = "Page"
        else:
            self.ui.lblPageAbsolute.clear()
            lbl = "Book page"
        self.ui.lblPageRelative.setText( "{}: {:d}".format( lbl, self.book.getRelativePage()))
        #self.updateBookmarkMenuNav( self.bookmakr )

        self.ui.statusProgress.setMaximum( self.book.getTotal())
        self.ui.statusProgress.setValue( absolutePageNumber)

    def clearLabels(self)->None:
        self.ui.left.text = ""
        self.ui.right.text = ""

    def restoreWindowFromSettings(self)->None:
        self.pref.restoreMainWindow( self.ui.getWindow() ) 
        self.pref.restoreShortcuts( self.ui )  
        self.actionViewStatusBar( self.pref.getValueBool( DbKeys.SETTING_WIN_STATUS_ENABLED , True ))
            
    def openBook(self, newBookName:str, page=None):
        """ """
        self.closeBook()
        rtn = self.book.openBook(newBookName, page )
        if rtn == QMessageBox.Ok:
            self._setPageLayout( self.book.getPropertyOrSystem( BOOKPROPERTY.layout) )
            self.smart_pages = toBool( self.book.getPropertyOrSystem( DbKeys.SETTING_SMART_PAGES ) )
            
            if self.showPages( absolute=True):
                self.setTitle()
                self.setMenusForBook(True)
                self.bookmark.open( newBookName )
                self.updateBookmarkMenuNav( self.bookmark.getBookmarkPage( page ))
                self.ui.actionAspectRatio.setChecked(  self.book.getAspectRatio()  )
                self.ui.actionSmartPages.setChecked( self.smart_pages )
        return rtn

    def closeBook(self)->None:
        """ Close the book, save a pointer to it, and hide the menu items. """
        if self.book.isOpen():
            self.pref.setValue( DbKeys.SETTING_LAST_BOOK_NAME , self.book.getTitle())
            self.book.closeBook()
        self.setMenusForBook(False)
        self.ui.mainWindow.hide()

    def setupWheelTimer(self)->None:
        self.wheelTimer = QTimer(self)
        self.wheelTimer.setInterval( 1000 ) # 500 msec == .5 seconds
        self.wheelTimer.setSingleShot(True)
        self.direction = None

    def eventFilter(self, object:QObject, event:QEvent)->bool:
        if (event.type() == QEvent.Gesture):
            object.blockSignals(True)
            if( event.GestureType() ==Qt.SwipeGesture ):
                if (event.horizontalDirection() == 'Left'):
                    self.pageBackward()
                if (event.horizontalDirection() == 'Right'):
                    self.pageForward()
                object.blockSignals(False)
                return True
        ###
        ### TODO: Need a better way to reduce page flips, otherwise
        ###         the screen acts erratic.
        ###
        if ( event.type() == QEvent.Wheel) :
            object.blockSignals(True)
            if not self.wheelTimer.isActive():
                # block wheel activies for a time
                # we end up with LOADS of events and it 
                # sometimes goes to zero, then back up, then zero 
                pnt = event.angleDelta()
                x = pnt.x()
                if x == 0:
                    if self.direction is not None:
                        self.wheelTimer.start()
                        if self.direction == 'Left':
                            self.pageBackward()
                        else:
                            self.pageForward()
                        
                        self.direction = None
                else:
                    if  x < 0 :
                        self.direction = 'Left'
                    else:  
                        self.direction = 'Right'
            object.blockSignals(False)
            return True
        ## End Wheel

        return False
    
    def resizeEvent(self,event):
        if self.ui.isRightPageShown() is not None:
            self.showPages( absolute=True)

    def keyPressEvent(self, ev)->None:
        #if False and (ev.type() == QEvent.KeyPress):
        #    key = ev.key()
        #    if (key == Qt.Key_Left):
        #        self.goFirstBookmark() if ev.modifiers() & Qt.ControlModifier else self.pageBackward()
        #    if (key == Qt.Key_Right):
        #        self.goLastBookmark() if ev.modifiers() & Qt.ControlModifier else self.pageForward()

        super().keyPressEvent(ev)

    def closeEvent(self, event)->None:
        """ called when the program is closed """
        pref = DilPreferences()
        pref.saveMainWindow( self.ui.mainWindow)
        self.closeBook()
        DbConn.closeDB()

    def pageBackward(self)->None:
        self.is_backward=True
        self.is_forward=False
        self.book.incPageNumber(-1)
        self.showPages(absolute=False)

    def pageForward(self)->None:
        self.is_backward=False
        self.is_forward=True
        self.book.incPageNumber(1)
        self.showPages(True, absolute=False)
    
    def goToPage(self, page )->None:
        ''' Set the page number to the page passed and display
            page number must be absolute, not relative.
        '''
        self.book.setPageNumber(page)
        self.showPages( absolute=True)

    def goFirstBookmark(self)->None:
        bmk = self.bookmark.getFirst( )
        self.book.setPageNumber(bmk[BOOKMARK.page])
        self.showPages(absolute=True)

    def goLastBookmark(self)->None:
        bmk = self.bookmark.getLast( )
        self.book.setPageNumber(bmk[BOOKMARK.page])
        self.showPages(absolute=True)

    def goFirstPageShown(self)->None:
        self.book.setPageNumber(self.book.getFirstPageShown() )
        self.showPages(absolute=True)

    def goLastPageShown(self)->None:
        self.book.setPageNumber( self.book.getLastPageShown())
        self.showPages(absolute=True)

    def connectMenus(self)->None:
        """ Connect menus and events to the routines handling the function"""
        self.ui.actionBookmarkCurrentPage.triggered.connect(self.actionMakeBookmark)
        self.ui.actionShowBookmarks.triggered.connect(self.actionShowBookmark)
        self.ui.actionAdd_Bookmark.triggered.connect(self.actionAddBookmark)
        self.ui.actionCleanDB.triggered.connect( self.actionCleanDB )
        self.ui.actionDumpDB.triggered.connect( self.actionDumpDB )
        #self.ui.actionBookmark.triggered.connect(self.actionGoBookmark)
        self.ui.actionPreviousBookmark.triggered.connect( self.goPreviousBookmark )
        self.ui.actionNextBookmark.triggered.connect( self.goNextBookmark )
        self.ui.lblBookmark.clicked.connect( self.actionClickedBookmark )

        self.ui.actionOpen.triggered.connect(self.actionFileOpen)
        self.ui.menuOpen_Recent.aboutToShow.connect( self.actionOpenRecentUpdateFiles)
        self.ui.menuOpen_Recent.triggered.connect(self.actionOpenRecent)
        self.ui.actionProperties.triggered.connect(self.actionProperties)
        self.ui.actionDeleteAllBookmarks.triggered.connect( self.actionDeleteAllBookmarks )
        self.ui.actionPreferences.triggered.connect(self.actionPreferences)
        self.ui.actionAbout.triggered.connect( self.actionAbout )
        self.ui.actionHelp.triggered.connect( self.actionHelp)
        self.ui.actionClose.triggered.connect(self.actionClose)
        self.ui.actionDelete.triggered.connect( self.actionDelete )
        
        self.ui.actionFirstPage.triggered.connect( self.goFirstPageShown )
        self.ui.actionLastPage.triggered.connect( self.goLastPageShown )

        self.ui.actionOne_Page.triggered.connect( self.actionOnePage)
        self.ui.actionTwo_Pages.triggered.connect( self.actionTwoPages)
        self.ui.actionViewStatus.triggered.connect(self.actionViewStatusBar)
        self.ui.actionAspectRatio.triggered.connect(self.actionAspectRatio)
        self.ui.actionSmartPages.triggered.connect( self.actionSmartPages )

        self.ui.actionGo_to_Page.triggered.connect(self.actionGoPage)
        self.ui.actionDown.triggered.connect(self.pageForward)
        self.ui.actionUp.triggered.connect( self.pageBackward)

        self.ui.statusProgress.valueChanged.connect( self.actionProgressChanged)
        self.ui.statusProgress.sliderReleased.connect(self.actionProgressReleased)

        self.ui.twoPagesSide.installEventFilter( self)

        self.ui.actionImportPDF.triggered.connect(self.actionImportPDF)
        self.ui.actionImportDirectory.triggered.connect( self.actionImportDirectory )
        self.ui.actionCheckIncomplete.triggered.connect( self.actionCheckIncomplete )
        self.ui.actionReimportPDF.triggered.connect( self.actionReimportPDF )

    def setMenusForBook(self, show=True)->None:
        """ Enable menus when file is open"""
        self.ui.actionProperties.setEnabled( show )
        self.ui.actionClose.setEnabled(show)
        self.ui.actionBookmarkCurrentPage.setEnabled(show)
        self.ui.actionShowBookmarks.setEnabled(show)
        #self.ui.actionBookmark.setEnabled(show)
        self.ui.actionUp.setEnabled(show)
        self.ui.actionDown.setEnabled(show)
        self.ui.actionGo_to_Page.setEnabled(show)
        self.ui.actionOne_Page.setEnabled(show)
        self.ui.actionTwo_Pages.setEnabled(show)
        
    def openLastBook(self)->None:
        if self.pref.getValueBool( DbKeys.SETTING_LAST_BOOK_REOPEN, True) :
            recent = self.book.getRecent()
            if recent is not None and len(recent) > 0 :
                self.openBook(recent[0][BOOK.name])    

    def setTitle( self, bookmark=None )->None:
        """ Title is made of the title and bookmark if there is one """
        title = "SheetMusic: " + self.book.getTitle()
        if bookmark:
            title = "{} - {}".format( title, bookmark)
        self.ui.mainWindow.setWindowTitle( title )
        self.ui.mainWindow.show()
    
    def _finishBookmarkNavigation( self, bmk ):
        if bmk is not None and BOOKMARK.page in bmk and bmk[BOOKMARK.page] is not None:
            self.ui.actionPreviousBookmark.setDisabled( self.bookmark.isFirst(bmk) )
            self.ui.actionNextBookmark.setDisabled( self.bookmark.isLast( bmk ) )
            if bmk[BOOKMARK.page] is not None:
                self.goToPage( bmk[BOOKMARK.page])

    def goPreviousBookmark(self)->None:
        bmk = self.bookmark.getPrevious( self.book.getAbsolutePage() )
        self._finishBookmarkNavigation(bmk)

    def goNextBookmark(self)->None:
        bmk = self.bookmark.getNext( self.book.getAbsolutePage() )
        self._finishBookmarkNavigation(bmk)

    def onTimer(self):
        self.setBorderColour()

    def actionViewStatusBar(self, state)->None:
        self.pref.setValueBool( DbKeys.SETTING_WIN_STATUS_ENABLED, state , replace=True)
        self.ui.actionViewStatus.setChecked(state)
        self.ui.statusbar.setVisible(state)

    def actionAspectRatio(self, state)->None:
        self.book.setAspectRatio( state )
        self.showPages(absolute=True)

    def actionSmartPages( self, state:bool )->None:
        self.book.setProperty( DbKeys.SETTING_SMART_PAGES , state)
        self.smart_pages = state

    def actionProgressChanged( self, value )->None:
        """ The slider has changed so update page numbers """
        self.updatePageNumbers(value)

    def actionProgressReleased(self)->None:
        """ Slider released so update the progress bar. """
        self.goToPage( self.sender().value() )

    def actionProperties(self)->None:
        if self.book.editProperties( UiProperties() ) :
            self.setTitle()
            self.updateStatusBar()
            self.showPages(absolute=True)

    def actionDeleteAllBookmarks(self)->None:
        rtn = QMessageBox.warning(
            None, "{}".format( self.book.getTitle()),
            "Delete all booksmarks for book?\nThis cannot be undone.",
            QMessageBox.No | QMessageBox.Yes 
        )
        if rtn == QMessageBox.Yes:
            self.bookmark.delAllBookmarks( book=self.book.getTitle() )
            
    def actionPreferences(self)->None:
        from ui.preferences import UiPreferences  
        pref = UiPreferences()
        pref.formatData()
        pref.exec()
        changes = pref.getChanges()
        if len( changes) > 0:
            self.pref.saveAll( changes )
        self.settings = self.pref.getAll()
        self.ui.setNavigationShortcuts( self.settings )
        self.ui.setBookmarkShortcuts( self.settings )
        viewState = self.book.getPropertyOrSystem( BOOKPROPERTY.layout)
        self.ui.showRightPage((viewState == DbKeys.VALUE_PAGES_DOUBLE ))
        self.toggleMenuPages( viewState )
        self.showPages(absolute=True)
    
    def actionAbout(self)->None:
        from ui.about import UiAbout
        UiAbout().exec()
    
    def actionHelp(self)->None:
        from ui.help import UiHelp
        try:
            mainFile = os.path.abspath(sys.modules['__main__'].__file__)
        except:
            mainFile = sys.executable
        mainExePath = os.path.dirname(mainFile)
        try:
            DbConn.closeDB()
            uihelp = UiHelp(self, mainExePath)
            uihelp.setupHelp()
            uihelp.exec()
        except Exception as err:
            self.logger.error("Exception occured during help: {}".format( str(err ) ))
        finally:
            DbConn.openDB()

    def actionClickedBookmark(self)->None:
        if self.ui.lblBookmark.text() != "":
            self.actionGoBookmark()

    def actionMakeBookmark(self)->None:
        self.bookmark.thisBook( 
            self.book.getTitle(),
            self.book.getRelativePage( ), 
            self.book.getAbsolutePage() )
        
    def actionAddBookmark(self)->None:
        from ui.bookmark import UiBookmarkAdd
        dlg = UiBookmarkAdd( totalPages=self.book.getTotal() , numberingOffset=self.book.getRelativePageOffset() )
        dlg.setWindowTitle( "Add Bookmark for '{}'".format( self.book.getTitle()) )
        self.bookmark.addBookmarkDialog( dlg )
        self.updateBookmarkMenuNav()
    # end actionAddBookmark
    
    def actionCleanDB(self)->None:
        DbConn.cleanDB()
        QMessageBox.information(None,"","Database cleaned", QMessageBox.Ok )

    def actionDumpDB(self)->None:
        selectFilter = 'Backup Files (*.bak)'
        filters = ";;".join( [selectFilter, 'All files (*)'])
        
        filename = QFileDialog.getSaveFileName(
            None,
            "Select Database Backup File",
            QDir.currentPath(),
            filters , selectFilter )[0]
        if filename :
            DbConn.dump( filename )
            if os.path.isfile( filename ):
                self.system.setValue( DbKeys.SETTING_LAST_BACKUP, filename )
                msg = "Backup file {} written. Size: {:,}".format( filename, os.path.getsize( filename ))
                QMessageBox.information(None,"",msg, QMessageBox.Ok )

    def actionShowBookmark( self )->None:
        from ui.bookmark import UiBookmark, UiBookmarkEdit
        bmk = UiBookmark()
        while True:
            bookmarkList = self.bookmark.getAll()
            if len(bookmarkList) == 0 :
                QMessageBox.information(None, "Bookmarks", "There are no bookmarks", QMessageBox.Cancel)
                break
            if bmk.setupData( bookmarkList, relativeOffset=self.book.getRelativePageOffset()):
                bmk.exec()
                if not bmk.selected[ BOOKMARK.page ]:
                    break
                markName = bmk.selected[ BOOKMARK.name ]
                if bmk.action == bmk.actionEdit :
                    bmkEdit = UiBookmarkEdit( totalPages=self.book.getTotal() , numberingOffset=self.book.getRelativePageOffset())
                    bmkEdit.setWindowTitle("Edit bookmark for '{}'".format( self.book.getTitle()))
                    bmkEdit.setupData( bmk.selected  )
                    if bmkEdit.exec() == QDialog.Accepted:
                        changes = bmkEdit.getChanges()
                        if len(changes)>0:
                            self.bookmark.insert( 
                                book=self.book.getTitle(), 
                                bookmark=changes[ BOOKMARK.name ],
                                page=changes[ BOOKMARK.page ],
                                previousBookmark=markName
                            )
                    continue
                if bmk.action == bmk.actionGo:
                    self._finishBookmarkNavigation(bmk.selected)
                if bmk.action == bmk.actionDelete:
                    self.bookmark.delBookmark( book_id=self.book.getID(), bookmark=bmk.selected[ BOOKMARK.name ])
                break
        
    def actionFileOpen(self)->None:
        of = Openfile()
        of.exec()
        if of.bookName is not None:
            self.openBook( of.bookName )
            
    def actionOpenRecent(self, action )->None:
        if action is not None:
            if self.openBook( action.data() ) == QMessageBox.Retry:
                self.actionFileOpen()

    def actionOpenRecentUpdateFiles(self)->None:
        self.ui.menuOpen_Recent.clear()
        fileNames = DilBook().getRecent()
        if fileNames is not None and len( fileNames ) > 0 :
            for entry, bookEntry in enumerate( fileNames , start=1):
                recent_action = self.ui.menuOpen_Recent.addAction(
                    '&{:2d}.  {} - {}'.format(
                        entry, bookEntry[BOOK.name], bookEntry[BOOK.location])
                    )
                recent_action.setData( bookEntry[ BOOK.name] )
        # end if len(fileNames)
        self.ui.menuOpen_Recent.setEnabled( (len( fileNames ) > 0) )    

    def actionClose(self)->None:
        self.closeBook()
        self.actionOpenRecentUpdateFiles()
    
    def actionDelete(self)->None:
        df = Deletefile()
        rtn = df.exec()
        if rtn == QMessageBox.Accepted:
            DeletefileAction( df.bookName )

    def actionGoBookmark(self)->None:
        uiBookmark = UiBookmark()
        uiBookmark.setup( self.book.getTitle(), self.bookmark.getAll() , self.book.getContentStartingPage())
        uiBookmark.exec()
        newPage = uiBookmark.selectedPage
        if newPage :
            self.goToPage( newPage )
            self.setTitle( uiBookmark.selectedBookmark )
        del uiBookmark

    def actionGoPage(self)->None:
        from ui.page import PageNumber
        getPageNumber = PageNumber( self.book.getRelativePage(), self.book.isPageRelative())
        if getPageNumber.exec()  == 1 :
            pn = getPageNumber.page
            if getPageNumber.relative:
                pn = self.book.convertRelativeToAbsolute( pn )
            self.goToPage( pn )
        
    def toggleMenuPages(self, layoutType:str )->None:
        if layoutType is None:
            layoutType = self.system.getValue( DbKeys.SETTING_PAGE_LAYOUT , DbKeys.VALUE_PAGES_SINGLE )
        self.ui.actionOne_Page.setChecked(  (layoutType == DbKeys.VALUE_PAGES_SINGLE))
        self.ui.actionTwo_Pages.setChecked( (layoutType == DbKeys.VALUE_PAGES_DOUBLE))

    def _setPageLayout( self, value ):
        self.book.setProperty( DbKeys.SETTING_PAGE_LAYOUT , value)
        self.ui.showRightPage((value == DbKeys.VALUE_PAGES_DOUBLE ))
        self.toggleMenuPages( value )
        self.showPages(absolute=True)

    def _setSmartPages( self, value ):
        self.book.setProperty( DbKeys.SETTING_SMART_PAGES , value )
        self.smart_pages = value

    def actionOnePage(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_SINGLE)

    def actionTwoPages(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_DOUBLE)

    def _importPDF(self, insertData, duplicateData ):
        dilb = DilBook()
        bookmarks={}
        if len( duplicateData ) > 0 :
            for loc in duplicateData:
                book = dilb.getBookByColumn( BOOK.source , loc )
                if book is not None:
                    bookmarks[ loc ] = self.bookmark.getAll( book[BOOK.book])
                    dilb.delBook( book=book[BOOK.book])

        if  len( insertData ) > 0:
            for bdat in insertData:
                dilb.newBook( **bdat )

        if len( bookmarks ) > 0 :
            for loc in bookmarks:
                book = dilb.getBookByColumn( BOOK.source , loc )
                for marks in bookmarks[ loc ]:
                    self.bookmark.addBookmark( book[ BOOK.name ], marks[ BOOKMARK.name] , marks[BOOKMARK.page])

        
    def actionImportPDF(self)->None:
        from util.toolconvert import UiConvert
        uiconvert = UiConvert()
        uiconvert.setBaseDirectory( self.pref.getValue( DbKeys.SETTING_LAST_IMPORT_DIR))
        if uiconvert.exec_():
            self._importPDF( uiconvert.data , uiconvert.getDuplicateList() )
        self.pref.setValue( DbKeys.SETTING_LAST_IMPORT_DIR , uiconvert.baseDirectory(), replace=True )
        del uiconvert

    def actionReimportPDF(self)->None:
        rif = Reimportfile()
        if rif.exec() == QMessageBox.Accepted:
            book = self.book.getBook( book = rif.bookName)
            from util.toolconvert import UiConvertFilenames
            uiconvert = UiConvertFilenames( )
            if uiconvert.processFile( book[ BOOK.source ] ):
                self._importPDF(uiconvert.data, uiconvert.getDuplicateList() )
            del uiconvert
        del rif

    def actionImportDirectory(self)->None:
        from util.toolconvert import UiConvertDirectory
        uiconvert = UiConvertDirectory()
        uiconvert.setBaseDirectory( self.pref.getValue( DbKeys.SETTING_LAST_IMPORT_DIR))
        if uiconvert.exec_():
            self._importPDF( uiconvert.data , uiconvert.getDuplicateList() )
        self.pref.setValue( DbKeys.SETTING_LAST_IMPORT_DIR , uiconvert.baseDirectory() , replace=True)
        del uiconvert

    def actionCheckIncomplete(self)->None:
        from qdil.book import DilBook
        DilBook().updateIncompleteBooksUI()
        pass

if __name__ == "__main__":
    sy = SystemPreferences()
    dbLocation    = sy.getPathDB()    # Fetch the system settings
    mainDirectory = sy.getDirectory()
    DbConn.openDB( dbLocation )
    setup = Setup()

    app = QApplication([])
    ## This will initialise the system. It requires prompting so uses dialog box
    if not isfile( dbLocation ) or not os.path.isdir( mainDirectory ):
        from util.beginsetup import Initialise
        ini = Initialise( )
        ini.run( dbLocation  )
        del ini
        
    setup.initData()
    setup.updateSystem()
    setup.logging(mainDirectory)
    logger = logging.getLogger( 'main')

    del sy
    del setup
    
    window = MainWindow( )
    window.connectMenus()
    window.restoreWindowFromSettings()
    window.show()
    window.openLastBook()
    window.setupWheelTimer()
    window.show()
    rtn = app.exec()
    DbConn.destroyConnection()
    sys.exit(rtn )
