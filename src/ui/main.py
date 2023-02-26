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
from ui.pagewidget import (PageWidget, PageLabelWidget)
from PySide6.QtCore import (QCoreApplication, QRect, QSize)
from PySide6.QtGui import (QAction, Qt, QKeySequence)
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMenu, QPushButton,
    QMenuBar, QSizePolicy, QStatusBar,
    QSlider, QWidget, QStackedWidget)


class UiMain(object):

    def __init__(self):
        pass

    def setupUi(self, MainWindow):
        self.setupMainWindow(MainWindow)
        self.createActions(MainWindow)
        self.createMenus(MainWindow)
        self.addActions(MainWindow)
        self.setNavigationShortcuts()
        self.setBookmarkShortcuts()
        self.addPageWidgets(MainWindow)
        self.addStatus(MainWindow)

    def getWindow(self):
        return self.mainWindow

    def setupMainWindow(self, MainWindow):
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
        MainWindow.setWindowTitle(QCoreApplication.translate(
            "MainWindow", u"MainWindow", None))
        p = MainWindow.palette()
        p.setColor(MainWindow.backgroundRole(), Qt.black)
        MainWindow.setPalette(p)

        MainWindow.setAutoFillBackground(True)

    def createActions(self, MainWindow):
        def action(name, title: str = None, shortcut: str = None, checkable=False, checked=False):
            s = QAction(MainWindow)
            s.setObjectName(u'action' + name)
            s.setCheckable(checkable)
            if checkable:
                s.setChecked(checked)
            if title is None:
                title = name
            s.setText(
                QCoreApplication.translate("MainWindow", title, None))
            if shortcut is not None:
                if isinstance(shortcut, str):
                    s.setShortcut(
                        QCoreApplication.translate("MainWindow", shortcut, None))
                else:
                    s.setShortcut(shortcut)
            return s

        # FILE actions
        self.action_file_open = action(
            u'Open',   title='Open...',  shortcut=QKeySequence.Open)
        self.action_file_open_recent = action(u'Recent')
        self.action_file_reopen = action(u'Reopen', title="Reopen")
        self.action_file_close = action(
            u"Close",                    shortcut=QKeySequence.Close)
        self.action_file_delete = action(
            u'Delete', title='Delete...', shortcut=QKeySequence.DeleteEndOfWord)
        self.action_file_import = action(u'Import')
        self.action_file_library = action(u'Library')

        # file -> import actions
        self.action_file_select_import = action(
            u'SelectImport', title=u'Select Import Script ...')
        self.action_file_import_PDF = action(
            u'ImportPDF',    title=u'Import PDF ...')
        self.action_file_import_dir = action(
            u'ImportDir',    title=u"Import Directory of PDFs...")
        self.action_file_reimport_PDF = action(
            u'ReimportPDF', title=u'Reimport PDF...')
        
        self.action_file_import_images = action(
            u'ImportImages', title=u'Import directory of images...' )
        self.action_file_import_images_dir = action(
            u'ImportImagesDir', title=u'Import directory holding multiple directories of images...' )
        
        # file -> Library actions
        self.action_file_library_consolidate = action(
            u'LibraryConsolidate', title=u'Consolidate library entries...' )
        self.action_file_library_check = action(
            u'LibraryCheck', title=u'Check library for consistency...' )

        # EDIT actions
        self.action_edit_page = action(
            u'PageEdit', title='Edit Page #', shortcut=u'Ctrl+E')
        self.action_edit_properties = action(u"Properties", shortcut=u'Ctrl+I')
        self.action_edit_note_book = action(u"BookNote", title="Note for Book")
        self.action_edit_note_page = action(u'PageNote', title='Note for Page')
        

        # VIEW actions
        self.action_refresh = action(
            u'Refresh',  title=u'Refresh',                 shortcut=QKeySequence.Refresh)
        
        self.actionOne_Page = action(
            u"One_Page",  title=u'One Page', shortcut=u'Ctrl+1', checkable=True,)
        self.actionTwo_Pages = action(
            u"Two_Pages",  title=u'Two Pages side-by-side', shortcut=u'Ctrl+2', checkable=True,)
        self.actionThree_Pages = action(
            u"Three_Pages",  title=u'Three Pages side-by-side', shortcut=u'Ctrl+3', checkable=True,)
        self.actionTwo_Pages_Stacked = action(
            u"Two_stack",  title=u'Two Pages Stacked',       shortcut=u'Ctrl+4', checkable=True,)
        self.actionThree_Pages_Stacked = action(
            u"Three_Stack",  title=u'Three Pages Stacked',    shortcut=u'Ctrl+5', checkable=True,)
        self.actionAspectRatio = action(
            u"AspectRatio",  title=u'Keep Aspect ratio',       shortcut=u"Ctrl+A", checkable=True,)
        self.actionSmartPages = action(
            u"SmartPages",  title=u'Smart Page Turn',         shortcut=QKeySequence.AddTab, checkable=True,)
        self.actionViewStatus = action(u'ViewStatus',  title=u'View Status',
                                       shortcut=u'Ctrl+S', checkable=True, checked=True)

        # GO actions (Note: shortcuts are sent in 'setNavigationShortcuts' )
        self.actionUp = action(u"Up",        title=u'Previous Page')
        self.actionDown = action(u"Down",      title=u'Next Page')
        self.actionFirstPage = action(u"FirstPage", title=u'First Page')
        self.actionLastPage = action(u"LastPage", title=u'Last Page')
        self.actionGo_to_Page = action(u"Go_to_Page", title=u'Go To Page...')

        # BOOKMARK actions
        self.action_bookmark_previous = action(
            u"PreviousBookmark",   title=u'Previous Bookmark')
        self.action_bookmark_next = action(
            u"NextBookmark",       title=u'Next Bookmark')
        self.action_bookmark_delete_all = action(
            u'DeleteAllBookmarks', title=u'Delete All Bookmarks')
        self.action_bookmark_show_all = action(
            u"ShowBookmarks", title=u'Show Bookmarks...')
        self.action_bookmark_current = action(
            u"BookmarkCurrentPage", title=u'Bookmark current page')
        self.action_bookmark_add = action(
            u"Add_Bookmark",        title=u'Add Bookmark...')

        # TOOL actions (Bookmark controls are set in 'setBookmarkShortcuts')
        self.action_tool_check = action(
            u"CheckIncomplete",    title=u'Check for incomplete entries ...')
        self.action_tool_refresh = action(
            u"RefreshTool",        title=u'Refresh script list')
        self.actionToolScript = action(u'Script')

        # HELP actions
        self.action_help = action(u"Help")

        # NOTE: Following tend to be 'special' as they an float to other places
        self.action_edit_preferences = action(u'Preferences')
        self.action_edit_preferences.setMenuRole(QAction.PreferencesRole)

        self.action_help_about = action(u"action_help_about")
        self.action_help_about.setMenuRole(QAction.AboutRole)

    def addStatus(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")

        self.label_page_relative = QLabel()
        self.label_page_relative.setObjectName(u'pageRelative')
        self.label_page_relative.setMinimumWidth(80)
        self.label_page_relative.setText("")

        self.label_book_note = QLabel()
        self.label_book_note.setObjectName(u'bookNote')
        self.label_book_note.setMinimumWidth(30)
        self.setBookNote(True)

        self.label_page_note = QLabel()
        self.label_page_note.setObjectName(u'pageNote')
        self.label_page_note.setMinimumWidth(30)
        self.setPageNote(True)

        self.slider_page_position = QSlider()
        self.slider_page_position.setObjectName(u'progressbar')
        self.slider_page_position.setMinimum(1)
        self.slider_page_position.setOrientation(Qt.Horizontal)
        self.slider_page_position.setTracking(True)

        self.label_page_absolute = QLabel()
        self.label_page_absolute.setObjectName(u'pageAbsolute')

        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setObjectName(u'bookmark')
        self.btn_bookmark.setToolTip("Current bookmark")
        self.btn_bookmark.setFlat(True)
        self.btn_bookmark.setText(self._bookmark)

        self.statusbar.addWidget(self.label_page_relative)
        self.statusbar.addWidget(self.label_book_note)
        self.statusbar.addWidget(self.label_page_note)
        # self.statusbar.addWidget( self.btn_bookmark )
        self.statusbar.addWidget(self.slider_page_position, 100)
        #
        self.statusbar.addWidget(self.label_page_absolute)

        MainWindow.setStatusBar(self.statusbar)

    # White square: "\U00002B1C"
    _blank_note_indicator = "   "
    _double_bar = "\U00002016"
    _bookmark = "\U0001f516"

    def setBookNote(self, flag: bool):
        if flag:
            self.label_book_note.setText("\U0001F4D3")
            self.label_book_note.setStyleSheet("border: 3px solid gray")
            self.label_book_note.setToolTip("Note set for book.")
        else:
            self.label_book_note.setText(self._blank_note_indicator)
            self.label_book_note.setStyleSheet("border: 2px solid lightgray")
            self.label_book_note.setToolTip("")

    def setPageNote(self, flag: bool, page=""):
        if flag:
            self.label_page_note.setText("\U0001F4DD")
            self.label_page_note.setStyleSheet("border: 3px solid gray")
            self.label_page_note.setToolTip(
                "Note set for page {}".format(page))
        else:
            self.label_page_note.setText(self._blank_note_indicator)
            self.label_page_note.setStyleSheet("border: 2px solid lightgray")
            self.label_page_note.setToolTip("")

    def set_absolute_page(self, absolute: int, total: int, offset_page: int = 1) -> None:
        self.label_page_absolute.setText(
            "{} {:>4d} / {:<4d} ".format(self._double_bar, absolute, total))
        tt = "Absolute page / Total pages / Numbering starts on {}\n".format(
            offset_page)
        self.label_page_absolute.setToolTip(tt)
        self.label_page_absolute.setStyleSheet("text-align: center;")

    def createTriggers(self):
        self.setMarkBookmark = self.action_bookmark_current.triggered.connect
        self.setAddBookmark = self.action_bookmark_add.triggered.connect
        self.setShowBookmarks = self.action_bookmark_show_all.triggered.connect
        self.setImportScript = self.action_file_select_import.triggered.connect
        self.setImportPDF = self.action_file_import_PDF.triggered.connect
        self.setReimportPDF = self.action_file_reimport_PDF.triggered.connect

    def createMenus(self, MainWindow) -> None:
        """
        Create all of the menus
        """
        def menuElement(name: str, title: str = None, shortcut=None, top: bool = True) -> QMenu:
            if top:
                s = QMenu(self.menubar)
            else:
                s = QMenu()
            s.setObjectName(u'menu' + name)
            if title == None:
                title = name
            s.setTitle(
                QCoreApplication.translate("MainWindow", name, None))
            return s

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))

        self.menuFile = menuElement(u'File')
        self.menuEdit = menuElement(u'Edit')
        self.menuView = menuElement(u'View')
        self.menuGo = menuElement(u'Go')
        self.menuBookmark = menuElement( u'Bookmark')
        self.menuTools = menuElement(u'Tools')
        self.menuHelp = menuElement(u'Help')

        self.menuOpenRecent = menuElement(
            u'OpenRecent', 'Open Recent...', top=False)
        self.menuImportPDF = menuElement(
            u'ImportPDF', 'Import Book from PDF', top=False)
        self.menuReimportPDF = menuElement(
            u'ReimportPDF', 'Reimport Book from PDF', top=False)
        self.menuImportDirectory = menuElement(
            u'ScanDir', 'Scan and import books from directory', top=False)
        self.menuToolScript = menuElement(
            u'Scripts', 'Run Script...', top=False)
        self.menuToolRefresh = menuElement(
            u'ToolRefresh', 'Refresh script list', top=False)

    def addActions(self, MainWindow) -> None:
        # Add top level menus to the menubar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuGo.menuAction())
        self.menubar.addAction( self.menuBookmark.menuAction() )
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        # attach actions to top level menus
        self.addFileActions()
        self.addEditActions()
        self.addViewActions()
        self.addGoActions()
        self.addBookmarkActions()
        self.addToolActions()
        self.addHelpActions()

    def addFileActions(self) -> None:
        self.menuFile.addAction(self.action_file_open)
        self.action_file_open_recent = self.menuFile.addMenu(
            self.menuOpenRecent)
        self.menuFile.addAction(self.action_file_reopen)
        self.menuFile.addAction(self.action_file_close)
        self.menuFile.addAction(self.action_file_delete)
        self.menuFile.addSeparator()   # -------------------
        # import submenu...
        self.menuImport = self.menuFile.addMenu("Import")
        self.menuImport.setTitle('Import music')
        self.menuImport.addAction(self.action_file_select_import)
        self.menuImport.addAction(self.action_file_import_PDF)
        self.menuImport.addAction(self.action_file_reimport_PDF)
        self.menuImport.addAction(self.action_file_import_dir)
        self.menuImport.addSeparator()   # -------------------
        self.menuImport.addAction( self.action_file_import_images )
        self.menuImport.addAction( self.action_file_import_images_dir )

        # library submenu
        self.menuLibrary = self.menuFile.addMenu("Library")
        self.menuLibrary.setTitle(u'Library')
        self.menuLibrary.addAction( self.action_file_library_consolidate)
        self.menuLibrary.addAction( self.action_file_library_check )

        self.menuFile.addSeparator()   # -------------------
        self.menuFile.addAction(self.action_edit_preferences)

    def addEditActions(self) -> None:
        self.menuEdit.addAction(self.action_edit_page)
        self.menuEdit.addSeparator()   # -------------------
        self.menuEdit.addAction(self.action_edit_properties)
        self.menuEdit.addAction(self.action_edit_note_book)
        self.menuEdit.addAction(self.action_edit_note_page)
        self.menuEdit.addSeparator()   # -------------------

    def addViewActions(self) -> None:
        self.menuView.addAction(self.action_refresh)
        self.menuView.addSeparator()   # -------------------
        self.menuView.addAction(self.actionOne_Page)
        self.menuView.addAction(self.actionTwo_Pages)
        self.menuView.addAction(self.actionThree_Pages)
        self.menuView.addAction(self.actionTwo_Pages_Stacked)
        self.menuView.addAction(self.actionThree_Pages_Stacked)
        self.menuView.addSeparator()   # -------------------
        self.menuView.addAction(self.actionAspectRatio)
        self.menuView.addAction(self.actionViewStatus)
        self.menuView.addAction(self.actionSmartPages)
        self.menuView.addSeparator()   # -------------------

    def addGoActions(self) -> None:
        self.menuGo.addAction(self.actionUp)
        self.menuGo.addAction(self.actionDown)
        self.menuGo.addSeparator()   # -------------------
        self.menuGo.addAction(self.actionFirstPage)
        self.menuGo.addAction(self.actionLastPage)
        self.menuGo.addAction(self.actionGo_to_Page)

    def addBookmarkActions(self)->None:
        self.menuBookmark.addAction(self.action_bookmark_add)
        self.menuBookmark.addAction(self.action_bookmark_current)
        self.menuBookmark.addAction(self.action_bookmark_show_all)
        self.menuBookmark.addAction(self.action_bookmark_delete_all)
        self.menuBookmark.addSeparator()   # -------------------
        self.menuBookmark.addAction(self.action_bookmark_previous)
        self.menuBookmark.addAction(self.action_bookmark_next)

    def addToolActions(self) -> None:
        self.menuTools.addAction(self.action_tool_check)
        self.actionToolScript = self.menuTools.addMenu(self.menuToolScript)
        self.menuTools.addAction(self.action_tool_refresh)

    def addHelpActions(self) -> None:
        self.menuHelp.addAction(self.action_help_about)
        self.menuHelp.addAction(self.action_help)

    def setNavigationShortcuts(self, overrides: dict = None):
        """
            Set the navigation shortcut. You can pass a dictionary of values
            in and those setting will override the defaults. Th dictionary
            can contain other entries - that won't affect the operation.
        """
        navigationShortcut = {
            DbKeys.SETTING_PAGE_PREVIOUS:      u'Up',
            DbKeys.SETTING_BOOKMARK_PREVIOUS:   u'Alt+Up',
            DbKeys.SETTING_PAGE_NEXT:           u'Down',
            DbKeys.SETTING_BOOKMARK_NEXT:       u'Alt+Down',
            DbKeys.SETTING_FIRST_PAGE_SHOWN:    u"Alt+Ctrl+Left",
            DbKeys.SETTING_LAST_PAGE_SHOWN:     u"Alt+Ctrl+Right",
        }
        if overrides is not None:
            navigationShortcut.update(overrides)

        def shortcut(name: str, action: QAction):
            action.setShortcut(
                QCoreApplication.translate(
                    "MainWindow", navigationShortcut[name], None)
            )

        shortcut(DbKeys.SETTING_PAGE_PREVIOUS,         self.actionUp)
        shortcut(DbKeys.SETTING_BOOKMARK_PREVIOUS,
                 self.action_bookmark_previous)
        shortcut(DbKeys.SETTING_PAGE_NEXT,             self.actionDown)
        shortcut(DbKeys.SETTING_BOOKMARK_NEXT,
                 self.action_bookmark_next)
        shortcut(DbKeys.SETTING_FIRST_PAGE_SHOWN,      self.actionFirstPage)
        shortcut(DbKeys.SETTING_LAST_PAGE_SHOWN,       self.actionLastPage)

    def setBookmarkShortcuts(self, overrides: dict = None):
        bookmarkShortcut = {
            'markBookmark':    u'Ctrl+D',
            'showBookmark':    u'Shift+Ctrl+D',
            'addBookmark':      u'Alt+B',
        }
        if overrides is not None:
            bookmarkShortcut.update(overrides)

        def shortcut(name, action: QAction):
            action.setShortcut(
                QCoreApplication.translate(
                    "MainWindow", bookmarkShortcut[name], None)
            )

        # Shortcuts
        shortcut('showBookmark',        self.action_bookmark_show_all)
        shortcut('markBookmark',        self.action_bookmark_current)
        shortcut('addBookmark',         self.action_bookmark_add)

    def addPageWidgets(self, MainWindow):
        self.pageWidget = PageWidget(MainWindow)
        self.pager = self.pageWidget.getMainPageWidget()
        MainWindow.setCentralWidget(self.pager)

    def statusText(self, statusTxt=""):
        self.statusbar.showMessage(statusTxt)
