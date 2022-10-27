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
        p = MainWindow.palette()
        p.setColor(MainWindow.backgroundRole(), Qt.black)
        MainWindow.setPalette(p)

        MainWindow.setAutoFillBackground( True )
        self.createActions(MainWindow)
        self.createMenus(MainWindow)
        self.addActions(MainWindow)
        self.addMenuBookmark(MainWindow)
        self.addStatus(MainWindow)
        self.retranslateUi(MainWindow)

    def getWindow(self):
        return self.mainWindow

    def createActions(self, MainWindow):
        # Action Open
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen_Recent = QAction(MainWindow)
        self.actionOpen_Recent.setObjectName(u"actionOpen_Recent")
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u'actionDelete')

        # Import Files: PDF, Check Incomplete, 
        self.actionImport = QAction( MainWindow )

        self.actionImportPDF = QAction(MainWindow)
        self.actionImportPDF.setObjectName(u'actionImportPDF')

        self.actionImportDirectory = QAction(MainWindow)
        self.actionImportDirectory.setObjectName(u"actionImportDirectory")

        self.actionReimportPDF = QAction(MainWindow)
        self.actionReimportPDF.setObjectName(u'actionReimportPDF')

        self.actionCheckIncomplete = QAction(MainWindow)
        self.actionCheckIncomplete.setObjectName( u"actionCheckIncomplete")
        
        # Action Properties
        self.actionProperties = QAction(MainWindow)
        self.actionProperties.setObjectName(u"actionProperties")

        self.actionDeleteAllBookmarks = QAction(MainWindow)
        self.actionDeleteAllBookmarks.setObjectName( u'actionDeleteAllBookmarks')

        # Action Close
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")

        # Preferences
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u'preferences')
        self.actionPreferences.setMenuRole( QAction.PreferencesRole)

        # Action Pages
        self.actionOne_Page = QAction(MainWindow)
        self.actionOne_Page.setObjectName(u"actionOne_Page")
        self.actionOne_Page.setCheckable(True)

        self.actionTwo_Pages = QAction(MainWindow)
        self.actionTwo_Pages.setObjectName(u"actionTwo_Pages")
        self.actionTwo_Pages.setCheckable(True)

        # Aspect Ratio
        self.actionAspectRatio = QAction(MainWindow)
        self.actionAspectRatio.setObjectName(u'actionAspectRatio')
        self.actionAspectRatio.setCheckable(True)

        # Smart Pages
        self.actionSmartPages = QAction( MainWindow )
        self.actionSmartPages.setObjectName(u'actionSmartPages')
        self.actionSmartPages.setCheckable(True)
        

        # Status Bar
        self.actionViewStatus = QAction(MainWindow)
        self.actionViewStatus.setObjectName(u"actionViewStatus")
        self.actionViewStatus.setChecked(True)
        self.actionViewStatus.setCheckable(True)
        
        # Action About
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAbout.setMenuRole( QAction.AboutRole)

        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")

        #### Navigation
        self.actionUp = QAction(MainWindow)
        self.actionUp.setObjectName(u"actionUp")
        self.actionDown = QAction(MainWindow)
        self.actionDown.setObjectName(u"actionDown")

        # Page Navigation
        self.actionGo_to_Page = QAction(MainWindow)
        self.actionGo_to_Page.setObjectName(u"actionGo_to_Page")

        self.actionFirstPage=QAction(MainWindow)
        self.actionFirstPage.setObjectName(u"actionFirstPage")

        self.actionLastPage=QAction(MainWindow)
        self.actionLastPage.setObjectName(u"actionLastPage")

        # Bookmarks
        self.actionPreviousBookmark=QAction(MainWindow)
        self.actionPreviousBookmark.setObjectName(u"actionPreviousBookmark")
        
        self.actionNextBookmark=QAction(MainWindow)
        self.actionNextBookmark.setObjectName(u"actionNextBookmark")

        #self.actionBookmark = QAction(MainWindow)
        #self.actionBookmark.setObjectName(u"actionBookmark")

        self.actionBookmarkCurrentPage = QAction(MainWindow)
        self.actionBookmarkCurrentPage.setObjectName(u"actionBookmarkCurrentPage")
        
        self.actionAdd_Bookmark = QAction(MainWindow)
        self.actionAdd_Bookmark.setObjectName(u"actionAdd_Bookmark")

        self.actionCleanDB = QAction(MainWindow)
        self.actionCleanDB.setObjectName( u'actionCleanDB')

        self.actionDumpDB = QAction(MainWindow)
        self.actionDumpDB.setObjectName( u'actionDumpDB')

        self.actionShowBookmarks = QAction(MainWindow)
        self.actionShowBookmarks.setObjectName(u"actionShowBookmarks")

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
        self.setMarkBookmark = self.actionBookmarkCurrentPage.triggered.connect
        self.setAddBookmark = self.actionAdd_Bookmark.triggered.connect
        self.setShowBookmarks = self.actionShowBookmarks.triggered.connect
        self.setImportPDF = self.actionImportPDF.triggered.connect
        self.setReimportPDF = self.actionReimportPDF.triggered.connect

# Create Menus
    def createMenus(self, MainWindow)->bool:
        """
        Create all of the menus
        """
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))

        # File Menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")

        # Edit Menu
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")

        # View Menu
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")

        # Go Menu
        self.menuGo = QMenu(self.menubar)
        self.menuGo.setObjectName(u"menuGo")

        # Tools Menu
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")

        # Help Menu
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        
        # Link menubar to main window
        MainWindow.setMenuBar(self.menubar)
       
        # File actions
        self.menuOpen_Recent = QMenu()
        self.menuOpen_Recent.setTitle('Open Recent...')
        self.menuDelete = QMenu()
        self.menuDelete.setTitle("Delete")

        
        self.menuImportPDF = QMenu()
        self.menuImportPDF.setTitle( 'Import Book from PDF')
        self.menuReimportPDF = QMenu()
        self.menuReimportPDF.setTitle( 'Reimport Book from PDF')
        self.menuImportDirectory = QMenu()
        self.menuImportDirectory.setTitle('Scan and import books from directory')


    def addActions(self, MainWindow):
        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.actionOpen_Recent = self.menuFile.addMenu( self.menuOpen_Recent )

        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction( self.actionDelete )

        self.menuFile.addSeparator()
        self.menuImport = self.menuFile.addMenu( "Import")
        self.menuImport.setTitle('Import music')
        self.menuImport.addAction( self.actionImportPDF )
        self.menuImport.addAction( self.actionReimportPDF)
        self.menuImport.addAction( self.actionImportDirectory)
        self.menuImport.addAction( self.actionCheckIncomplete)

        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)

        # Edit actions
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuEdit.addAction(self.actionProperties)
        
        self.menuEdit.addSeparator()
        self.menuEdit.addAction( self.actionDeleteAllBookmarks )

        # View actions
        self.addViewActions()
    

        # Go actions
        self.menubar.addAction(self.menuGo.menuAction())
        self.menuGo.addAction(self.actionUp)
        self.menuGo.addAction(self.actionDown)
        self.menuGo.addSeparator()
        self.menuGo.addAction(self.actionFirstPage)
        self.menuGo.addAction(self.actionLastPage)
        self.menuGo.addAction(self.actionGo_to_Page)
        
        # Tool actions
        self.menubar.addAction(self.menuTools.menuAction())
        
        # Help actions
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionHelp)

        self.addPageWidgets(MainWindow)
        return True
# end createMenus

    def addViewActions(self)->None:
        self.menubar.addAction(self.menuView.menuAction())
        
        self.menuView.addAction( self.actionShowBookmarks )
        
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionOne_Page)
        self.menuView.addAction(self.actionTwo_Pages)

        self.menuView.addSeparator()
        self.menuView.addAction( self.actionAspectRatio)
        self.menuView.addAction(self.actionViewStatus)
        self.menuView.addAction( self.actionSmartPages )
        self.menuView.addSeparator()

    def addMenuBookmark( self , MainWindow):
        self.menuGo.addSeparator()
        self.menuGo.addAction(self.actionPreviousBookmark)
        self.menuGo.addAction(self.actionNextBookmark)

        self.menuEdit.addSeparator()
        self.menuTools.addAction(self.actionBookmarkCurrentPage)
        self.menuTools.addAction(self.actionAdd_Bookmark)
        self.menuTools.addSeparator()
        self.menuTools.addAction( self.actionCleanDB )
        self.menuTools.addAction( self.actionDumpDB )

        

# ReTranslate UI
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate(
            "MainWindow", u"MainWindow", None))

        self.actionOpen.setText(
            QCoreApplication.translate("MainWindow", u"Open...", None))
        self.actionOpen.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+O", None))

        self.actionProperties.setText(
            QCoreApplication.translate("MainWindow", u"Properties...",None))
        self.actionProperties.setShortcut(
            QCoreApplication.translate("Properties", u"Ctrl+I", None))

        self.actionDeleteAllBookmarks.setText(
            QCoreApplication.translate( 'MainWindow', u"Delete All Bookmarks", None))

        self.actionPreferences.setText(
            QCoreApplication.translate("MainWindow",u"Preferences...", None))

        self.actionOpen_Recent.setText(
            QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.actionDelete.setText(
            QCoreApplication.translate("MainWindow", u"Delete...", None))

        self.actionClose.setText(
            QCoreApplication.translate("MainWindow", u"Close", None))

        self.actionClose.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))

        self.actionOne_Page.setText(
            QCoreApplication.translate("MainWindow", u"One Page", None))

        self.actionOne_Page.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+1", None))

        self.actionTwo_Pages.setText(
            QCoreApplication.translate("MainWindow", u"Two Pages", None))

        self.actionTwo_Pages.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+2", None))

        self.actionAspectRatio.setText(
            QCoreApplication.translate("MainWindow", u"Keep Aspect Ratio", None))
        self.actionAspectRatio.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+A", None))

        self.actionSmartPages.setText(
            QCoreApplication.translate("MainWindow", u"Smart Page Turn", None))

        self.actionViewStatus.setText(
            QCoreApplication.translate("MainWindow", u"View Status Bar", None))

        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", u"About", None))
        self.actionHelp.setText(
            QCoreApplication.translate("MainWindow", u"Help", None))

        self.actionUp.setText(
            QCoreApplication.translate("MainWindow", u"Previous Page", None))
        self.actionUp.setShortcut(
            QCoreApplication.translate("MainWindow", u"Up", None))

        self.actionDown.setText(
            QCoreApplication.translate("MainWindow", u"Next Page", None))
        self.actionDown.setShortcut(
            QCoreApplication.translate("MainWindow", u"Down", None))

        self.actionFirstPage.setText(
            QCoreApplication.translate("MainWindow", u"First Page", None))
        self.actionFirstPage.setShortcut(
            QCoreApplication.translate("MainWindow", u"Alt+Ctrl+Left", None))  

        self.actionLastPage.setText(
            QCoreApplication.translate("MainWindow", u"Last Page", None))
        self.actionLastPage.setShortcut(
            QCoreApplication.translate("MainWindow", u"Alt+Ctrl+Right", None))           

        
        self.actionGo_to_Page.setText(QCoreApplication.translate(
            "MainWindow", u"Go to Page...", None))
        self.actionGo_to_Page.setShortcut(
            QCoreApplication.translate("MainWindow", u"Ctrl+Alt+G", None))

        #########
        # Tools
        #########
        
        self.actionImport.setText(QCoreApplication.translate(
            "MainWindow", u"Import ...", None))
        self.actionImportDirectory.setText(QCoreApplication.translate(
            "MainWindow", u"Import Directory of books ...", None))

        self.actionImportPDF.setText(QCoreApplication.translate(
            "MainWindow", u"Import PDF ...", None))

        self.actionReimportPDF.setText(QCoreApplication.translate(
            "MainWindow", u"Reimport PDF ...", None))

        self.actionCheckIncomplete.setText(QCoreApplication.translate(
            "MainWindow", u"Check for incomplete entries ...", None))

        self.menuFile.setTitle(
            QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(
            QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(
            QCoreApplication.translate("MainWindow", u"View", None))
        self.menuGo.setTitle(
            QCoreApplication.translate("MainWindow", u"Go", None))
        self.menuTools.setTitle(
            QCoreApplication.translate("MainWindow", u"Tools", None))
        self.menuHelp.setTitle(
            QCoreApplication.translate("MainWindow", u"Help", None))
        # retranslateUi

        self.translateBookmarkOptions()
        self.setNavigationShortcuts()
        self.setBookmarkShortcuts()
# End retranslateUi

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

    def translateBookmarkOptions(self):
        def xlate( newLabel, action:QAction):
            action.setText(
                QCoreApplication.translate("MainWindow",newLabel, None)
            )
        # Labels
        xlate( u'Previous Bookmark',     self.actionPreviousBookmark)
        xlate( u'Next Bookmark',         self.actionNextBookmark)
        xlate( u'Bookmarks ...',         self.actionShowBookmarks)
        xlate( u'Bookmark current page', self.actionBookmarkCurrentPage)
        xlate( u'Add Bookmark',          self.actionAdd_Bookmark)
        xlate( u'Clean DB',              self.actionCleanDB )
        xlate( u'Backup DB to file...' ,   self.actionDumpDB )
    ## end translateBookmarkOptions

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
    ## end setBookmarkShortcuts
        
    def addPageWidgets(self, MainWindow):
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.centralWidget = QStackedWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        sizePolicy.setHeightForWidth(
            self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setAutoFillBackground(True)
        MainWindow.setCentralWidget(self.centralWidget)

        self.centralWidget.addWidget(self.addTwoPagesSide(MainWindow))


# addTwoPagesSide


    def addTwoPagesSide(self, MainWindow)->QWidget:
        self.left = QLabel()
        self.left.setObjectName(u"left")
        self.left.setScaledContents(False)
        self.left.setAlignment(Qt.AlignCenter)
        self.left.setMargin(5)
        self.right = QLabel()
        self.right.setObjectName(u"right")
        self.right.setScaledContents(False)
        self.right.setAlignment(Qt.AlignCenter)
        self.right.setMargin(5)

        self.twoPagesSide = QWidget()
        self.twoPagesSide.setObjectName(u"twoPagesSide")
        self.twoPagesSide.setEnabled(True)
        self.twoPagesSide.setVisible(True)
        self.twoPagesSide.grabGesture(Qt.SwipeGesture)

        self.twoPagesSideLayout = QHBoxLayout(self.twoPagesSide)
        self.twoPagesSideLayout.setObjectName(u"horizontalLayoutWidget")
        self.twoPagesSideLayout.setContentsMargins(0, 0, 0, 0)
        self.twoPagesSideLayout.addWidget(self.left, 1)
        self.twoPagesSideLayout.addWidget(self.right, 1)

        self.rightPageAdded = True

        return self.twoPagesSide

    def isRightPageShown(self)->bool:
        return self.rightPageAdded

    def showRightPage( self, showRightPage:bool):
        if showRightPage :
            if not self.rightPageAdded:
                self.twoPagesSideLayout.addWidget(self.right, 1)
                self.rightPageAdded = True
            self.right.show()
        else: 
            self.right.clear()
            self.right.hide()
            if self.rightPageAdded:
                self.twoPagesSideLayout.removeWidget(self.right)
                self.rightPageAdded = False

    def statusText( self, statusTxt=""):
        self.statusbar.showMessage( statusTxt )

# end addTwoPagseSide
