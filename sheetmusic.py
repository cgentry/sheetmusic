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

"""
    SheetMusic is a program to display music on a monitor. It uses
    PNGs (normally) and flips pages. A simple program in Python and QT
"""
__version__ = "0.1.5"
__author__ = "Charles Gentry"

import sys
import os

from musicsettings import MusicSettings, MSet
from recent_files import RecentFiles
from ui.main import UiMain
from ui.bookmark import UiBookmark, UiBookmarkAdd
from ui.properties import UiProperties
from ui.file import UiFile

from PySide6.QtCore import  QEvent, Qt,QObject,QPoint,QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadUi()
        self.bookOpen = False

    def _pageLabel( self, label, bookpage ):
        keepAspectRatio = self.file.getAspectRatio()
        
        px = self.file.getPixmap(bookpage )
        label.setScaledContents( ( not keepAspectRatio ) )
        if keepAspectRatio:
            size = self.ui.mainWindow.size()
            if self.ui.isRightPageShown():
                size.setWidth( size.width()/2 )
            label.resize( size )
            px = px.scaled( size , aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation )

        label.setPixmap( px )

    def pageImageLeft(self)->None:
        """ Display the left page image """
        self._pageLabel( self.ui.left ,self.file.getBookPageNumber() )

    def pageImageRight(self)->None:
        """ Display the right page image when doing two page display"""
        if self.ui.isRightPageShown():
            self._pageLabel( self.ui.right ,self.file.getBookPageNumber()+1 )

    def showPages(self, delay:bool=False)->None:
        if self.bookOpen :
            self.pageImageLeft()
            self.pageImageRight()
            self.updateStatusBar()
            self.ui.mainWindow.show()

    def updatePageNumbers(self, absolutePageNumber:int=None )->None:
        if  self.file.isThisPageRelative(absolutePageNumber):
            self.ui.lblPageAbsolute.setText( " |{:4d} |".format( absolutePageNumber ))
            lbl = "Page"
        else:
            self.ui.lblPageAbsolute.clear()
            lbl = "Book page"
        self.ui.lblPageRelative.setText( "{}: {:d}".format( lbl, self.file.getBookPageNumberRelative(absolutePageNumber)))
        
    def updateBookmarkMenuNav( self, bookmark=None ):
        if self.file.totalBookmarks < 1 :
            self.ui.actionNextBookmark.setDisabled(True)
            self.ui.actionPreviousBookmark.setDisabled(True)
        elif bookmark is not None and bookmark.isEndOfList():
            if bookmark.index <=0:
                self.ui.actionNextBookmark.setEnabled(True)
                self.ui.actionPreviousBookmark.setDisabled(True)
            else:
                self.ui.actionPreviousBookmark.setEnabled(True)
                self.ui.actionNextBookmark.setDisabled(True)
        else:
            self.ui.actionNextBookmark.setEnabled(True)
            self.ui.actionPreviousBookmark.setEnabled(True)

    def updateStatusBar(self)->None:
        absolutePageNumber = self.file.getBookPageNumber()
        Bookmark = self.file.config.getCurrentBookmark()

        if  self.file.isThisPageRelative(absolutePageNumber):
            self.ui.lblPageAbsolute.setText( " |{:4d} |".format( absolutePageNumber))
            lbl = "Page"
        else:
            self.ui.lblPageAbsolute.clear()
            lbl = "Book page"
        self.ui.lblPageRelative.setText( "{}: {:d}".format( lbl, self.file.getBookPageNumberRelative()))
        self.updateBookmarkMenuNav( Bookmark )

        self.ui.statusProgress.setMaximum( self.file.totalPages)
        self.ui.statusProgress.setValue( absolutePageNumber)

    def clearLabels(self)->None:
        self.ui.left.text = ""
        self.ui.right.text = ""

    def restoreWindowFromSettings(self)->None:
        self.settings.restoreMainWindow( self.ui.getWindow() ) 
        self.settings.restoreShortcuts( self.ui )  

    def openFile(self)->None:
        """ Open the file configuration"""
        self.closeFile()
        self.file = UiFile()
        self.file.setFileType(self.settings.value(
            MSet.byDefault(MSet.SETTING_DEFAULT_TYPE)))

    def closeFile(self)->None:
        if self.file is not None:
            self.file.closeBook()
            self.file = None
            del self.file
            
    def openBook(self, newDirName:str, page=None):
        """ """
        self.openFile() 
        rtn = self.file.openBook(newDirName)
        if rtn == QMessageBox.Ok:
            self.bookOpen = True
            self.toggleMenuPages( self.file.config.getBookLayout())
            showRight = self.file.config.getNumberPagesToDisplay() > 1
            self.ui.showRightPage(showRight)
            self.ui.actionAspectRatio.setChecked( self.file.getAspectRatio())
            self.setTitle()
            self.setMenusForBook(True)
            self.showPages()
            self.recentList.addToRecent( self.file.getBookPath(), self.file.getBookPageNumber() )
        return rtn

    def closeBook(self)->None:
        """ Close the book, save a pointer to it, and hide the menu items. """
        self.recentList.write()
        self.settings.setValue(
           MSet.byFile( MSet.SETTING_LAST_BOOK), self.file.getBookPagePath())
        self.closeFile()
        self.setMenusForBook(False)
        self.ui.mainWindow.hide()
        self.bookOpen = False

    def loadUi(self)->None:
        self.settings = MusicSettings()
        self.recentList = RecentFiles(
            self.settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_PATH)) )
        self.recentList.read()
        self.ui = UiMain()
        self.ui.setupUi(self)
        self.file = None
    
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
            self.showPages()

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
        self.settings.saveMainWindow( self.ui.mainWindow)
        self.closeBook()

    def pageBackward(self)->None:
        self.file.incPageNumber(-1)
        self.showPages()

    def pageForward(self)->None:
        self.file.incPageNumber(1)
        self.showPages(True)
    
    def goToPage(self, page )->None:
        ''' Set the page number to the page passed and display

            page number must be absolute, not relative.
        '''
        self.file.setPageNumber(page)
        self.showPages()

    def goFirstBookmark(self)->None:
        self.file.setPageNumber(self.file.config.getFirstBookmark())
        self.showPages()

    def goLastBookmark(self)->None:
        self.file.setPageNumber(self.file.config.getLastBookmark())
        self.showPages()

    def goFirstPageShown(self)->None:
        self.file.setPageNumber(self.file.getFirstPageShown() )
        self.showPages()

    def goLastPageShown(self)->None:
        self.file.setPageNumber( self.file.getLastPageShown())
        self.showPages()

    def connectMenus(self)->None:
        """ Connect menus and events to the routines handling the function"""
        self.ui.actionBookmarkCurrentPage.triggered.connect(self.actionMakeBookmark)
        self.ui.actionShowBookmarks.triggered.connect(self.actionShowBookmark)
        self.ui.actionAdd_Bookmark.triggered.connect(self.actionAddBookmark)
        #self.ui.actionBookmark.triggered.connect(self.actionGoBookmark)
        self.ui.actionPreviousBookmark.triggered.connect( self.goPreviousBookmark )
        self.ui.actionNextBookmark.triggered.connect( self.goNextBookmark )
        self.ui.lblBookmark.clicked.connect( self.actionClickedBookmark )

        self.ui.actionOpen.triggered.connect(self.actionFileOpen)
        self.ui.menuOpen_Recent.aboutToShow.connect( self.actionOpenRecentUpdateFiles)
        self.ui.menuOpen_Recent.triggered.connect(self.actionOpenRecent)
        self.ui.actionProperties.triggered.connect(self.actionProperties)
        self.ui.actionPreferences.triggered.connect(self.actionPreferences)
        self.ui.actionClose.triggered.connect(self.actionClose)

        self.ui.actionGo_to_Page.triggered.connect(self.actionGoPage)
        self.ui.actionUp.triggered.connect( self.pageBackward)
        self.ui.actionDown.triggered.connect(self.pageForward)

        
        self.ui.actionFirstPage.triggered.connect( self.goFirstPageShown )
        self.ui.actionLastPage.triggered.connect( self.goLastPageShown )

        self.ui.actionOne_Page.triggered.connect( self.actionOnePage)
        self.ui.actionTwo_Pages.triggered.connect( self.actionTwoPages)
        self.ui.actionViewStatus.triggered.connect(self.actionViewStatusBar)
        self.ui.actionAspectRatio.triggered.connect(self.actionAspectRatio)

        self.ui.statusProgress.valueChanged.connect( self.actionProgressChanged)
        self.ui.statusProgress.sliderReleased.connect(self.actionProgressReleased)

        self.ui.twoPagesSide.installEventFilter( self)

        self.ui.actionImportPDF.triggered.connect( self.actionImportPDF)

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
        if self.settings.value( MSet.byDefault(MSet.SETTING_DEFAULT_OPEN_LAST), True):
            book,page = self.recentList.getTopEntry()
            if book :
                self.openBook(book, page)    

    def setTitle( self, bookmark=None )->None:
        """ Title is made of the title and bookmark if there is one """
        title = "SheetMusic: " + self.file.getBookTitle()
        if bookmark:
            title = "{} - {}".format( title, bookmark)
        self.ui.mainWindow.setWindowTitle( title )
        self.ui.mainWindow.show()
    
    def goPreviousBookmark(self)->None:
        bookmark = self.file.goPreviousBookmark()
        if bookmark.isEndOfList():
            self.ui.actionPreviousBookmark.setDisabled( True )
        self.showPages()

    def goNextBookmark(self)->None:
        bookmark = self.file.goNextBookmark()
        if bookmark.isEndOfList():
            self.ui.actionNextBookmark.setDisabled( True )
        self.showPages()

    def actionViewStatusBar(self, state)->None:
        if state:
            self.ui.statusbar.show()
        else:
            self.ui.statusbar.hide()

    def actionAspectRatio(self, state)->None:
        self.file.setAspectRatio( state )
        self.showPages()


    def actionProgressChanged( self, value )->None:
        """ The slider has changed so update page numbers """
        self.updatePageNumbers(value)

    def actionProgressReleased(self)->None:
        """ Slider released so update the progress bar. """
        self.goToPage( self.sender().value() )

    def actionProperties(self)->None:
        prop = UiProperties()
        prop.setPropertyList( self.file )
        rtn = prop.exec()
        if rtn :
            self.file.setMutableProperties( prop.changes[0], prop.changes[1], prop.changes[2], prop.changes[3])
            self.setTitle()
            self.updateStatusBar()
            self.showPages()
            
    def actionPreferences(self)->None:
        from ui.preferences import UiPreferences   
        pref= UiPreferences()
        pref.formatData( self.settings )
        if pref.exec():
            changes = pref.getChanges()
            for key,value in changes["settings"].items():
                self.settings.setValue(key , value )
            self.settings.beginGroup( MSet.SETTING_GROUP_KEYS )
            for key, value in changes["keys"].items():
                self.settings.setValue( key , value )
            self.settings.endGroup()

        ## Don't override the default setting
        ## Save config file
        if MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT) in pref.states:
            if not self.file.config.has_option( None, MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)):
                viewState = pref.states[MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)]
                self.ui.showRightPage( (viewState == MSet.VALUE_PAGES_DOUBLE) )
                self.toggleMenuPages(viewState)
                self.showPages()
    
    def actionClickedBookmark(self)->None:
        if self.ui.lblBookmark.text() != "":
            self.actionGoBookmark()

    def actionMakeBookmark(self)->None:
        ok = False
        relativePage = self.file.getBookPageNumberRelative( )
        absolutePage = self.file.getBookPageNumber()
        prompt = "Name for bookmark at "
        if relativePage != absolutePage :
            prompt = prompt + "Book Page {:d} / Page Shown {:d}:".format( absolutePage, relativePage )
        else:
            prompt = prompt + "Book Page {:d}:".format( absolutePage )
        windowFlag = Qt.FramelessWindowHint

        dlg = QInputDialog(self)
        dlg.setLabelText( prompt )
        dlg.setTextValue( "")
        dlg.setOption(QInputDialog.UsePlainTextEditForTextInput, False)
        dlg.setWindowFlag( windowFlag )
        ok = dlg.exec()
        if ok :
            self.file.saveBookmark( dlg.textValue() )

    def actionAddBookmark(self)->None:
        dlg = UiBookmarkAdd( maximumPage=self.file.getBookPagesTotal(), pageShownOffset=self.file.getRelativePageOffset())
        loop = UiBookmarkAdd.SAVE_CONTINUE
        while loop==UiBookmarkAdd.SAVE_CONTINUE:
            dlg.clear()
            loop = dlg.exec()
            if loop != UiBookmarkAdd.CANCEL:
                self.file.saveBookmark( 
                    name=dlg.values["bookmark"],
                    bookpage=dlg.values['bookpage'],
                    pageshown=dlg.values['pageshown'])
                self.updateBookmarkMenuNav()
    # end actionAddBookmark
    
    def actionShowBookmark( self )->None:
        uiBookmark = UiBookmark( )
        uiBookmark.setBookmarkList( self.file )
        rtn = uiBookmark.exec()
        if rtn == QMessageBox.Accepted:
            if uiBookmark.action == 'go':
                newPage = uiBookmark.selectedPage
                if newPage :
                    self.goToPage( newPage )
                    self.setTitle( uiBookmark.selectedBookmark )
            if uiBookmark.action == 'delete':
                bookName = self.file.getBookTitle()
                if uiBookmark.selectedPage :
                    title = "{}:   {}\n{}:   {}\n{}:    {}\n{}:    {}".format(
                        "Book", bookName, 
                        "Bookmark", uiBookmark.selectedBookmark,
                        "Page shown", uiBookmark.relativePage, 
                        "Book page:", uiBookmark.selectedPage )
                    qbox = QMessageBox()
                    qbox.setIcon(QMessageBox.Question)
                    qbox.setCheckBox(None)
                    qbox.addButton('Delete', QMessageBox.AcceptRole)
                    qbox.addButton('Cancel', QMessageBox.RejectRole)

                    qbox.setText("Delete bookmark?")
                    qbox.setInformativeText(uiBookmark.selectedBookmark)
                    qbox.setDetailedText(title)
                    if qbox.exec() == QMessageBox.AcceptRole:
                        self.file.deleteBookmark( 
                            self.file.getBookPageName( uiBookmark.selectedPage) , 
                            pageShown=uiBookmark.relativePage,
                            bookName=bookName,
                            bookmark=uiBookmark.selectedBookmark,
                            bookPage=uiBookmark.selectedPage 
                        )
                    qbox.close()
                    del qbox
        uiBookmark.close()
        del uiBookmark

    def actionFileOpen(self)->None:
        rtn = QMessageBox.Retry
        while rtn == QMessageBox.Retry:
            newDirName = QFileDialog.getExistingDirectory(
                self,
                "Open SheetMusic Directory",
                dir=self.settings.value(MSet.byDefault(MSet.SETTING_DEFAULT_PATH)),
                options=QFileDialog.Option.ShowDirsOnly)
            rtn = QMessageBox.Cancel
            if newDirName:
                rtn = self.openBook(newDirName)
            
    def actionOpenRecent(self, action )->None:
        if self.openBook( action.data() ) == QMessageBox.Retry:
            self.actionFileOpen()

    def actionOpenRecentUpdateFiles(self)->None:
        self.ui.menuOpen_Recent.clear()
        fileNames = self.recentList.getRecentListBookNames()
        entry = 0
        if len( fileNames ) > 0 :
            for row, bookEntry in enumerate(fileNames, 1):
                if os.path.isdir( bookEntry.book ) and bookEntry.book != self.file.getBookPath():
                    entry += 1
                    print( "Entry:", entry, ", row:", row )
                    if bookEntry.book != bookEntry.name :
                        recent_action = self.ui.menuOpen_Recent.addAction('&{}.  {} - {}'.format(
                            entry, bookEntry.name, bookEntry.book)
                        )
                    else:
                        recent_action = self.ui.menuOpen_Recent.addAction('&{}.  {}'.format(
                            entry, bookEntry.name))
                    recent_action.setData( bookEntry.book )

        self.ui.menuOpen_Recent.setEnabled( (entry > 0) )    

    def actionClose(self)->None:
        self.closeBook()
        self.actionOpenRecentUpdateFiles()
    
    def actionGoBookmark(self)->None:
        uiBookmark = UiBookmark()
        uiBookmark.setBookmarkList( self.file )
        uiBookmark.exec()
        newPage = uiBookmark.selectedPage
        if newPage :
            self.goToPage( newPage )
            self.setTitle( uiBookmark.selectedBookmark )
        del uiBookmark

    def actionGoPage(self)->None:
        from ui.page import PageNumber
        pn = self.file.getBookPageNumberRelative()
        relative = self.file.isThisPageRelative()
        getPageNumber = PageNumber( pn, relative)
        rtn = getPageNumber.exec()
        if rtn ==1 :
            pn = getPageNumber.page
            relative = getPageNumber.relative
            if relative:
                pn = self.file.getBookPageAbsolute( pn )
            self.goToPage( pn )
        
    def actionOnePage(self)->None:
        self.file.setConfig( MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT), MSet.VALUE_PAGES_SINGLE)
        self.ui.showRightPage(False)
        self.toggleMenuPages( MSet.VALUE_PAGES_SINGLE)
        self.showPages()

    def actionTwoPages(self)->None:
        self.file.setConfig( MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT), MSet.VALUE_PAGES_DOUBLE)
        self.ui.showRightPage(True)
        self.toggleMenuPages( MSet.VALUE_PAGES_DOUBLE )
        self.showPages()

    def actionImportPDF(self)->None:
        from util.toolconvert import UiConvert
        uiconvert = UiConvert(self.settings)
        uiconvert.exec_()
        if uiconvert.status == uiconvert.RETURN_CONTINUE and os.path.isdir( self.file.dirPath ):
            ## write a blank config for the new config
            originalPath = self.file.dirPath
            self.file.setPaths( uiconvert.bookPath )
            self.file.openBookConfig()
            self.recentList.addToRecent( self.file.getBookPath(), self.file.getBookPageNumber() )
            self.file.setPaths( originalPath)
            self.file.openBookConfig()

    def toggleMenuPages(self, layoutType:str )->None:
        self.ui.actionOne_Page.setChecked( (layoutType == MSet.VALUE_PAGES_SINGLE))
        self.ui.actionTwo_Pages.setChecked( (layoutType == MSet.VALUE_PAGES_DOUBLE))

if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.connectMenus()
    widget.restoreWindowFromSettings()
    widget.openLastBook()
    widget.setupWheelTimer()
    widget.show()
    sys.exit(app.exec())
