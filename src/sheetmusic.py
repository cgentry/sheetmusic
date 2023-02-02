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

"""
    SheetMusic is a program to display music on a monitor. It uses
    PNGs (normally) and flips pages. A simple program in Python and QT
"""

from genericpath import isfile
import sys
import os
import logging
from tkinter import N

from PySide6.QtCore     import QEvent, QObject, Qt, QTimer, QDir, QByteArray
from PySide6.QtWidgets  import QApplication, QMainWindow,  QMessageBox, QDialog, QFileDialog
from PySide6.QtGui      import QPixmap, QAction

from qdb.dbconn         import DbConn
from qdb.dbsystem       import DbSystem
from qdb.keys           import BOOK, BOOKPROPERTY, BOOKMARK, DbKeys, NOTE
from qdb.setup          import Setup
from qdb.dbnote         import DbNote

from qdil.preferences   import DilPreferences, SystemPreferences
from qdil.book          import DilBook
from qdil.bookmark      import DilBookmark

from ui.main            import UiMain
from ui.pagewidget      import ( PageLabelWidget, PageWidget )
from ui.properties      import UiProperties
from ui.bookmark        import UiBookmark
from ui.file            import Openfile, Deletefile, DeletefileAction, Reimportfile
from ui.note            import UiNote
from util.toollist      import GenerateToolList, ToolScript
from ui.runscript       import UiRunScriptFile, ScriptKeys

from util.convert       import toBool

class MainWindow(QMainWindow):
    MAX_PAGES=3
    def __init__(self):
        super().__init__()
        self.smart_pages = False
        
        self.loadUi()
        
        self.book = DilBook()
        self.system = DbSystem()
        self.bookmark = DilBookmark()
        self._notelist = None
        self.logger = logging.getLogger('main')
        self.import_dir = self.pref.getValue( DbKeys.SETTING_LAST_IMPORT_DIR  )
        tl = GenerateToolList()
        self.toollist = tl.list()
        del tl
        
    def loadUi(self)->None:
        self.pref = DilPreferences()
        self.ui = UiMain()
        self.ui.setupUi(self)

    def _pageLabel( self, label:PageLabelWidget, bookpage )->bool:
        label.clear()
        if bookpage > self.book.getTotal():
            return True
        px = self.book.getPixmap(bookpage )
        return label.setImage( px , bookpage )

    def pageList( self, start_page, len_list)->list:
        """ pageList creates a list, MAX_PAGES long, of the pages. The first entry will always be the one requests."""
        plist = [0]*self.MAX_PAGES
        if start_page < 1:
            start_page = 1
        totalpages = self.book.getTotal()
        for i in range( 0, len_list ):
            if  start_page+i > totalpages:
                break
            plist[i] = start_page+i
        return plist

    def loadPages( self )->bool:
        """ Load all pages into the book at once. This loads the MAX_PAGES every time.

            This attempts to optimise page loads and display by looking at the number of
            pages we load.
        """
        if self.book.isOpen():
            page = self.book.getAbsolutePage()  
            ## work some 'magic' Show page-n...page IF page is last page.
            totalPages = self.book.getTotal()
            showingPages = self.ui.pageWidget.numberPages()
            if page == totalPages and showingPages and showingPages > 1:
                plist = self.pageList( page-showingPages+1 , self.MAX_PAGES )
                self._loadPageWidgetList( plist )
            else:
                self._loadPageWidgetList( self.pageList( page , self.MAX_PAGES ) )
        return self.book.isOpen()

    def reloadPages( self )->bool:
        if self.book.isOpen():
            self._loadPageWidgetList( self.ui.pageWidget.pageNumbers() )
        return self.book.isOpen()

    def _loadPageWidgetList( self, plist:list ):
        if len( plist ) < self.MAX_PAGES :
            plist.extend( [0] * (self.MAX_PAGES - len(plist) ))
        return self._loadPageWidget( plist[0], plist[1], plist[2] )

    def _loadPageWidget( self, pg1:int, pg2:int, pg3:int ):
            page1 = self.book.getPixmap( pg1 )
            page2 = self.book.getPixmap( pg2)
            page3 = self.book.getPixmap( pg3)
            self.ui.pageWidget.loadPages( page1, pg1 , page2, pg2 ,page3, pg3)

    def updatePageNumbers(self, absolute_page_number:int=None )->None:
        if  self.book.isPageRelative(absolute_page_number):
            self.ui.label_page_absolute.setText( " |{:4d} |".format( absolute_page_number ))
            lbl = "Page"
        else:
            self.ui.label_page_absolute.clear()
            lbl = "Book page"
        self.ui.label_page_relative.setText( "{}: {:d}".format( lbl, self.book.getRelativePage(absolute_page_number)))
        
    def updateBookmarkMenuNav( self, bookmark=None ):
        if self.bookmark.getTotal() < 1 :
            self.ui.actionPreviousBookmark.setDisabled(True)
            self.ui.actionNextBookmark.setDisabled(True)
        if bookmark is not None:
            self.ui.actionPreviousBookmark.setDisabled( self.bookmark.isFirst( bookmark) )
            self.ui.actionNextBookmark.setDisabled( self.bookmark.isLast( bookmark ))

    def _update_note_indicator(self, page_number:int):
        nlist = self.getNoteList( self.book.getID())
        self.ui.setBookNote( (0 in nlist and nlist[0] > 0 ))
        self.ui.setPageNote( (page_number in nlist and nlist[ page_number] > 0 ))

    def updateStatusBar(self)->None:
        if self.ui.pageWidget.getHighestPageShown() == self.book.getTotal():
            absolute_page_number = self.ui.pageWidget.getHighestPageShown()
        else:
            absolute_page_number = self.ui.pageWidget.getLowestPageShown()

        self.ui.slider_page_position.setMaximum( self.book.getTotal())
        self.ui.slider_page_position.setValue( absolute_page_number)

        if  self.book.isPageRelative(absolute_page_number):
            self.ui.label_page_absolute.setText( " |{:4d} |".format( absolute_page_number))
            lbl = "Page"
        else:
            self.ui.label_page_absolute.clear()
            lbl = "Book page"

        self.ui.label_page_relative.setText( "{}: {:d}".format( lbl, self.book.getRelativePage()))
        self._update_note_indicator(absolute_page_number)

        
    def restoreWindowFromSettings(self)->None:
        self.pref.restoreMainWindow( self.ui.getWindow() ) 
        self.pref.restoreShortcuts( self.ui )  
        self.actionViewStatusBar( self.pref.getValueBool( DbKeys.SETTING_WIN_STATUS_ENABLED , True ))
    
    def getNoteList(self, book_id:int , refresh=False)->dict:
        if book_id is not None and (self._notelist is None or refresh ):
            dbnote = DbNote()
            self._notelist = dbnote.getNoteForBook( book_id )
        return self._notelist

    def open_book(self, newBookName:str, page=None):
        """ """
        self.close_book()
        rtn = self.book.openBook(newBookName, page )
        if rtn == QMessageBox.Ok:
            self.book_layout = self.book.getPropertyOrSystem( BOOKPROPERTY.layout)
            self.smart_pages = toBool( self.book.getPropertyOrSystem( DbKeys.SETTING_SMART_PAGES ) )

            #self.ui.pageWidget.setDisplay( self.book_layout )
            self.ui.pageWidget.setSmartPageTurn( self.smart_pages )
            self.ui.pageWidget.setKeepAspectRatio( self.book.getAspectRatio() )
            #self.ui.pageWidget.resize( self.ui.pager.size() )
            self.ui.pageWidget.setDisplay( self.book_layout )

            # if self.loadPages():
            self.setTitle()
            self.setMenusForBook(True)
            self.bookmark.open( newBookName )
            self.updateBookmarkMenuNav( self.bookmark.getBookmarkPage( page ))
            self.ui.actionAspectRatio.setChecked( self.book.getAspectRatio()  )
            self.ui.actionSmartPages.setChecked( self.smart_pages )
            self._setPageLayout( self.book.getPropertyOrSystem( BOOKPROPERTY.layout) )
            self.updateStatusBar()
        return rtn

    def close_book(self)->None:
        """ Close the book, save a pointer to it, and hide the menu items. """
        self._notelist = None
        if self.book.isOpen():
            self.pref.setValue( DbKeys.SETTING_LAST_BOOK_NAME , self.book.getTitle())
            self.book.closeBook()
            self.ui.pageWidget.clear()
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
        self.ui.pageWidget.resize( self.ui.pager.size() )
        self.reloadPages()


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
        self.pref.saveMainWindow( self.ui.getWindow() )
        self.pref.setValue( DbKeys.SETTING_LAST_IMPORT_DIR , self.import_dir , replace=True )
        self.close_book()
        DbConn.closeDB()
        
    def pageBackward(self)->None:
        pg = self.book.getAbsolutePage()-1 
        if pg < 1:
            return
        self.ui.pageWidget.previousPage( self.book.getPixmap( pg ), pg , end=(pg==1))
        self.book.setPageNumber( pg )
        self.updateStatusBar()

    def pageForward(self)->None:
        pg = self.ui.pageWidget.getHighestPageShown()
        if pg == 0:
            pg = self.book.getAbsolutePage()
        self.book.setPageNumber( pg )
        pg = pg+1
        if self.book.isValidPage( pg  ): 
            self.ui.pageWidget.nextPage( self.book.getPixmap( pg ), pg , end=(pg==self.book.getTotal()))
        self.updateStatusBar()
    
    def goToPage(self, page )->None:
        ''' Set the page number to the page passed and display
            page number must be absolute, not relative.
        '''
        self.book.setPageNumber(page)
        self.loadPages()

    def goFirstBookmark(self)->None:
        bmk = self.bookmark.getFirst( )
        self.book.setPageNumber(bmk[BOOKMARK.page])
        self.loadPages()

    def goLastBookmark(self)->None:
        bmk = self.bookmark.getLast( )
        self.book.setPageNumber(bmk[BOOKMARK.page])
        self.loadPages()

    def goFirstPageShown(self)->None:
        self.book.setPageNumber(self.book.getFirstPageShown() )
        self.loadPages()

    def goLastPageShown(self)->None:
        self.book.setPageNumber( self.book.getLastPageShown())
        self.loadPages()

    def connectMenus(self)->None:
        """ Connect menus and events to the routines handling the function"""
        self.ui.actionBookmarkCurrentPage.triggered.connect(self.actionMakeBookmark)
        self.ui.actionShowBookmarks.triggered.connect(self.actionShowBookmark)
        self.ui.actionAdd_Bookmark.triggered.connect(self.actionAddBookmark)
        #  self.ui.actionCleanDB.triggered.connect( self.actionCleanDB )
        #  self.ui.actionDumpDB.triggered.connect( self.actionDumpDB )
        self.ui.actionToolRefresh.triggered.connect( self.action_tool_refresh )

        self.ui.menuToolScript.aboutToShow.connect( self.actionToolScriptUpdateList)
        self.ui.menuToolScript.triggered.connect(self.actionToolScript )
        

        #self.ui.actionBookmark.triggered.connect(self.actionGoBookmark)
        self.ui.actionPreviousBookmark.triggered.connect( self.goPreviousBookmark )
        self.ui.actionNextBookmark.triggered.connect( self.goNextBookmark )
        self.ui.btn_bookmark.clicked.connect( self.actionClickedBookmark )

        self.ui.actionOpen.triggered.connect(self.actionFileOpen)
        self.ui.menuOpenRecent.aboutToShow.connect( self.actionOpenRecentUpdateFiles)
        self.ui.menuOpenRecent.triggered.connect(self.actionOpenRecent)
        self.ui.actionProperties.triggered.connect(self.actionProperties)
        self.ui.actionNoteBook.triggered.connect( self.actionNoteBook )
        self.ui.actionDeleteAllBookmarks.triggered.connect( self.actionDeleteAllBookmarks )
        self.ui.actionPreferences.triggered.connect(self.actionPreferences)
        self.ui.actionAbout.triggered.connect( self.actionAbout )
        self.ui.actionHelp.triggered.connect( self.actionHelp)
        self.ui.actionClose.triggered.connect(self.actionClose)
        self.ui.actionDelete.triggered.connect( self.actionDelete )
        
        self.ui.actionFirstPage.triggered.connect( self.goFirstPageShown )
        self.ui.actionLastPage.triggered.connect( self.goLastPageShown )

        self.ui.actionOne_Page.triggered.connect( self.actionOnePage)
        self.ui.actionTwo_Pages.triggered.connect( self.actionTwoPagesSide)
        self.ui.actionTwo_Pages_Stacked.triggered.connect( self.actionTwoPagesStacked)
        self.ui.actionThree_Pages.triggered.connect( self.actionThreePagesSide )
        self.ui.actionThree_Pages_Stacked.triggered.connect( self.actionThreePagesStacked )
        self.ui.actionViewStatus.triggered.connect(self.actionViewStatusBar)
        self.ui.actionAspectRatio.triggered.connect(self.actionAspectRatio)
        self.ui.actionSmartPages.triggered.connect( self.actionSmartPages )

        self.ui.actionGo_to_Page.triggered.connect(self.actionGoPage)
        self.ui.actionDown.triggered.connect(self.pageForward)
        self.ui.actionUp.triggered.connect( self.pageBackward)

        self.ui.slider_page_position.valueChanged.connect( self.actionProgressChanged)
        self.ui.slider_page_position.sliderReleased.connect(self.actionProgressReleased)

        #self.ui.twoPagesSide.installEventFilter( self)

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
                self.open_book(recent[0][BOOK.name])    

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

    def actionViewStatusBar(self, state)->None:
        self.pref.setValueBool( DbKeys.SETTING_WIN_STATUS_ENABLED, state , replace=True)
        self.ui.actionViewStatus.setChecked(state)
        self.ui.statusbar.setVisible(state)

    def actionAspectRatio(self, state)->None:
        self.book.setAspectRatio( state )
        self.loadPages()

    def actionSmartPages( self, state:bool )->None:
        self.book.setProperty( DbKeys.SETTING_SMART_PAGES , state)
        self.smart_pages = state
        self.ui.pageWidget.setSmartPageTurn( self.smart_pages )

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
            self.loadPages()

    def _actionNote( self, page:int, seq:int , titleSuffix:str ):
        dbnote = DbNote()
        uinote = UiNote()
        id     = self.book.getID()
        note   = dbnote.getNote( id , page=page , seq=seq )
        
        uinote.setText( note[ NOTE.note ] )    
        uinote.setLocation( note[NOTE.location])
        uinote.setWindowTitle( "{} - {}".format( self.book.getTitle() , titleSuffix) )
        uinote.setID( ( note[ NOTE.id ] if NOTE.id in note and note[NOTE.id] > 0 else None ) )
        rtn=uinote.exec()
        if rtn:
            if uinote.delete() and NOTE.id in note :
                dbnote.deleteNote(note )
            elif uinote.textChanged():
                note[NOTE.note ]     = uinote.text() 
                note[NOTE.location ] = uinote.location() 
                dbnote.add( note )
                self.ui.setBookNote(True)

    def actionNoteBook(self)->None:
        self._actionNote( page=0, seq=0, titleSuffix='Book')

    def actionNotePage( self, id ):
        page   = self.book.getAbsolutePage()
        self._actionNote( page=page , seq=0 ,titleSuffix="Page {}".format( page ) )

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
        settings = self.pref.getAll()
        self.ui.setNavigationShortcuts( settings )
        self.ui.setBookmarkShortcuts( settings )
        viewState = self.book.getPropertyOrSystem( BOOKPROPERTY.layout)
        self.ui.pageWidget.setDisplay( viewState )
        self.toggleMenuPages( viewState )
        self.loadPages()
    
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
        if self.ui.btn_bookmark.text() != "":
            self.actionGoBookmark()

    def actionMakeBookmark(self)->None:
        self.bookmark.thisBook( 
            self.book.getTitle(),
            self.book.getRelativePage( ), 
            self.book.getAbsolutePage() )
        
    def actionAddBookmark(self)->None:
        from ui.bookmark import UiBookmarkAdd
        dlg_add_bookmark = UiBookmarkAdd( totalPages=self.book.getTotal() , numberingOffset=self.book.getRelativePageOffset() )
        dlg_add_bookmark.setWindowTitle( "Add Bookmark for '{}'".format( self.book.getTitle()) )
        self.bookmark.addBookmarkDialog( dlg_add_bookmark )
        self.updateBookmarkMenuNav()
    # end actionAddBookmark
    
    # def actionCleanDB(self)->None:
    #     DbConn.cleanDB()
    #     QMessageBox.information(None,"","Database cleaned", QMessageBox.Ok )

    # def actionDumpDB(self)->None:
    #     selectFilter = 'Backup Files (*.bak)'
    #     filters = ";;".join( [selectFilter, 'All files (*)'])
        
    #     filename = QFileDialog.getSaveFileName(
    #         None,
    #         "Select Database Backup File",
    #         QDir.currentPath(),
    #         filters , selectFilter )[0]
    #     if filename :
    #         DbConn.dump( filename )
    #         if os.path.isfile( filename ):
    #             self.system.setValue( DbKeys.SETTING_LAST_BACKUP, filename )
    #             msg = "Backup file {} written. Size: {:,}".format( filename, os.path.getsize( filename ))
    #             QMessageBox.information(None,"",msg, QMessageBox.Ok )

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
            self.open_book( of.bookName )
            
    def actionOpenRecent(self, action:QAction )->None:
        if action is not None:
            if self.open_book( action.data() ) == QMessageBox.Retry:
                self.actionFileOpen()

    def action_tool_refresh( self, action:QAction )->None:
        tl = GenerateToolList()
        self.toollist = tl.rescan()
        self.ui.menuToolScript.clear()
        print("Refresh list\n", str( self.toollist ))

    def actionToolScript(self, action:QAction )->None:
        if action is not None:
            if action.text() in self.toollist:
                from ui.runscript import ScriptKeys, UiRunSimpleNote, UiRunScriptFile
                key = action.text()
                if self.toollist[key].isSimple() :
                    runner = UiRunSimpleNote( self.toollist[key].path() )
                else:
                    runner = UiRunScriptFile( self.toollist[key].path()  )
                runner.run()

    def actionToolScriptUpdateList(self)->None:
        self.ui.menuToolScript.clear()
        keys = sorted( self.toollist.keys() )
        for key in keys :
            recent = self.ui.menuToolScript.addAction( key )
            recent.setData( self.toollist[ key ])
        self.ui.menuToolScript.setEnabled( len( keys ) > 0 )
        
    def actionOpenRecentUpdateFiles(self)->None:
        self.ui.menuOpenRecent.clear()
        fileNames = DilBook().getRecent()
        if fileNames is not None and len( fileNames ) > 0 :
            for entry, bookEntry in enumerate( fileNames , start=1):
                recent_action = self.ui.menuOpenRecent.addAction(
                    '&{:2d}.  {} - {}'.format(
                        entry, bookEntry[BOOK.name], bookEntry[BOOK.location])
                    )
                recent_action.setData( bookEntry[ BOOK.name] )
        # end if len(fileNames)
        self.ui.menuOpenRecent.setEnabled( (len( fileNames ) > 0) )    

    def actionClose(self)->None:
        self.close_book()
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
        self.ui.actionTwo_Pages.setChecked( (layoutType == DbKeys.VALUE_PAGES_SIDE_2))
        self.ui.actionTwo_Pages_Stacked.setChecked( (layoutType == DbKeys.VALUE_PAGES_STACK_2 ))
        self.ui.actionThree_Pages.setChecked( (layoutType == DbKeys.VALUE_PAGES_SIDE_3))
        self.ui.actionThree_Pages_Stacked.setChecked( (layoutType == DbKeys.VALUE_PAGES_STACK_3 ))

    def _setPageLayout( self, value ):
        """ Set the display to either one page or two, depending on what value is in the book entry"""
        self.book.setProperty( DbKeys.SETTING_PAGE_LAYOUT , value)
        self.ui.pageWidget.setDisplay( value )
        self.toggleMenuPages( value )
        self.loadPages()

    def _setSmartPages( self, value ):
        self.book.setProperty( DbKeys.SETTING_SMART_PAGES , value )
        self.smart_pages = value

    def actionOnePage(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_SINGLE)

    def actionTwoPagesSide(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_SIDE_2)

    def actionTwoPagesStacked(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_STACK_2)

    def actionThreePagesSide(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_SIDE_3)

    def actionThreePagesStacked(self)->None:
        self._setPageLayout( DbKeys.VALUE_PAGES_STACK_3)

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
        uiconvert.setBaseDirectory( self.import_dir )
        if uiconvert.exec_():
            self._importPDF( uiconvert.data , uiconvert.getDuplicateList() )
        self.import_dir = str( uiconvert.baseDirectory() )
        del uiconvert

    def actionReimportPDF(self)->None:
        rif = Reimportfile()
        if rif.exec() == QMessageBox.Accepted:
            book = self.book.getBook( book = rif.bookName)
            from util.toolconvert import UiConvertFilenames
            uiconvert = UiConvertFilenames( )
            if not isfile( book[BOOK.source] ) :
                if QMessageBox.Yes == QMessageBox.critical(None,"",
                    "Book cannot be located.\nWould you like to find it?",
                    QMessageBox.No|QMessageBox.Yes ):
                        
                        dlg = QFileDialog(caption= book[BOOK.name ] )
                        dlg.setFileMode( QFileDialog.ExistingFile )
                        dir = os.path.dirname( book[BOOK.source ] )
                        if not os.path.isdir( dir ):
                            dir = self.import_dir
                        dlg.setDirectory( dir )
                        if dlg.exec() :
                            filename = dlg.selectedFiles()[0]
                            book[ BOOK.source ] = filename
                            self.book.update( book=book[ BOOK.name ], location=filename )
                        else:
                            return False
            if uiconvert.processFile( book[ BOOK.source ] ):
                self._importPDF(uiconvert.data, uiconvert.getDuplicateList() )
            del uiconvert
        del rif

    def actionImportDirectory(self)->None:
        from util.toolconvert import UiConvertDirectory
        uiconvert = UiConvertDirectory()
        uiconvert.setBaseDirectory( self.import_dir)
        if uiconvert.exec_():
            self._importPDF( uiconvert.data , uiconvert.getDuplicateList() )
        self.import_dir =  uiconvert.baseDirectory()
        del uiconvert

    def actionCheckIncomplete(self)->None:
        from qdil.book import DilBook
        DilBook().updateIncompleteBooksUI()
        pass

    def introImage( self )->None:
        imagePath = os.path.join( os.path.dirname(__file__) , "images", "sheetmusic.png" )
        if os.path.isfile( imagePath ) :
            px= QPixmap(imagePath)
            self.ui.pageWidget.staticPage ( px)
            self.show()
        

if __name__ == "__main__":
    sy = SystemPreferences()
    dbLocation    = sy.getPathDB()          # Fetch the system settings
    mainDirectory = sy.getDirectory()       # Get directory
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
