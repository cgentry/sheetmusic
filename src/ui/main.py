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

from re import M
from qdb.keys import DbKeys
from ui.pagewidget import ( PageWidget, PageLabelWidget )
from PySide6.QtCore import (QCoreApplication, QRect,QSize)
from PySide6.QtGui import (QAction, Qt )
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
                s.setShortcut(
                    QCoreApplication.translate("MainWindow", shortcut, None))
            return s

        # FILE actions
        self.actionOpen         = action(u'Open',   title='Open...',  shortcut=u'Ctrl+O')
        self.actionOpen_Recent  = action(u'Recent')
        self.actionClose        = action(u"Close",                    shortcut=u"Ctrl+W")
        self.actionDelete       = action(u'Delete', title='Delete...')
        self.actionImport       = action(u'Import')
        ### file -> import actions
        self.actionImportPDF    = action(u'ImportPDF',    title=u'Import PDF ...')
        self.actionImportDirectory = action(u'ImportDir', title=u"Import Directory of PDFs...")
        self.actionReimportPDF = action( u'ReimportPDF' , title=u'Reimport PDF...')

        # EDIT actions
        self.actionProperties           = action( u"Properties", shortcut=u'Ctrl+I')
        self.actionDeleteAllBookmarks   = action( u'DeleteAllBookmarks', title=u'Delete All Bookmarks')

        # VIEW actions
        self.actionShowBookmarks    = action(u"ShowBookmarks",                title=u'Show Bookmarks...')
        self.actionOne_Page         = action(u"One_Page"    , checkable=True, title=u'One Page', shortcut=u'Ctrl+1')
        self.actionTwo_Pages        = action(u"Two_Pages"   , checkable=True, title=u'Two Pages side-by-side' , shortcut='Ctrl+2')
        self.actionStack_Pages      = action(u"Stack_Pages" , checkable=True, title=u'Two Pages Stacked',       shortcut=u'Ctrl+2')
        self.actionAspectRatio      = action(u"AspectRatio" , checkable=True, title=u'Keep Aspect ratio',       shortcut=u"Ctrl+A")
        self.actionSmartPages       = action(u"SmartPages"  , checkable=True, title=u'Smart Page Turn')
        self.actionViewStatus       = action('ViewStatus'   , checkable=True, title=u'View Status', checked=True)

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
        self.actionCleanDB              = action(u'CleanDB',             title=u'Clean Database')
        self.actionDumpDB               = action(u'DumpDB',              title=u'Backup Database...')

        # HELP actions
        self.actionHelp = action( u"Help")

        # NOTE: Following tend to be 'special' as they an float to other places
        self.actionPreferences = action( u'Preferences')
        self.actionPreferences.setMenuRole( QAction.PreferencesRole)
        self.actionAbout = action(u"actionAbout")
        self.actionAbout.setMenuRole( QAction.AboutRole)
     
    def addStatus(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")

        self.lblPageRelative = QLabel()
        self.lblPageRelative.setObjectName(u'pageRelative')
        self.lblPageRelative.setText("*")

        self.statusProgress = QSlider()
        self.statusProgress.setObjectName(u'progressbar')
        self.statusProgress.setMinimum(1)
        self.statusProgress.setOrientation(Qt.Horizontal)
        self.statusProgress.setTracking( True )

        self.lblPageAbsolute = QLabel()
        self.lblPageAbsolute.setObjectName(u'pageAbsolute')
        self.lblPageAbsolute.setToolTip("Absolute book page")

        self.lblBookmark = QPushButton()
        self.lblBookmark.setObjectName(u'bookmark')
        self.lblBookmark.setToolTip("Current bookmark")
        self.lblBookmark.setFlat( True )

        self.statusbar.addWidget( self.lblPageRelative)
        self.statusbar.addWidget( self.statusProgress,100)
        self.statusbar.addWidget( self.lblBookmark )
        self.statusbar.addWidget( self.lblPageAbsolute)

        MainWindow.setStatusBar(self.statusbar)

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

        self.menuOpen_Recent = menuElement( u'OpenRecent' , 'Open Recent...', top=False)
        self.menuImportPDF   = menuElement( u'ImportPDF'  , 'Import Book from PDF', top=False )
        self.menuReimportPDF = menuElement( u'ReimportPDF', 'Reimport Book from PDF', top=False)
        self.menuImportDirectory = menuElement( u'ScanDir', 'Scan and import books from directory', top=False )

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
        self.actionOpen_Recent = self.menuFile.addMenu( self.menuOpen_Recent )
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction( self.actionDelete )
        self.menuFile.addSeparator()   # -------------------
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
        self.menuEdit.addSeparator()   # -------------------
        self.menuEdit.addAction( self.actionDeleteAllBookmarks )

    def addViewActions(self)->None:
        self.menuView.addAction( self.actionShowBookmarks )
        self.menuView.addSeparator()   # -------------------
        self.menuView.addAction(self.actionOne_Page)
        self.menuView.addAction(self.actionTwo_Pages)
        self.menuView.addAction(self.actionStack_Pages)
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
        self.menuTools.addAction( self.actionCleanDB )
        self.menuTools.addAction( self.actionDumpDB )

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

