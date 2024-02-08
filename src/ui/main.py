"""
User Interface : contains all of the main elements
            for creating and controlling the main window

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtCore import (QCoreApplication, QRect, QSize)
from PySide6.QtGui import (QAction, Qt, QKeySequence)
from PySide6.QtWidgets import (
    QLabel, QMenu, QPushButton,
    QMenuBar, QSizePolicy, QStatusBar,
    QSlider, QMainWindow, QStackedWidget)

from qdb.keys import DbKeys
from ui.pdfwidget import PdfWidget
from ui.pxwidget import PxWidget

class UiMain():
    """ Create and iniitalse all of the window elements """
    PAGER_PNG = 'png'
    PAGER_PDF = 'pdf'

    STACK_PAGER_CLASS = 'pager'
    STACK_DISPLAY_WIDGET = 'display'

    def __init__(self):
        """Create all the variables used and call setup routines
        """
        self._current_stack = None
        self._stacks_widget = None
        self.action_aspect_ratio = None
        self.action_bookmark_add = None
        self.action_bookmark_current = None
        self.action_bookmark_delete_all = None
        self.action_bookmark_next = None
        self.action_bookmark_previous = None
        self.action_bookmark_show_all = None
        self.action_down = None
        self.action_edit_note_book = None
        self.action_edit_note_page = None
        self.action_edit_page = None
        self.action_edit_preferences = None
        self.action_edit_properties = None
        self.action_file_close = None
        self.action_file_delete = None
        self.action_file_import = None
        self.action_file_import_dir = None
        self.action_file_import_document = None
        self.action_file_import_document_dir = None
        self.action_file_import_images = None
        self.action_file_import_images_dir = None
        self.action_file_import_pdf = None
        self.action_file_library = None
        self.action_file_library_check = None
        self.action_file_library_consolidate = None
        self.action_file_library_stats = None
        self.action_file_open = None
        self.action_file_open_recent = None
        self.action_file_reimport = None
        self.action_file_reopen = None
        self.action_file_select_import = None
        self.action_first_page = None
        self.action_goto_page = None
        self.action_help = None
        self.action_help_about = None
        self.action_last_page = None
        self.action_one_page = None
        self.action_refresh = None
        self.action_smart_pages = None
        self.action_three_pages = None
        self.action_three_pages_stacked = None
        self.action_tool_check = None
        self.action_tool_refresh = None
        self.action_toolscript = None
        self.action_toolscript = None
        self.action_two_pages = None
        self.action_two_pages_stacked = None
        self.action_up = None
        self.action_view_status = None
        self.btn_bookmark = None
        self.label_book_note = None
        self.label_page_absolute = None
        self.label_page_note = None
        self.label_page_relative = None
        self.label_slider = None
        self.main_window = None
        self.menu_bar = None
        self.menu_bookmark = None
        self.menu_edit = None
        self.menu_file = None
        self.menu_go = None
        self.menu_help = None
        self.menu_import = None
        self.menu_import_directory = None
        self.menu_import_pdf = None
        self.menu_library = None
        self.menu_open_recent = None
        self.menu_reimport_pdf = None
        self.menu_tool_refresh = None
        self.menu_tools = None
        self.menu_toolscript = None
        self.menu_view = None
        self.pager = None
        self.set_add_bookmark = None
        self.set_import_pdf = None
        self.set_import_script = None
        self.set_mark_bookmark = None
        self.set_reimport_pdf = None
        self.set_show_bookmarks = None
        self.slider_page_position = None
        self.stacks = None
        self.statusbar = None

        # White square: "\U00002B1C"
        self._blank_note_indicator = "   "
        self._double_bar = "\U00002016"
        self._bookmark = "\U0001f516"

    def setup_ui(self, window:QMainWindow):
        """Setup ui window

        Args:
            window (_type_): QWindow to save
        """
        self._setup_main_window(window)
        self._setup_ui_actions(window)
        self._setup_menus(window)
        self._add_actions()
        self._add_page_widgets()
        self._add_status_bar(window)
        self.set_navigation_shortcuts()
        self.set_bookmark_shortcuts()

    def _setup_main_window(self, main_window):
        """Initialise main QT Window

        This sets window default size, size policy, colours, etc.
        All aspects of the main window should be set here

        Args:
            main_window (QWindow): QT Window object
        """
        if not main_window.objectName():
            main_window.setObjectName("main_window")
        main_window.resize(800, 600)
        self.main_window = main_window
        size_policy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            main_window.size_policy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)
        main_window.setMinimumSize(QSize(500, 500))
        main_window.setWindowTitle(QCoreApplication.translate(
            "main_window", "main_window", None))
        p = main_window.palette()
        p.setColor(main_window.backgroundRole(), Qt.black)
        main_window.setPalette(p)

        main_window.setAutoFillBackground(True)

    def _setup_ui_actions(self, main_window:QMainWindow):
        def action(name, title: str = None, shortcut: str = None, checkable=False, checked=False):
            s = QAction(main_window)
            s.setObjectName('action_' + name)
            s.setCheckable(checkable)
            if checkable:
                s.setChecked(checked)
            if title is None:
                title = name
            s.setText(
                QCoreApplication.translate("main_window", title, None))
            if shortcut is not None:
                if isinstance(shortcut, str):
                    s.setShortcut(
                        QCoreApplication.translate("main_window", shortcut, None))
                else:
                    s.setShortcut(shortcut)
            return s

        # FILE action_s
        self.action_file_open = action(
            'Open',   title='Open...',  shortcut=QKeySequence.Open)
        self.action_file_open_recent = action('Recent')
        self.action_file_reopen = action('Reopen', title="Reopen")
        self.action_file_close = action(
            "Close",                    shortcut=QKeySequence.Close)
        self.action_file_delete = action(
            'Delete', title='Delete...', shortcut=QKeySequence.DeleteEndOfWord)
        self.action_file_import = action('Import')
        self.action_file_library = action('Library')

        # file -> import action_s
        self.action_file_import_document = action(
            'ImportDocument', title='Import PDF Document...')
        self.action_file_import_document_dir = action(
            'ImportDocumentDir', title='Import Directory of PDF Documents...')
        # -----
        self.action_file_select_import = action(
            'SelectImport', title='Select PDF to PNG Conversion Script ...')
        self.action_file_import_pdf = action(
            'ImportPDF',    title='Convert PDF to PNG and Import...')
        self.action_file_import_dir = action(
            'ImportDir',    title="Convert Directory of PDFs to PNG and Import...")
        self.action_file_reimport = action(
            'ReimportPDF', title='Reimport PDF (Document or PNG)...')

        self.action_file_import_images = action(
            'ImportImages', title='Import directory of PNG Images...' )
        self.action_file_import_images_dir = action(
            'ImportImagesDir',
            title='Import directory holding multiple directories of PNG images...' )

        # file -> Library action_s
        self.action_file_library_consolidate = action(
            'LibraryConsolidate', title='Consolidate library entries...' )
        self.action_file_library_check = action(
            'LibraryCheck', title='Check library for consistency...' )
        self.action_file_library_stats = action(
            'LibraryStats', title='Show stats for library' )


        # EDIT action_s
        self.action_edit_page = action(
            'PageEdit', title='Edit Page #', shortcut='Ctrl+E')
        self.action_edit_properties = action("Properties", shortcut='Ctrl+I')
        self.action_edit_note_book = action("BookNote", title="Note for Book")
        self.action_edit_note_page = action('PageNote', title='Note for Page')


        # VIEW action_s
        self.action_refresh = action(
            'Refresh',  title='Refresh',                 shortcut=QKeySequence.Refresh)

        self.action_one_page = action(
            "One_page",
            title='One Page',
            shortcut='Ctrl+1', checkable=True,)
        self.action_two_pages = action(
            "Two_pages",
            title='Two Pages side-by-side',
            shortcut='Ctrl+2', checkable=True,)
        self.action_three_pages = action(
            "Three_pages",
            title='Three Pages side-by-side',
            shortcut='Ctrl+3', checkable=True,)
        self.action_two_pages_stacked = action(
            "Two_stack",  title='Two Pages Stacked',
            shortcut='Ctrl+4', checkable=True,)
        self.action_three_pages_stacked = action(
            "Three_Stack",
            title='Three Pages Stacked',
            shortcut='Ctrl+5', checkable=True,)
        self.action_aspect_ratio = action(
            "AspectRatio",
            title='Keep Aspect ratio',
            shortcut="Ctrl+A", checkable=True,)
        self.action_smart_pages = action(
            "_smart_pages",
            title='Smart Page Turn',
            shortcut=QKeySequence.AddTab, checkable=True,)
        self.action_view_status = action(
            'ViewStatus',
            title='View Status',
            shortcut='Ctrl+S', checkable=True, checked=True)

        # GO action_s (Note: shortcuts are sent in 'setNavigationShortcuts' )
        self.action_up = action("Up",        title='Previous Page')
        self.action_down = action("Down",      title='Next Page')
        self.action_first_page = action("_first_page", title='First Page')
        self.action_last_page = action("last_page", title='Last Page')
        self.action_goto_page = action("goto_page", title='Go To Page...')

        # BOOKMARK action_s
        self.action_bookmark_previous = action(
            "PreviousBookmark",   title='Previous Bookmark')
        self.action_bookmark_next = action(
            "NextBookmark",       title='Next Bookmark')
        self.action_bookmark_delete_all = action(
            'DeleteAllBookmarks', title='Delete All Bookmarks')
        self.action_bookmark_show_all = action(
            "ShowBookmarks", title='Show Bookmarks...')
        self.action_bookmark_current = action(
            "BookmarkCurrentPage", title='Bookmark current page')
        self.action_bookmark_add = action(
            "Add_Bookmark",        title='Add Bookmark...')

        # TOOL action_s (Bookmark controls are set in 'setBookmarkShortcuts')
        self.action_tool_check = action(
            "CheckIncomplete",    title='Check for incomplete entries ...')
        self.action_tool_refresh = action(
            "RefreshTool",        title='Refresh script list')
        self.action_toolscript = action('Script')

        # HELP action_s
        self.action_help = action("Help")

        # NOTE: Following tend to be 'special' as they an float to other places
        self.action_edit_preferences = action('Preferences')
        self.action_edit_preferences.setMenuRole(QAction.PreferencesRole)

        self.action_help_about = action("action_help_about")
        self.action_help_about.setMenuRole(QAction.AboutRole)

    def _setup_menus(self, main_window) -> None:
        """
        Create all of the menus
        """
        def menu_element(name: str, title: str = None, top: bool = True) -> QMenu:
            if top:
                s = QMenu(self.menu_bar)
            else:
                s = QMenu()
            s.setObjectName('menu' + name)
            if title is None:
                title = name
            s.set_title(
                QCoreApplication.translate("main_window", name, None))
            return s

        self.menu_bar = QMenuBar(main_window)
        self.menu_bar.setObjectName("menubar")
        self.menu_bar.setGeometry(QRect(0, 0, 800, 24))

        self.menu_file = menu_element('File')
        self.menu_edit = menu_element('Edit')
        self.menu_view = menu_element('View')
        self.menu_go = menu_element('Go')
        self.menu_bookmark = menu_element( 'Bookmark')
        self.menu_tools = menu_element('Tools')
        self.menu_help = menu_element('Help')

        self.menu_open_recent = menu_element(
            'OpenRecent', 'Open Recent...', top=False)
        self.menu_import_pdf = menu_element(
            'ImportPDF', 'Import Book from PDF', top=False)
        self.menu_reimport_pdf = menu_element(
            'ReimportPDF', 'Reimport Book from PDF', top=False)
        self.menu_import_directory = menu_element(
            'ScanDir', 'Scan and import books from directory', top=False)
        self.menu_toolscript = menu_element(
            'Scripts', 'Run Script...', top=False)
        self.menu_tool_refresh = menu_element(
            'ToolRefresh', 'Refresh script list', top=False)

    def get_windows(self):
        """Get the window object

        Returns:
            QWindow: QT window
        """
        return self.main_window

    def _add_actions(self) -> None:
        # Add top level menus to the menubar
        self.menu_bar.addAction(self.menu_file.menuAction())
        self.menu_bar.addAction(self.menu_edit.menuAction())
        self.menu_bar.addAction(self.menu_view.menuAction())
        self.menu_bar.addAction(self.menu_go.menuAction())
        self.menu_bar.addAction(self.menu_bookmark.menuAction() )
        self.menu_bar.addAction(self.menu_tools.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())

        # attach action_s to top level menus
        self._add_file_actions()
        self._add_edit_actions()
        self._add_view_actions()
        self._add_go_actions()
        self._add_bookmark_actions()
        self._add_tool_actions()
        self._add_help_actions()

    def _add_file_actions(self) -> None:
        self.menu_file.addAction(self.action_file_open)
        self.action_file_open_recent = self.menu_file.addMenu(
            self.menu_open_recent)
        self.menu_file.addAction(self.action_file_reopen)
        self.menu_file.addAction(self.action_file_close)
        self.menu_file.addAction(self.action_file_delete)
        self.menu_file.addSeparator()   # -------------------
        # import submenu...
        self.menu_import = self.menu_file.addMenu("Import")
        self.menu_import.set_title('Import music')
        self.menu_import.addAction( self.action_file_import_document )
        self.menu_import.addAction( self.action_file_import_document_dir )
        self.menu_import.addSeparator()   # -------------------
        self.menu_import.addAction(self.action_file_select_import)
        self.menu_import.addAction(self.action_file_import_pdf)
        self.menu_import.addAction(self.action_file_import_dir)
        self.menu_import.addSeparator()   # -------------------
        self.menu_import.addAction(self.action_file_reimport)
        self.menu_import.addSeparator()   # -------------------
        self.menu_import.addAction( self.action_file_import_images )
        self.menu_import.addAction( self.action_file_import_images_dir )

        # library submenu
        self.menu_library = self.menu_file.addMenu("Library")
        self.menu_library.set_title('Library')
        self.menu_library.addAction( self.action_file_library_consolidate)
        self.menu_library.addAction( self.action_file_library_check )
        self.menu_library.addAction( self.action_file_library_stats )

        self.menu_file.addSeparator()   # -------------------
        self.menu_file.addAction(self.action_edit_preferences)

    def _add_edit_actions(self) -> None:
        self.menu_edit.addAction(self.action_edit_page)
        self.menu_edit.addSeparator()   # -------------------
        self.menu_edit.addAction(self.action_edit_properties)
        self.menu_edit.addAction(self.action_edit_note_book)
        self.menu_edit.addAction(self.action_edit_note_page)
        self.menu_edit.addSeparator()   # -------------------

    def _add_view_actions(self) -> None:
        self.menu_view.addAction(self.action_refresh)
        self.menu_view.addSeparator()   # -------------------
        self.menu_view.addAction(self.action_one_page)
        self.menu_view.addAction(self.action_two_pages)
        self.menu_view.addAction(self.action_three_pages)
        self.menu_view.addAction(self.action_two_pages_stacked)
        self.menu_view.addAction(self.action_three_pages_stacked)
        self.menu_view.addSeparator()   # -------------------
        self.menu_view.addAction(self.action_aspect_ratio)
        self.menu_view.addAction(self.action_view_status)
        self.menu_view.addAction(self.action_smart_pages)
        self.menu_view.addSeparator()   # -------------------

    def _add_go_actions(self) -> None:
        self.menu_go.addAction(self.action_up)
        self.menu_go.addAction(self.action_down)
        self.menu_go.addSeparator()   # -------------------
        self.menu_go.addAction(self.action_first_page)
        self.menu_go.addAction(self.action_last_page)
        self.menu_go.addAction(self.action_goto_page)

    def _add_bookmark_actions(self)->None:
        self.menu_bookmark.addAction(self.action_bookmark_add)
        self.menu_bookmark.addAction(self.action_bookmark_current)
        self.menu_bookmark.addAction(self.action_bookmark_show_all)
        self.menu_bookmark.addAction(self.action_bookmark_delete_all)
        self.menu_bookmark.addSeparator()   # -------------------
        self.menu_bookmark.addAction(self.action_bookmark_previous)
        self.menu_bookmark.addAction(self.action_bookmark_next)

    def _add_tool_actions(self) -> None:
        self.menu_tools.addAction(self.action_tool_check)
        self.action_toolscript = self.menu_tools.addMenu(self.menu_toolscript)
        self.menu_tools.addAction(self.action_tool_refresh)

    def _add_help_actions(self) -> None:
        self.menu_help.addAction(self.action_help_about)
        self.menu_help.addAction(self.action_help)

    def _add_page_widgets(self):
        """ Add all of the pager widgets here. Call 'show_pager(name) to pick"""
        self._stacks_widget = {}

        self.stacks = QStackedWidget( self.main_window )
        self.stacks.setObjectName( 'pagerStacks')
        self.stacks.setAutoFillBackground(True)

        # pagerWidget is the intface from program to display
        # display_widget is the widget that holds all the pages.

        # PNG Pager
        pager_class = PxWidget( self.main_window )
        display_widget = pager_class.get_pager_widget()
        self._stacks_widget[ DbKeys.VALUE_PNG] = {
            UiMain.STACK_PAGER_CLASS: pager_class,
            UiMain.STACK_DISPLAY_WIDGET : display_widget
        }
        self.stacks.addWidget( display_widget  )

        # PDF pager - Image
        pager_class = PdfWidget( self.main_window )
        pager_class.usepdf = False
        display_widget = pager_class.get_pager_widget()
        self._stacks_widget[ f"{DbKeys.VALUE_PDF}_{'False'}"] = {
            UiMain.STACK_PAGER_CLASS: pager_class,
            UiMain.STACK_DISPLAY_WIDGET : display_widget
        }
        self.stacks.addWidget( display_widget  )

        # PDF pager - PDF
        pager_class = PdfWidget( self.main_window )
        pager_class.usepdf = True
        display_widget = pager_class.get_pager_widget()
        self._stacks_widget[ f"{DbKeys.VALUE_PDF}_{'True'}"] = {
            UiMain.STACK_PAGER_CLASS: pager_class,
            UiMain.STACK_DISPLAY_WIDGET : display_widget
        }
        self.stacks.addWidget( display_widget  )

        self.main_window.setCentralWidget(self.stacks)
        self.show_pager( DbKeys.VALUE_PNG )

    def _add_status_bar(self, main_window):
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")

        self.label_page_relative = QLabel()
        self.label_page_relative.setObjectName('pageRelative')
        self.label_page_relative.setMinimumWidth(80)
        self.label_page_relative.setText("")

        self.label_book_note = QLabel()
        self.label_book_note.setObjectName('bookNote')
        self.label_book_note.setMinimumWidth(30)
        self.set_book_note(True)

        self.label_page_note = QLabel()
        self.label_page_note.setObjectName('pageNote')
        self.label_page_note.setMinimumWidth(30)
        self.set_page_note(True)

        self.label_slider = QLabel()
        self.label_slider.setHidden( True )

        self.slider_page_position = QSlider()
        self.slider_page_position.setObjectName('progressbar')
        self.slider_page_position.setMinimum(1)
        self.slider_page_position.setOrientation(Qt.Horizontal)
        self.slider_page_position.setTracking(True)

        self.label_page_absolute = QLabel()
        self.label_page_absolute.setObjectName('pageAbsolute')

        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setObjectName('bookmark')
        self.btn_bookmark.setToolTip("Current bookmark")
        self.btn_bookmark.setFlat(True)
        self.btn_bookmark.setText(self._bookmark)

        self.statusbar.addWidget(self.label_page_relative)
        self.statusbar.addWidget(self.label_book_note)
        self.statusbar.addWidget(self.label_page_note)
        self.statusbar.addWidget(self.label_slider )
        self.statusbar.addWidget(self.slider_page_position, 100)
        #
        self.statusbar.addWidget(self.label_page_absolute)

        main_window.setStatusBar(self.statusbar)

    def create_triggers(self):
        """ Create trigger connection points """
        self.set_mark_bookmark = self.action_bookmark_current.triggered.connect
        self.set_add_bookmark = self.action_bookmark_add.triggered.connect
        self.set_show_bookmarks = self.action_bookmark_show_all.triggered.connect
        self.set_import_script = self.action_file_select_import.triggered.connect
        self.set_import_pdf = self.action_file_import_pdf.triggered.connect
        self.set_reimport_pdf = self.action_file_reimport.triggered.connect

    def set_book_note(self, flag: bool)->None:
        """ Turn on or off the flag on status bar for note
        This will display a small notebook symbol and border
        in the status bar

        Args:
            flag (bool): True if you want a notebook, false to clear
        """
        if flag:
            self.label_book_note.setText("\U0001F4D3")
            self.label_book_note.setStyleSheet("border: 3px solid gray")
            self.label_book_note.setToolTip("Note set for book.")
        else:
            self.label_book_note.setText(self._blank_note_indicator)
            self.label_book_note.setStyleSheet("border: 2px solid lightgray")
            self.label_book_note.setToolTip("")

    def set_page_note(self, flag: bool, page=""):
        """Display a small icon of a page with page number
        Call to set or clear the page note indicator in the
        status bar

        Args:
            flag (bool): True if you want a page ote, false to clear
            page (str, optional): page number text. Defaults to "".
                if "" then page text will be cleared.
        """
        if flag:
            self.label_page_note.setText("\U0001F4DD")
            self.label_page_note.setStyleSheet("border: 3px solid gray")
            if page:
                self.label_page_note.setToolTip(
                    f"Note set for page {page}")
            else:
                self.label_page_note.setToolTip("")
        else:
            self.label_page_note.setText(self._blank_note_indicator)
            self.label_page_note.setStyleSheet("border: 2px solid lightgray")
            self.label_page_note.setToolTip("")

    def set_absolute_page(self, absolute: int, total: int, offset_page: int = 1) -> None:
        """ Set tool tip and status bar page number """
        self.label_page_absolute.setText(
            f"{self._double_bar} {absolute:>4d} / {total:<4d} ")
        tt = f"Absolute page / Total pages / Numbering starts on {offset_page}\n"
        self.label_page_absolute.setToolTip(tt)
        self.label_page_absolute.setStyleSheet("text-align: center;")


    def set_navigation_shortcuts(self, overrides: dict = None):
        """
            Set the navigation shortcut. You can pass a dictionary of values
            in and those setting will override the defaults. Th dictionary
            can contain other entries - that won't affect the operation.
        """
        _nav_shortcuts = {
            DbKeys.SETTING_PAGE_PREVIOUS:       'Up',
            DbKeys.SETTING_BOOKMARK_PREVIOUS:   'Alt+Up',
            DbKeys.SETTING_PAGE_NEXT:           'Down',
            DbKeys.SETTING_BOOKMARK_NEXT:       'Alt+Down',
            DbKeys.SETTING_FIRST_PAGE_SHOWN:    "Alt+Ctrl+Left",
            DbKeys.SETTING_LAST_PAGE_SHOWN:     "Alt+Ctrl+Right",
        }
        if overrides is not None:
            _nav_shortcuts.update(overrides)

        def shortcut(name: str, action_: QAction):
            action_.setShortcut(
                QCoreApplication.translate(
                    "main_window", _nav_shortcuts[name], None)
            )

        shortcut(DbKeys.SETTING_PAGE_PREVIOUS,         self.action_up)
        shortcut(DbKeys.SETTING_BOOKMARK_PREVIOUS,
                 self.action_bookmark_previous)
        shortcut(DbKeys.SETTING_PAGE_NEXT,             self.action_down)
        shortcut(DbKeys.SETTING_BOOKMARK_NEXT,
                 self.action_bookmark_next)
        shortcut(DbKeys.SETTING_FIRST_PAGE_SHOWN,      self.action_first_page)
        shortcut(DbKeys.SETTING_LAST_PAGE_SHOWN,       self.action_last_page)

    def set_bookmark_shortcuts(self, overrides: dict = None):
        """ Set the shortcuts for bookmark navigation """
        bmk_shortcut = {
            'markBookmark':    'Ctrl+D',
            'showBookmark':    'Shift+Ctrl+D',
            'addBookmark':      'Alt+B',
        }
        if overrides is not None:
            bmk_shortcut.update(overrides)

        def shortcut(name, action_: QAction):
            action_.setShortcut(
                QCoreApplication.translate(
                    "main_window", bmk_shortcut[name], None)
            )

        # Shortcuts
        shortcut('showBookmark',        self.action_bookmark_show_all)
        shortcut('markBookmark',        self.action_bookmark_current)
        shortcut('addBookmark',         self.action_bookmark_add)

    def show_pager( self , name:str , pdfmode:bool=True)->object:
        """ Select which pager in the stack we are using """
        name = f"{name}" if name != DbKeys.VALUE_PDF else f"{DbKeys.VALUE_PDF}_{str(pdfmode)}"
        if name in self._stacks_widget :
            self._current_stack = name
            self.pager = self._stacks_widget[ name ][ UiMain.STACK_PAGER_CLASS]
            self.stacks.setCurrentWidget(
                self._stacks_widget[ name ][ UiMain.STACK_DISPLAY_WIDGET] )
            self._stacks_widget[ name ][ UiMain.STACK_DISPLAY_WIDGET ].show()
        return self.pager

    def page_widget(self)->PdfWidget|PxWidget:
        """ Return the pager widget """
        return self.pager

    def set_status_text(self, status_txt=""):
        """Set the status text in the status bar

        Args:
            status_txt (str, optional): Text to display. Defaults to "".
        """
        self.statusbar.showMessage(status_txt)
