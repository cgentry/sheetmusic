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

from re import M
from qdb.keys import DbKeys
from ui.pagewidget import ( PageWidget, PageLabelWidget )
from PySide6.QtCore import (QCoreApplication, QRect,QSize)
from PySide6.QtGui import (QAction, Qt , QKeySequence)
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel,QMenu, QPushButton,
    QMenuBar, QSizePolicy, QStatusBar,
    QSlider, QWidget, QStackedWidget)


class UiMain(object):

    def __init__(self):
        pass

    def setupUi(self, MainWindow):
        self.setupMainWindow( MainWindow )
        self.createActions(MainWindow)
        self.createMenus(MainWindow)
        self.addActions(MainWindow)
        self.setNavigationShortcuts()
        self.setBookmarkShortcuts()
        self.addPageWidgets(MainWindow)
        self.addStatus(MainWindow)

    def getWindow(self):
        return self.mainWindow

    def setupMainWindow( self , MainWindow ):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.mainWindow = MainWindow
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(500, 500))
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        p = MainWindow.palette()
        p.setColor(MainWindow.backgroundRole(), Qt.black)
        MainWindow.setPalette(p)

        MainWindow.setAutoFillBackground( True )

    def createActions(self, MainWindow):
        def action( name , title:str=None, shortcut:str=None, checkable=False , checked=False):
            s = QAction(MainWindow)
            s.setObjectName( u'action' + name )
            s.setCheckable( checkable )
            if checkable:
                s.setChecked( checked )
            if title is None:
                title = name
            s.setText(
                QCoreApplication.translate("MainWindow", title , None))
            if shortcut is not None:
                if isinstance( shortcut, str ):
                    s.setShortcut(
                        QCoreApplication.translate("MainWindow", shortcut, None))
                else:
                    s.setShortcut( shortcut )
            return s

        # FILE actions
        self.actionOpen         = action(u'Open',   title='Open...',  shortcut=QKeySequence.Open)
        self.actionOpenRecent   = action(u'Recent')
        self.actionClose        = action(u"Close",                    shortcut=QKeySequence.Close)
        self.actionDelete       = action(u'Delete', title='Delete...',shortcut=QKeySequence.DeleteEndOfWord)
        self.actionImport       = action(u'Import')
        ### file -> import actions
        self.actionImportPDF    =    action( u'ImportPDF',    title=u'Import PDF ...'  )
        self.actionImportDirectory = action( u'ImportDir',    title=u"Import Directory of PDFs...")
        self.actionReimportPDF =     action( u'ReimportPDF' , title=u'Reimport PDF...')

        # EDIT actions
        self.actionProperties           = action( u"Properties", shortcut=u'Ctrl+I')
        self.actionNoteBook             = action( u"BookNote"  , title="Note for Book")
        self.actionNotePage             = action( u'PageNote'  , title='Note for Page')
        self.actionDeleteAllBookmarks   = action( u'DeleteAllBookmarks', title=u'Delete All Bookmarks')

        # VIEW actions
        self.actionRefresh             = action(u'Refresh'     ,  title=u'Refresh',                 shortcut=QKeySequence.Refresh)
        self.actionShowBookmarks       = action(u"ShowBookmarks", title=u'Show Bookmarks...')
        self.actionOne_Page            = action(u"One_Page"    ,  title=u'One Page'                ,shortcut=u'Ctrl+1', checkable=True,)
        self.actionTwo_Pages           = action(u"Two_Pages"   ,  title=u'Two Pages side-by-side'  ,shortcut=u'Ctrl+2', checkable=True,)
        self.actionThree_Pages         = action(u"Three_Pages" ,  title=u'Three Pages side-by-side',shortcut=u'Ctrl+3', checkable=True,)
        self.actionTwo_Pages_Stacked   = action(u"Two_stack"   ,  title=u'Two Pages Stacked',       shortcut=u'Ctrl+4', checkable=True,)
        self.actionThree_Pages_Stacked = action(u"Three_Stack" ,  title=u'Three Pages Stacked' ,    shortcut=u'Ctrl+5', checkable=True,)
        self.actionAspectRatio         = action(u"AspectRatio" ,  title=u'Keep Aspect ratio',       shortcut=u"Ctrl+A", checkable=True,)
        self.actionSmartPages          = action(u"SmartPages"  ,  title=u'Smart Page Turn',         shortcut=QKeySequence.AddTab, checkable=True,)
        self.actionViewStatus          = action(u'ViewStatus'  ,  title=u'View Status',             shortcut=u'Ctrl+S', checkable=True, checked=True)

        # GO actions (Note: shortcuts are sent in 'setNavigationShortcuts' )
        self.actionUp               = action(u"Up",        title=u'Previous Page')
        self.actionDown             = action(u"Down",      title=u'Next Page')
        self.actionFirstPage        = action(u"FirstPage", title=u'First Page' )
        self.actionLastPage         = action(u"LastPage" , title=u'Last Page' )
        self.actionGo_to_Page       = action(u"Go_to_Page",title=u'Go To Page...')

        self.actionPreviousBookmark = action(u"PreviousBookmark",   title=u'Previous Bookmark')
        self.actionNextBookmark     = action(u"NextBookmark",       title=u'Next Bookmark')

        # TOOL actions (Bookmark controls are set in 'setBookmarkShortcuts')
        self.actionBookmarkCurrentPage  = action(u"BookmarkCurrentPage", title=u'Bookmark current page')
        self.actionAdd_Bookmark         = action(u"Add_Bookmark",        title=u'Add Bookmark...')
        self.actionCheckIncomplete      = action( u"CheckIncomplete",    title=u'Check for incomplete entries ...')
        self.actionToolRefresh          = action( u"RefreshTool",        title=u'Refresh script list')
        #self.actionCleanDB              = action(u'CleanDB',             title=u'Clean Database')
        #self.actionDumpDB               = action(u'DumpDB',              title=u'Backup Database...')
        self.actionToolScript           = action(u'Script')
        # HELP actions
        self.actionHelp = action( u"Help")

        # NOTE: Following tend to be 'special' as they an float to other places
        self.actionPreferences = action( u'Preferences')
        self.actionPreferences.setMenuRole( QAction.PreferencesRole)

        self.actionAbout       = action(u"actionAbout")
        self.actionAbout.setMenuRole( QAction.AboutRole)
     
    def addStatus(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")

        self.label_page_relative = QLabel()
        self.label_page_relative.setObjectName(u'pageRelative')
        self.label_page_relative.setMinimumWidth( 80 )
        self.label_page_relative.setText("")

        self.label_book_note = QLabel()
        self.label_book_note.setObjectName( u'bookNote')
        self.label_book_note.setMinimumWidth( 30 )
        self.setBookNote(True )

        self.label_page_note = QLabel()
        self.label_page_note.setObjectName( u'pageNote')
        self.label_page_note.setMinimumWidth( 30 )
        self.setPageNote(True)

        self.slider_page_position = QSlider()
        self.slider_page_position.setObjectName(u'progressbar')
        self.slider_page_position.setMinimum(1)
        self.slider_page_position.setOrientation(Qt.Horizontal)
        self.slider_page_position.setTracking( True )

        self.label_page_absolute = QLabel()
        self.label_page_absolute.setObjectName(u'pageAbsolute')

        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setObjectName(u'bookmark')
        self.btn_bookmark.setToolTip("Current bookmark")
        self.btn_bookmark.setFlat( True )
        self.btn_bookmark.setText( self._bookmark )

        self.statusbar.addWidget( self.label_page_relative)
        self.statusbar.addWidget( self.label_book_note )
        self.statusbar.addWidget( self.label_page_note )
        #self.statusbar.addWidget( self.btn_bookmark )
        self.statusbar.addWidget( self.slider_page_position,100)
        #
        self.statusbar.addWidget( self.label_page_absolute)

        MainWindow.setStatusBar(self.statusbar)
    
    # White square: "\U00002B1C"
    _blank_note_indicator = "   "
    _double_bar = "\U00002016"
    _bookmark = "\U0001f516"
    def setBookNote(self, flag:bool):
        if flag:
            self.label_book_note.setText( "\U0001F4D3" )
            self.label_book_note.setStyleSheet("border: 3px solid gray")
            self.label_book_note.setToolTip("Note set for book.")
        else:
            self.label_book_note.setText( self._blank_note_indicator) 
            self.label_book_note.setStyleSheet("border: 2px solid lightgray")
            self.label_book_note.setToolTip("")

    def setPageNote(self, flag:bool, page="" ):
        if flag:
            self.label_page_note.setText( "\U0001F4DD" )
            self.label_page_note.setStyleSheet("border: 3px solid gray")
            self.label_page_note.setToolTip("Note set for page {}".format( page ))
        else:
            self.label_page_note.setText( self._blank_note_indicator)
            self.label_page_note.setStyleSheet("border: 2px solid lightgray")
            self.label_page_note.setToolTip("")

    def set_absolute_page( self, absolute:int, total:int, offset_page:int=1 )->None:
        self.label_page_absolute.setText("{} {:>4d} / {:<4d} ".format(self._double_bar, absolute, total))
        tt = "Absolute page / Total pages / Numbering starts on {}\n".format( offset_page ) 
        self.label_page_absolute.setToolTip( tt )
        self.label_page_absolute.setStyleSheet("text-align: center;")

    def createTriggers(self):
        self.setMarkBookmark    = self.actionBookmarkCurrentPage.triggered.connect
        self.setAddBookmark     = self.actionAdd_Bookmark.triggered.connect
        self.setShowBookmarks   = self.actionShowBookmarks.triggered.connect
        self.setImportPDF       = self.actionImportPDF.triggered.connect
        self.setReimportPDF     = self.actionReimportPDF.triggered.connect

    def createMenus(self, MainWindow)->None:
        """
        Create all of the menus
        """
        def menuElement( name:str , title:str=None, shortcut=None,top:bool=True )->QMenu:
            if top:
                s = QMenu( self.menubar )
            else:
                s = QMenu()
            s.setObjectName( u'menu' + name )
            if title == None:
                title = name
            s.setTitle(
                QCoreApplication.translate("MainWindow", name , None))
            return s

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))

        self.menuFile = menuElement( u'File' )
        self.menuEdit = menuElement( u'Edit')
        self.menuView = menuElement( u'View')
        self.menuGo   = menuElement( u'Go' )
        self.menuTools= menuElement( u'Tools')
        self.menuHelp = menuElement( u'Help' )

        self.menuOpenRecent  = menuElement( u'OpenRecent' , 'Open Recent...', top=False)
        self.menuImportPDF   = menuElement( u'ImportPDF'  , 'Import Book from PDF', top=False )
        self.menuReimportPDF = menuElement( u'ReimportPDF', 'Reimport Book from PDF', top=False)
        self.menuImportDirectory = menuElement( u'ScanDir', 'Scan and import books from directory', top=False )
        self.menuToolScript  = menuElement( u'Scripts'    , 'Run Script...', top=False)
        self.menuToolRefresh = menuElement( u'ToolRefresh' , 'Refresh script list', top=False)

    def addActions(self, MainWindow)->None:
        ## Add top level menus to the menubar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuGo.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        ## attach actions to top level menus
        self.addFileActions()
        self.addEditActions()        
        self.addViewActions()
        self.addGoActions()
        self.addToolActions()
        self.addHelpActions()

    def addFileActions(self)->None:
        self.menuFile.addAction(self.actionOpen)
        self.actionOpenRecent = self.menuFile.addMenu( self.menuOpenRecent )
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction( self.actionDelete )
        self.menuFile.addSeparator()   # -------------------
        # import submenu...
        self.menuImport = self.menuFile.addMenu( "Import")
        self.menuImport.setTitle('Import music')
        self.menuImport.addAction( self.actionImportPDF )
        self.menuImport.addAction( self.actionReimportPDF)
        self.menuImport.addAction( self.actionImportDirectory)
        self.menuImport.addAction( self.actionCheckIncomplete)

        self.menuFile.addSeparator()   # -------------------
        self.menuFile.addAction(self.actionPreferences)

    def addEditActions(self)->None:
        self.menuEdit.addAction(self.actionProperties)
        self.menuEdit.addAction(self.actionNoteBook)
        self.menuEdit.addAction(self.actionNotePage)
        self.menuEdit.addSeparator()   # -------------------
        self.menuEdit.addAction( self.actionDeleteAllBookmarks )

    def addViewActions(self)->None:
        self.menuView.addAction( self.actionRefresh )
        self.menuView.addAction( self.actionShowBookmarks )
        self.menuView.addSeparator()   # -------------------
        self.menuView.addAction(self.actionOne_Page)
        self.menuView.addAction(self.actionTwo_Pages)
        self.menuView.addAction(self.actionThree_Pages)
        self.menuView.addAction(self.actionTwo_Pages_Stacked)
        self.menuView.addAction(self.actionThree_Pages_Stacked)
        self.menuView.addSeparator()   # -------------------
        self.menuView.addAction( self.actionAspectRatio)
        self.menuView.addAction(self.actionViewStatus)
        self.menuView.addAction( self.actionSmartPages )
        self.menuView.addSeparator()   # -------------------

    def addGoActions(self)->None:
        self.menuGo.addAction(self.actionUp)
        self.menuGo.addAction(self.actionDown)
        self.menuGo.addSeparator()   # -------------------
        self.menuGo.addAction(self.actionFirstPage)
        self.menuGo.addAction(self.actionLastPage)
        self.menuGo.addAction(self.actionGo_to_Page)
        self.menuGo.addSeparator()   # -------------------
        self.menuGo.addAction(self.actionPreviousBookmark)
        self.menuGo.addAction(self.actionNextBookmark)

    def addToolActions(self)->None:
        self.menuTools.addAction(self.actionBookmarkCurrentPage)
        self.menuTools.addAction(self.actionAdd_Bookmark)
        self.menuTools.addSeparator()   # -------------------
        self.actionToolScript = self.menuTools.addMenu( self.menuToolScript )
        self.menuTools.addAction( self.actionToolRefresh )
        #self.menuTools.addAction( self.actionCleanDB )
        #self.menuTools.addAction( self.actionDumpDB )

    def addHelpActions(self)->None:
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionHelp)
        
    def setNavigationShortcuts(self, overrides:dict=None):
        """
            Set the navigation shortcut. You can pass a dictionary of values
            in and those setting will override the defaults. Th dictionary
            can contain other entries - that won't affect the operation.
        """
        navigationShortcut = {
            DbKeys.SETTING_PAGE_PREVIOUS :      u'Up',
            DbKeys.SETTING_BOOKMARK_PREVIOUS:   u'Alt+Up',
            DbKeys.SETTING_PAGE_NEXT:           u'Down',
            DbKeys.SETTING_BOOKMARK_NEXT:       u'Alt+Down',
            DbKeys.SETTING_FIRST_PAGE_SHOWN:    u"Alt+Ctrl+Left",
            DbKeys.SETTING_LAST_PAGE_SHOWN:     u"Alt+Ctrl+Right",
        }
        if overrides is not None:
            navigationShortcut.update( overrides )

        def shortcut( name:str, action:QAction):
            action.setShortcut( 
                QCoreApplication.translate("MainWindow", navigationShortcut[name], None)
            )

        shortcut( DbKeys.SETTING_PAGE_PREVIOUS,         self.actionUp)
        shortcut( DbKeys.SETTING_BOOKMARK_PREVIOUS,     self.actionPreviousBookmark)
        shortcut( DbKeys.SETTING_PAGE_NEXT,             self.actionDown)
        shortcut( DbKeys.SETTING_BOOKMARK_NEXT,         self.actionNextBookmark)
        shortcut( DbKeys.SETTING_FIRST_PAGE_SHOWN,      self.actionFirstPage)
        shortcut( DbKeys.SETTING_LAST_PAGE_SHOWN,       self.actionLastPage)              

    def setBookmarkShortcuts(self, overrides:dict=None):
        bookmarkShortcut = {
            'markBookmark' :    u'Ctrl+D',
            'showBookmark' :    u'Shift+Ctrl+D',
            'addBookmark':      u'Alt+B',
        }
        if overrides is not None:
            bookmarkShortcut.update( overrides )
            
        def shortcut( name, action:QAction):
            action.setShortcut( 
                QCoreApplication.translate("MainWindow", bookmarkShortcut[name], None)
            )

        # Shortcuts
        shortcut( 'showBookmark',        self.actionShowBookmarks)
        shortcut( 'markBookmark',        self.actionBookmarkCurrentPage)
        shortcut( 'addBookmark',         self.actionAdd_Bookmark)

    def addPageWidgets(self, MainWindow):
        self.pageWidget = PageWidget(MainWindow)
        self.pager = self.pageWidget.getMainPageWidget()
        MainWindow.setCentralWidget(self.pager )

    def statusText( self, statusTxt=""):
        self.statusbar.showMessage( statusTxt )

