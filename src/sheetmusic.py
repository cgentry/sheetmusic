"""
    SheetMusic is a program to display music on a monitor. It uses
    PDFs (normally) or PNGs and flips pages. A simple program in Python and QT


 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import gc
import logging
import os
import platform
import sys
from genericpath import isfile

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow,  QMessageBox, QDialog, QFileDialog
from PySide6.QtGui import QPixmap, QAction, QPixmapCache

from constants import ProgramConstants
from qdb.dbconn import DbConn
from qdb.dbnote import DbNote
from qdb.dbsystem import DbSystem
from qdb.keys import DbKeys
from qdb.log import DbLog, Trace
from qdb.setup import Setup

from qdb.fields.book import BookField
from qdb.fields.bookmark import BookmarkField
from qdb.fields.booksetting import BookSettingField
from qdb.fields.bookproperty import BookPropertyField
from qdb.fields.note import NoteField
from qdil.book import DilBook
from qdil.bookmark import DilBookmark
from qdil.preferences import DilPreferences, SystemPreferences

from ui.about import UiAbout
from ui.addbook import UiAddBook
from ui.bookmark import UiBookmark, UiBookmarkEdit, UiBookmarkAdd
from ui.file import Openfile, Deletefile, Reimportfile
from ui.help import UiHelp
from ui.library import UiLibraryConsolidate, UiLibraryCheck, UiLibraryStats
from ui.main import UiMain
from ui.note import UiNote
from ui.page import PageNumber
from ui.preferences import UiPreferences
from ui.properties import UiProperties
from ui.runscript import RunSilentRunDeep,UiRunSimpleNote, UiRunScript

from util.convert import to_bool, decode, encode
from util.toolconvert import (ImportSettings, UiImportPdfDirectory,
                              UiImportSetting, UiConvertFilenames,
                              UiConvertPDFDocumentDirectory,
                              UiImportPDFDocuments)
from util.toollist import GenerateToolList


class SheetMusic(QMainWindow):
    """SheetMusic main program

    Args:
        QMainWindow (QMainWindow): Pyside6 Main Window

    """
    MAX_PAGES = 3
    RESIZE_TIMER = 100

    def __init__(self):
        super().__init__()

        self.direction = None
        self._qtimer_wheel = None
        self._notelist = None

        self._load_ui()
        self.logger = DbLog('main_window')
        self.logger.debug('Program starting')
        self.dlbook = DilBook()
        self.system = DbSystem()
        self.bookmark = DilBookmark()
        self.import_dir = self.dilpref.get_value(DbKeys.SETTING_LAST_IMPORT_DIR)
        tl = GenerateToolList()
        self.toollist = tl.list()

        del tl

        self._perform_resize = False
        self._qtimer = QTimer()
        self._qtimer.timeout.connect(self._set_page_size)
        self._qtimer.setSingleShot(True)

    def _load_ui(self) -> None:
        """ Set the data interface preferences, main UI, initialise the main UI"""
        self.dilpref = DilPreferences()
        self.ui = UiMain()
        self.ui.setup_ui(self)

    def _page_list(self, start_page: int, len_list: int) -> list:
        """creates a list, MAX_PAGES long, of the pages.
        The first entry will always be the one requests.

        Args:
            start_page (int): which page to start with
            len_list (_type_): How many entries to return

        Returns:
            list: List of pages from start to a len or max
        """
        plist = [0]*self.MAX_PAGES
        start_page = max(start_page, 1)
        totalpages = self.dlbook.count()
        for i in range(0, len_list):
            if start_page+i > totalpages:
                break
            plist[i] = start_page+i
        return plist

    def _load_pages(self) -> bool:
        """ Load all pages into the book at once. This loads the MAX_PAGES every time.

            This attempts to optimise page loads and display by looking at the number of
            pages we load.
        """
        if self.dlbook.is_open():
            page = self.dlbook.pagenumber
            # work some 'magic' Show page-n...page IF page is last page.
            total_pages = self.dlbook.count()
            show_pages = self.ui.pager.number_pages()
            if page == total_pages and show_pages and show_pages > 1:
                plist = self._page_list(page-show_pages+1, self.MAX_PAGES)
                self._load_page_widget_list(plist)
            else:
                self._load_page_widget_list(
                    self._page_list(page, self.MAX_PAGES))
        return self.dlbook.is_open()

    def _reload_pages(self) -> bool:
        if self.dlbook.is_open():
            self._load_page_widget_list(self.ui.pager.page_numbers())
        return self.dlbook.is_open()

    def _load_page_widget_list(self, plist: list):
        if len(plist) < self.MAX_PAGES:
            plist.extend([0] * (self.MAX_PAGES - len(plist)))
        return self._load_page_widget(plist[0], plist[1], plist[2])

    def _load_page_widget(self, pg1: int, pg2: int, pg3: int):
        self.logger.debug(Trace.callstr())
        page1 = self.dlbook.page_filepath(pg1)
        page2 = self.dlbook.page_filepath(pg2)
        page3 = self.dlbook.page_filepath(pg3)
        self.logger.debug(f"Pages: {pg1}, {pg2}, {pg3}")
        self.ui.page_widget().resize(self.ui.stacks.size())
        self.ui.pager.load_pages(page1, pg1, page2, pg2, page3, pg3)
        self.dlbook.pagenumber = pg1
        self.update_status_bar()

    def _update_pages_shown(self, absolute_page_number: int = None) -> None:
        """ Update status bar with page numbers """
        self.ui.set_absolute_page(
            absolute_page_number, self.dlbook.count(), self.dlbook.relative_offset)
        lbl = 'Page' if self.dlbook.is_page_relative(
            absolute_page_number) else "Book"
        self.ui.label_page_relative.setText(
            f"{lbl}:{self.dlbook.page_to_relative(absolute_page_number):4d}")

    def _update_menu_bmk_nav(self, bookmark=None):
        has_bookmarks = self.bookmark.count() > 0
        self.ui.action_bookmark_previous.setEnabled(has_bookmarks)
        self.ui.action_bookmark_next.setEnabled(has_bookmarks)
        self.ui.action_bookmark_show_all.setEnabled(has_bookmarks)
        self.ui.action_bookmark_delete_all.setEnabled(has_bookmarks)

        if bookmark is not None:
            self.ui.action_bookmark_previous.setDisabled(
                self.bookmark.is_first(bookmark))
            self.ui.action_bookmark_next.setDisabled(
                self.bookmark.is_last(bookmark))

    def _update_note_indicator(self, page_number: int):
        nlist = self.get_note_list(self.dlbook.get_id())
        if len(nlist):
            self.ui.set_book_note((0 in nlist))
            self.ui.set_page_note((page_number in nlist), page_number)
        else:
            self.ui.set_book_note(False)
            self.ui.set_page_note(False)

    def update_status_bar(self) -> None:
        """ Update status with page numbers, slider position and note indicators """
        absolute_page_number = self.dlbook.pagenumber

        self.ui.slider_page_position.setMaximum(self.dlbook.count())
        self.ui.slider_page_position.set_value(absolute_page_number)

        self._update_pages_shown(absolute_page_number)
        self._update_note_indicator(absolute_page_number)

    def restore_window_from_settings(self) -> None:
        """ Pull in settings from preferences and restore """
        self.dilpref.restoremain_window(self.ui.get_windows())
        self.dilpref.restore_shortcuts(self.ui)
        self._action_view_status_bar(decode(
            self.dilpref.get_value( DbKeys.SETTING_WIN_STATUS_ENABLED),
            code=DbKeys.ENCODE_BOOL,default=True))

    def get_note_list(self, book_id: int, refresh=False) -> dict:
        """Get list of notes for a book

        Args:
            book_id (int): book id for current book
            refresh (bool, optional): _description_. Defaults to False.

        Returns:
            dict: dictionary [page:int][note:str]
        """
        if book_id is not None and (self._notelist is None or refresh):
            self._notelist = {}
            dbnote = DbNote()
            returnlist = dbnote.get_all(book_id)
            for note in returnlist:
                self._notelist[note[NoteField.PAGE]] = note
        return self._notelist

    def open_book(self, new_book: str, page=None) -> None:
        """Close current book and open new book to requested page

        Args:
            new_book (str): Name of new book to open
            page (_type_, optional): _description_. Defaults to None.
        """
        self.close_book()
        self.logger.debug(f"BEGIN '{new_book}'")
        self.logger.debug(Trace.callstr())
        q_rtn = QMessageBox.Retry
        while q_rtn == QMessageBox.Retry:
            q_rtn = self.dlbook.open(new_book, page)

        if q_rtn == QMessageBox.AcceptRole:
            book_layout = self.dlbook.get_property(
                BookPropertyField.LAYOUT, system=True)
            smart_page_turn = to_bool(self.dlbook.get_property(
                DbKeys.SETTING_SMART_PAGES, system=True))
            aspect_ratio = self.dlbook.keep_aspect_ratio
            self.dlbook.pagenumber = self.dlbook.last_pageread

            self.ui.show_pager(self.dlbook.get_filetype(),
                               self.dlbook.renderbookpdf())
            self.ui.page_widget().set_display(book_layout)
            self.ui.page_widget().set_smartpage(smart_page_turn)
            self.ui.page_widget().keep_aspect_ratio = aspect_ratio
            self.ui.page_widget().dimensions = \
                self.dlbook.get_property(BookSettingField.KEY_DIMENSIONS)
            self._load_pages()

            # Update page and menu displays
            self.set_title()
            self._set_menu_book_options(True)
            self._set_menu_page_options(book_layout)
            self.ui.action_aspect_ratio.setChecked(aspect_ratio)
            self.ui.action_smart_pages.setChecked(smart_page_turn)

            self.bookmark.open(new_book)
            self._update_menu_bmk_nav(self.bookmark.lookup_bookmark(page))

            self.ui.page_widget().show()
            self.update_status_bar()
        else:
            self.logger.warning(f"Couldn't open {new_book}")
            if q_rtn == QMessageBox.DestructiveRole:
                self.dlbook.del_book(new_book)
            self.open_lastbook(noretry=new_book)
        self.logger.debug(f'END "{new_book}"')

    def close_book(self) -> None:
        """ Close the book, save a pointer to it, and hide the menu items. """
        self._notelist = None
        if self.dlbook.is_open():
            self.dilpref.set_value(
                key=DbKeys.SETTING_LAST_BOOK_NAME,
                value=encode(
                        value=self.dlbook.title,
                        code=DbKeys.ENCODE_STR )
            )
            self.dlbook.close()
            self.ui.pager.clear()
            QPixmapCache().clear()
        self._set_menu_book_options(False)
        self.ui.main_window.hide()
        gc.collect()

    def setup_wheel_timer(self) -> None:
        """ Setup an interval timer """
        self._qtimer_wheel = QTimer(self)
        self._qtimer_wheel.setInterval(1000)  # 500 msec == .5 seconds
        self._qtimer_wheel.setSingleShot(True)
        self.direction = None

    def event_filter(self, qobject: QObject, qevent: QEvent) -> bool:
        """ Handle events for page flipping """
        if qevent.type() == QEvent.Gesture:
            qobject.blockSignals(True)
            if qevent.GestureType() == Qt.SwipeGesture:
                if qevent.horizontalDirection() == 'Left':
                    self.page_previous()
                if qevent.horizontalDirection() == 'Right':
                    self.page_forward()
                qobject.blockSignals(False)
                return True
        ###
        # TODO: Need a better way to reduce page flips, otherwise
        # the screen acts erratic.
        ###
        if qevent.type() == QEvent.Wheel:
            qobject.blockSignals(True)
            if not self._qtimer_wheel.isActive():
                # block wheel activies for a time
                # we end up with LOADS of events and it
                # sometimes goes to zero, then back up, then zero
                pnt = qevent.angleDelta()
                x = pnt.x()
                if x == 0:
                    if self.direction is not None:
                        self._qtimer_wheel.start()
                        if self.direction == 'Left':
                            self.page_previous()
                        else:
                            self.page_forward()

                        self.direction = None
                else:
                    if x < 0:
                        self.direction = 'Left'
                    else:
                        self.direction = 'Right'
            qobject.blockSignals(False)
            return True
        # End Wheel

        return False

    def _set_page_size(self):
        self.ui.page_widget().resize(self.ui.stacks.size())
        self._reload_pages()

    def event_resize(self, event):
        """ Set a timer for resizing """
        del event
        if self._qtimer.isActive():
            self._qtimer.stop()
        self._qtimer.start(self.main_window.RESIZE_TIMER)

    def closeEvent(self, event) -> None:
        """ called when the program is closed """
        del event
        self.dilpref.save_mainwindow(self.ui.get_windows())
        self.dilpref.set_value(
            key=DbKeys.SETTING_LAST_IMPORT_DIR,
            replace=True,
            value=encode(DbKeys.ENCODE_STR, self.import_dir)
        )
        self.close_book()
        DbConn.close_db()

    def page_previous(self) -> None:
        """ Move to previous page """
        pg = self.ui.pager.get_lowest_page_shown()-1
        if self.dlbook.is_valid_page(pg):
            is_endpage = pg == 1
            self.ui.pager.previous_page(
                self.dlbook.page_filepath(pg), pg, end=is_endpage)
            self.dlbook.pagenumber = pg
            self.update_status_bar()

    def page_forward(self) -> None:
        """ Move to next page """
        pg = self.ui.pager.get_highest_page_shown()+1
        if self.dlbook.is_valid_page(pg):
            self.dlbook.pagenumber = pg
            number_pages = self.dlbook.count()
            self.ui.pager.next_page(self.dlbook.page_filepath(pg),
                                   pg, end=pg == number_pages)
            self.update_status_bar()

    def goto_page(self, page: int) -> None:
        ''' Set the page number to the page passed and display
            page number must be absolute, not relative.
        '''
        if page:
            self.dlbook.pagenumber = page
            self._load_pages()
            self.update_status_bar()

    def goto_first_bookmark(self) -> None:
        """ Set the page to the first bookmark """
        bmk = self.bookmark.first()
        self.dlbook.pagenumber = bmk[BookmarkField.PAGE]
        self._load_pages()

    def goto_last_bookmark(self) -> None:
        """ Set the page to the last bookmark """
        bmk = self.bookmark.last()
        self.dlbook.pagenumber = bmk[BookmarkField.PAGE]
        self._load_pages()

    def connect_menus(self) -> None:
        """ Connect menus and events to the routines handling the function"""
        # FILE:
        self.ui.menu_file.aboutToShow.connect(self._about_to_show_file_menu)
        self.ui.action_file_open.triggered.connect(self._action_file_open)
        self.ui.menu_open_recent.aboutToShow.connect(
            self._about_to_show_file_recent)
        self.ui.menu_open_recent.triggered.connect(
            self._action_file_open_recent)
        self.ui.action_file_reopen.triggered.connect(self._action_file_reopen)
        self.ui.action_file_close.triggered.connect(self._action_file_close)
        self.ui.action_file_delete.triggered.connect(self._action_file_delete)
        # --------------
        self.ui.action_file_import_document.triggered.connect(
            self._action_file_import_document)
        self.ui.action_file_import_document_dir.triggered.connect(
            self._action_file_import_document_dir)
        # ---------------
        self.ui.action_file_select_import.triggered.connect(
            self._action_file_select_import)
        self.ui.action_file_import_pdf.triggered.connect(
            self._action_file_import_pdf)
        self.ui.action_file_import_dir.triggered.connect(
            self._action_file_import_dir)
        self.ui.action_file_reimport.triggered.connect(
            self._action_file_reimport)
        self.ui.action_file_import_images.triggered.connect(
            self._action_file_import_images)
        self.ui.action_file_import_images_dir.triggered.connect(
            self._action_file_import_images_dir)
        # ------
        self.ui.action_file_library_consolidate.triggered.connect(
            self._action_file_library_consolidate)
        self.ui.action_file_library_check.triggered.connect(
            self._action_file_library_check)
        self.ui.action_file_library_stats.triggered.connect(
            self._action_file_library_stats)

        # EDIT:
        self.ui.menu_edit.aboutToShow.connect(self._about_to_show_edit_menu)
        self.ui.action_edit_page.triggered.connect(self._action_edit_page)
        self.ui.action_edit_properties.triggered.connect(
            self._action_edit_properties)
        self.ui.action_edit_preferences.triggered.connect(
            self._action_edit_preferences)
        self.ui.action_edit_note_book.triggered.connect(
            self._action_edit_note_book)
        self.ui.action_edit_note_page.triggered.connect(
            self._action_edit_note_page)
        self.ui.action_bookmark_delete_all.triggered.connect(
            self._action_bookmark_delete_all)

        # VIEW:
        self.ui.action_refresh.triggered.connect(self._action_refresh)
        # --------------
        self.ui.action_one_page.triggered.connect(self._action_view_one_page)
        self.ui.action_two_pages.triggered.connect(self._action_view_two_side)
        self.ui.action_two_pages_stacked.triggered.connect(
            self._action_view_two_stack)
        self.ui.action_three_pages.triggered.connect(
            self._action_view_three_side)
        self.ui.action_three_pages_stacked.triggered.connect(
            self._action_view_three_stack)
        # --------------
        self.ui.action_aspect_ratio.triggered.connect(
            self._action_view_aspect_ratio)
        self.ui.action_view_status.triggered.connect(
            self._action_view_status_bar)
        self.ui.action_smart_pages.triggered.connect(
            self._action_view_smart_pages)

        # GO:
        self.ui.action_goto_page.triggered.connect(self._action_go_page)
        self.ui.action_first_page.triggered.connect(self._action_go_page_first)
        self.ui.action_last_page.triggered.connect(self._action_go_page_last)
        # --------------
        self.ui.action_up.triggered.connect(self.page_previous)
        self.ui.action_down.triggered.connect(self.page_forward)
        # --------------

        # BOOKMARK
        self.ui.action_bookmark_show_all.triggered.connect(
            self._action_bookmark_show)
        self.ui.action_bookmark_current.triggered.connect(
            self._action_bookmark_current)
        self.ui.action_bookmark_add.triggered.connect(
            self._action_bookmark_add)
        self.ui.action_bookmark_previous.triggered.connect(
            self._action_bookmark_go_previous)
        self.ui.action_bookmark_next.triggered.connect(
            self._action_bookmark_go_next)
        self.ui.btn_bookmark.clicked.connect(self.action_clicked_bookmark)

        # TOOLS

        self.ui.menu_toolscript.aboutToShow.connect(
            self._about_to_show_script_list)
        self.ui.action_tool_check.triggered.connect(self._action_tool_check)
        self.ui.action_tool_refresh.triggered.connect(
            self._action_tool_refresh)
        self.ui.menu_toolscript.triggered.connect(self._action_tool_script)

        # HELP:
        self.ui.action_help_about.triggered.connect(self._action_help_about)
        self.ui.action_help.triggered.connect(self._action_help)

        # INTERNAL
        self.ui.slider_page_position.valueChanged.connect(
            self._action_slider_changed)
        self.ui.slider_page_position.sliderReleased.connect(
            self._action_slider_released)

        # self.ui.action_bookmark.triggered.connect(self.action_goto_bookmark)
        # self.ui.twoPagesSide.installEventFilter( self)

    def _open_lastbook(self, noretry: str = None) -> None:
        if decode(
            self.dilpref.get_value( DbKeys.SETTING_LAST_BOOK_REOPEN),
                code=DbKeys.ENCODE_BOOL, default=True):
            recent = self.dlbook.recent()
            if recent is None or len(recent) == 0:
                self.logger.info('No last book to open')
            else:
                last_book_name = recent[0][BookField.NAME]
                self.logger.debug(
                    f'Recent book "{last_book_name}" noretry: "{noretry}"')
                if noretry != last_book_name:
                    self.open_book(recent[0][BookField.NAME])

    def set_title(self, bookmark: str = None) -> None:
        """ Title is made of the title and bookmark if there is one """
        if bookmark:
            title = f"{ProgramConstants.SYSTEM_NAME}: {self.dlbook.title} - {bookmark}"
        else:
            title = f"{ProgramConstants.SYSTEM_NAME}: {self.dlbook.title}"
        self.ui.main_window.setWindowTitle(title)
        self.ui.main_window.show()

    def _finish_bookmark_navigation(self, bmk: dict) -> None:
        if bmk is not None and BookmarkField.PAGE in bmk and bmk[BookmarkField.PAGE] is not None:
            self.ui.action_bookmark_previous.setDisabled(
                self.bookmark.is_first(bmk))
            self.ui.action_bookmark_next.setDisabled(self.bookmark.is_last(bmk))
            self.goto_page(bmk[BookmarkField.PAGE])

    def _action_slider_changed(self, absolute_page_number) -> None:
        """ The slider has changed so update page numbers """
        self._update_pages_shown(absolute_page_number)
        self._update_note_indicator(absolute_page_number)

    def _action_slider_released(self) -> None:
        """ Slider released so update the progress bar. """
        self.goto_page(self.sender().value())

    def _action_note(self, page: int, seq: int, title_suffix: str):
        """ Add a note to a page """
        dbnote = DbNote()
        uinote = UiNote()
        book_id = self.dlbook.get_id()
        note = dbnote.get_note(book_id, page=page, seq=seq)

        uinote.set_text(note[NoteField.NOTE])
        uinote.set_location(note[NoteField.LOCATION])
        uinote.set_title(
            f"{self.dlbook.title} - {title_suffix}")
        uinote.set_id(
            (note[NoteField.ID] if NoteField.ID in note and note[NoteField.ID] > 0 else None))
        if uinote.exec():
            if uinote.delete() and NoteField.ID in note:
                dbnote.delete_note(note)
            elif uinote.text_changed():
                note[NoteField.NOTE] = uinote.text()
                note[NoteField.LOCATION] = uinote.location()
                dbnote.add(note)
                self.ui.set_book_note(True)

    def action_clicked_bookmark(self) -> None:
        """ menu clicked on bookmark """
        if self.ui.btn_bookmark.text() != "":
            self.action_goto_bookmark()

    def _about_to_show_script_list(self) -> None:
        self.ui.menu_toolscript.clear()
        keys = sorted(self.toollist.keys())
        for key in keys:
            recent = self.ui.menu_toolscript.addAction(key)
            recent.set_data(self.toollist[key])
        self.ui.menu_toolscript.setEnabled(len(keys) > 0)

    # FILE ACTIONS
    def _about_to_show_file_menu(self) -> None:
        is_import_set = ImportSettings.get_select() is not None
        self.ui.action_file_import_pdf.setEnabled(is_import_set)
        self.ui.action_file_import_dir.setEnabled(is_import_set)
        # self.ui.action_file_reimport.setEnabled(is_import_set)

    def _action_file_open(self) -> None:
        of = Openfile()
        of.exec()
        if of.book_name is not None:
            self.open_book(of.book_name)

    def _action_file_open_recent(self, action_: QAction) -> None:
        if action_ is not None:
            self.open_book(action_.data())

    def _about_to_show_file_recent(self) -> None:
        show_filepath = decode(
            code=DbKeys.ENCODE_BOOL,
            value=self.dilpref.get_value(
                key=DbKeys.SETTING_SHOW_FILEPATH,
                default=DbKeys.VALUE_SHOW_FILEPATH)
            )
        self.ui.menu_open_recent.clear()
        filenames = DilBook().recent()
        if filenames is not None and len(filenames) > 0:
            if show_filepath:
                format_line = '&{:2d}.  {}   {} {}'
            for entry, book_entry in enumerate(filenames, start=1):
                if show_filepath:
                    recent_label = format_line.format(
                        entry,
                        book_entry[BookField.NAME],
                        "\U0001F4C1",
                        book_entry[BookField.LOCATION])
                else:
                    recent_label = f'&{entry:2d}.  {book_entry[BookField.NAME]}'
                recent_action_ = self.ui.menu_open_recent.addAction(
                    recent_label)
                recent_action_.set_data(book_entry[BookField.NAME])
        # end if len(filenames)
        self.ui.menu_open_recent.setEnabled((len(filenames) > 0))

    def _action_file_reopen(self) -> None:
        self.close_book()
        self.open_lastbook()

    def _action_file_close(self) -> None:
        self.close_book()

    def _action_file_delete(self) -> None:
        df = Deletefile()
        if df.delete():
            self.logger.info(f'Deleted book {df.book_name}')

    def _show_import_status(self, good_completion, number_files: int):
        qmsg_box = QMessageBox()
        qmsg_box.setIcon(QMessageBox.Information)
        qmsg_box.setWindowTitle('Import PDF Documents')
        qmsg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        if good_completion:
            qmsg_box.setText(f"Imported {number_files} documents.")
        else:
            qmsg_box.setText("Failed to import documents")
        qmsg_box.show()
        qmsg_box.exec()

    def _action_file_import_document(self) -> None:
        uiconvert = UiImportPDFDocuments()
        uiconvert.set_base_directory(self.import_dir)
        uiconvert.process_files()
        ui_completion = uiconvert.add_books_to_library()
        self.import_dir = str(uiconvert.base_directory())
        len_files = len(uiconvert.import_files())
        del uiconvert
        self._show_import_status(ui_completion, len_files)

    def _action_file_import_document_dir(self) -> None:
        uiconvert = UiImportPdfDirectory()
        uiconvert.set_base_directory(self.import_dir)
        uiconvert.process_files()
        uiconvert.add_books_to_library()
        self.import_dir = str(uiconvert.base_directory())
        del uiconvert

    def _action_file_select_import(self) -> None:
        """ Select a PDF import script """
        importset = UiImportSetting()
        importset.pick_import()

    def _action_file_import_pdf(self) -> None:
        uiconvert = UiConvertFilenames()
        uiconvert.set_base_directory(self.import_dir)
        uiconvert.process_files()
        if uiconvert.add_books_to_library():
            lfiles = len(uiconvert.import_files() )
            QMessageBox.information(
                None,
                'Import PDF Files to Images',
                f"Converted {lfiles} PDFs.",
                QMessageBox.Ok
            )
        self.import_dir = str(uiconvert.base_directory())
        del uiconvert

    def _action_file_import_dir(self) -> None:
        uiconvert = UiConvertPDFDocumentDirectory()
        uiconvert.set_base_directory(self.import_dir)
        uiconvert.process_files()
        uiconvert.add_books_to_library()
        self.import_dir = uiconvert.base_directory()
        del uiconvert

    def _action_file_reimport(self) -> None:
        rif = Reimportfile()
        if rif.exec() == QMessageBox.Accepted:
            # self.logger.info('Re-import book {}'.rif.book_name)
            book = self.dlbook.getbook(book=rif.book_name)
            uiconvert = UiConvertFilenames()
            if not isfile(book[BookField.SOURCE]):
                book[BookField.SOURCE] = self._lost_and_found_book(book[BookField.NAME])
                if book[BookField.SOURCE] is None:
                    return

            if uiconvert.process_file(book[BookField.SOURCE]):
                uiconvert.add_books_to_library()
            del uiconvert
        del rif

    def _action_file_import_images(self) -> None:
        addbook = UiAddBook()
        addbook.import_book()

    def _action_file_import_images_dir(self) -> None:
        addbook = UiAddBook()
        addbook.import_directory()

    def _action_file_library_consolidate(self) -> None:
        UiLibraryConsolidate().exec()

    def _action_file_library_check(self) -> None:
        UiLibraryCheck().exec()

    def _action_file_library_stats(self) -> None:
        UiLibraryStats().exec()

    # EDIT ACTIONS
    def _about_to_show_edit_menu(self) -> None:
        edit_label = self.ui.action_edit_page.text().split('#', 1)
        self.ui.action_edit_page.setEnabled(self.dlbook.is_open())
        if self.dlbook.is_open():
            page = self.dlbook.page_to_relative()
            if self.dlbook.is_page_relative(page):
                tag = f"{page} / Book: {self.dlbook.pagenumber}"
            else:
                tag = f"{page}"
            self.ui.action_edit_page.setText(
                f"{edit_label[0]} #{tag}")
        else:
            self.ui.action_edit_page.setText(edit_label[0])

    def _action_edit_page(self) -> None:
        script = None
        while script is None:
            script = self.dilpref.get_value(
                DbKeys.SETTING_PAGE_EDITOR_SCRIPT, None)
            if not script:
                if QMessageBox.Yes == QMessageBox.warning(
                    None,
                    "",
                    "No script editor is set.\nSet an editor?",
                    QMessageBox.No | QMessageBox.Yes
                ):
                    self._action_edit_preferences()
                else:
                    return
        # We have a script
        run_vars = [
            "-BOOK",        self.dlbook.filepath(),
            "-PAGE",        self.dlbook.page_filepath(
                self.dlbook.pagenumber, required=False),
            "-TITLE",        self.dlbook.title,
            "-O",    platform.platform(terse=True),
        ]
        runner = RunSilentRunDeep(script, run_vars)
        runner.run()
        self._action_refresh()

    def _action_edit_properties(self) -> None:
        property_editor = UiProperties(self.dlbook.get_properties())
        if property_editor.exec():
            if self.dlbook.update_properties(property_editor.get_changes()):
                bookname = self.dlbook.title
                self.open_book(bookname)

    def _action_edit_preferences(self) -> None:
        try:

            pref = UiPreferences()
            pref.format_data()
            pref.exec()
            changes = pref.get_changes()
            if len(changes) > 0:
                self.dilpref.save_all(changes)
            # settings = self.dilpref.get_all()
            # self.ui.set_navigation_shortcuts(settings)
            # self.ui.set_bookmark_shortcuts(settings)
                self.open_book(self.dlbook.title)
        except Exception as err:
            err_str = str(err)
            self.logger.critical(
                f"Error opening preferences: {err_str}")
            QMessageBox.critical(
                None,
                ProgramConstants.SYSTEM_NAME,
                f"Error opening preferences:\n{err_str}",
                QMessageBox.Cancel
            )

    def _action_edit_note_book(self) -> None:
        self._action_note(page=0, seq=0, title_suffix='(Book Note)')

    def _action_edit_note_page(self, note_id):
        del note_id
        absolute_page = self.dlbook.pagenumber
        if self.dlbook.is_page_relative(absolute_page):
            title = f"Page: {self.dlbook.page_to_relative()} (Book: {absolute_page})"
        else:
            title = f"Book: {absolute_page}"
        self._action_note(page=absolute_page, seq=0, title_suffix=title)

    # VIEW ACTIONS
    def _action_refresh(self) -> None:
        QPixmapCache().clear()
        self.open_book(self.dlbook.title)

    def _action_view_one_page(self) -> None:
        self._set_display_page_layout(DbKeys.VALUE_PAGES_SINGLE)

    def _action_view_two_side(self) -> None:
        self._set_display_page_layout(DbKeys.VALUE_PAGES_SIDE_2)

    def _action_view_two_stack(self) -> None:
        self._set_display_page_layout(DbKeys.VALUE_PAGES_STACK_2)

    def _action_view_three_side(self) -> None:
        self._set_display_page_layout(DbKeys.VALUE_PAGES_SIDE_3)

    def _action_view_three_stack(self) -> None:
        self._set_display_page_layout(DbKeys.VALUE_PAGES_STACK_3)

    def _action_view_status_bar(self, state) -> None:
        self.dilpref.set_value(
            key=DbKeys.SETTING_WIN_STATUS_ENABLED,
            replace=True,
            value=encode( state, DbKeys.ENCODE_BOOL)
        )
        self.ui.action_view_status.setChecked(state)
        self.ui.statusbar.setVisible(state)

    def _action_view_aspect_ratio(self, state) -> None:
        self.dlbook.keep_aspect_ratio = state
        self.ui.pager.keep_aspect_ratio = state
        self._load_pages()

    def _action_view_smart_pages(self, state: bool) -> None:
        self.dlbook.set_property(DbKeys.SETTING_SMART_PAGES, state)
        self.ui.pager.set_smartpage(state)
        self.dlbook.set_property(DbKeys.SETTING_SMART_PAGES, state)

    # BOOKMARK ACTIONS
    def _action_bookmark_show(self) -> None:

        bmk = UiBookmark()
        while True:
            bookmark_list = self.bookmark.all()
            if len(bookmark_list) == 0:
                QMessageBox.information(
                    None, "Bookmarks", "There are no bookmarks", QMessageBox.Cancel)
                break
            if bmk.setup_data(bookmark_list, relative_offset=self.dlbook.relative_offset):
                bmk.exec()
                if not bmk.selected[BookmarkField.PAGE]:
                    break
                if bmk.action_ == bmk.action_Edit:
                    bmk_edit = UiBookmarkEdit(totalPages=self.dlbook.count(
                    ), numbering_offset=self.dlbook.relative_offset)
                    bmk_edit.setWindowTitle(
                        f"Edit bookmark for '{self.dlbook.title}'")
                    bmk_edit.setup_data(bmk.selected)
                    if bmk_edit.exec() == QDialog.Accepted:
                        changes = bmk_edit.get_changes()
                        if len(changes) > 0:
                            self.bookmark.add(
                                book=self.dlbook.get_id(),
                                bookmark=changes[BookmarkField.NAME],
                                page=changes[BookmarkField.PAGE]
                            )
                    continue
                if bmk.action_ == bmk.action_Go:
                    self._finish_bookmark_navigation(bmk.selected)
                if bmk.action_ == bmk.action_file_delete:
                    self.bookmark.delete(
                        book=self.dlbook.get_id(), bookmark=bmk.selected[BookmarkField.NAME])
                break
        self._update_menu_bmk_nav()

    def _action_bookmark_current(self) -> None:
        self.bookmark.current_book(
            self.dlbook.title,
            self.dlbook.page_to_relative(),
            self.dlbook.pagenumber)
        self._update_menu_bmk_nav()

    def _action_bookmark_add(self) -> None:
        dlg = UiBookmarkAdd(
            total_pages=self.dlbook.count(),
            numbering_offset=self.dlbook.relative_offset)
        dlg.setWindowTitle(
            f"Add Bookmark for '{self.dlbook.title}'")
        while dlg.exec() == QDialog.Accepted:
            changes = dlg.get_changes()
            self.bookmark.save(
                name=changes[BookmarkField.NAME],
                page=changes[BookmarkField.PAGE])
            if dlg.button_was_save:  # One shot operation
                break
            dlg.clear()
        self._update_menu_bmk_nav()

    def _action_bookmark_go_previous(self) -> None:
        bmk = self.bookmark.get_previous(self.dlbook.pagenumber)
        self._finish_bookmark_navigation(bmk)

    def _action_bookmark_go_next(self) -> None:
        bmk = self.bookmark.get_next(self.dlbook.pagenumber)
        self._finish_bookmark_navigation(bmk)

    def _action_bookmark_delete_all(self) -> None:
        qmbox_rtn = QMessageBox.warning(
            None,
            f"{self.dlbook.title}",
            "Delete all booksmarks for book?\nThis cannot be undone.",
            QMessageBox.No | QMessageBox.Yes
        )
        if qmbox_rtn == QMessageBox.Yes:
            self.logger.info(
                f'Delete all bookmarks for {self.dlbook.title}')
            self.bookmark.delete_all(book=self.dlbook.title)
            self._update_menu_bmk_nav()

    # TOOL ACTIONS
    def _action_tool_refresh(self, action: QAction) -> None:
        del action
        tl = GenerateToolList()
        self.toollist = tl.rescan()
        self.ui.menu_toolscript.clear()

    def _action_tool_check(self) -> None:
        """ Check and update the books """
        DilBook().update_incomplete_books_ui()

    def _action_tool_script(self, action_: QAction) -> None:
        if action_ is not None:
            if action_.text() in self.toollist:
                key = action_.text()
                if self.toollist[key].isSimple():
                    runner = UiRunSimpleNote(self.toollist[key].path())
                else:
                    runner = UiRunScript(self.toollist[key].path())
                runner.run()

    def action_goto_bookmark(self) -> None:
        """ action goto to a bookmark """
        ui_bmk = UiBookmark(
            self.dlbook.title, self.bookmark.get_all(), self.dlbook.relative_offset)
        ui_bmk.exec()
        new_page = ui_bmk.selected_page
        if new_page:
            self.goto_page(new_page)
            self.set_title(ui_bmk.selectedBookmark)
        del ui_bmk

    def _set_menu_book_options(self, show=True) -> None:
        """ Enable menus when file is open"""
        self.ui.action_edit_properties.setEnabled(show)
        self.ui.action_file_close.setEnabled(show)
        self.ui.action_file_reopen.setEnabled(show)
        # self.ui.action_file_delete.setEnabled(show)
        self.ui.action_refresh.setEnabled(show)

        self.ui.action_bookmark_current.setEnabled(show)
        self.ui.action_bookmark_show_all.setEnabled(show)
        self.ui.action_bookmark_delete_all.setEnabled(show)
        self.ui.action_bookmark_add.setEnabled(show)

        self.ui.action_up.setEnabled(show)
        self.ui.action_down.setEnabled(show)
        self.ui.action_goto_page.setEnabled(show)
        self.ui.action_first_page.setEnabled(show)
        self.ui.action_last_page.setEnabled(show)

        self.ui.action_aspect_ratio.setEnabled(show)
        self.ui.action_smart_pages.setEnabled(show)
        self.ui.action_one_page.setEnabled(show)
        self.ui.action_two_pages.setEnabled(show)
        self.ui.action_two_pages_stacked.setEnabled(show)
        self.ui.action_three_pages.setEnabled(show)
        self.ui.action_three_pages_stacked.setEnabled(show)

        self.ui.action_edit_note_book.setEnabled(show)
        self.ui.action_edit_note_page.setEnabled(show)

        if not show:
            self._set_menu_page_options('off')

    # HELP
    def _action_help_about(self) -> None:
        UiAbout().exec()

    def _action_help(self) -> None:
        try:
            DbConn.close_db()
            uihelp = UiHelp(self, self.get_main_path())
            uihelp.setup_help()
            uihelp.exec()
        except Exception as err:
            self.logger.error(
                f"Exception occured during help: {str(err)}" )
        finally:
            DbConn.open_db()

    # # # #
    def _set_menu_page_options(self, layout_type: str) -> None:
        if layout_type is None:
            layout_type = self.system.get_value(
                DbKeys.SETTING_PAGE_LAYOUT, DbKeys.VALUE_PAGES_SINGLE)
        self.ui.action_one_page.setChecked(
            (layout_type == DbKeys.VALUE_PAGES_SINGLE))
        self.ui.action_two_pages.setChecked(
            (layout_type == DbKeys.VALUE_PAGES_SIDE_2))
        self.ui.action_two_pages_stacked.setChecked(
            (layout_type == DbKeys.VALUE_PAGES_STACK_2))
        self.ui.action_three_pages.setChecked(
            (layout_type == DbKeys.VALUE_PAGES_SIDE_3))
        self.ui.action_three_pages_stacked.setChecked(
            (layout_type == DbKeys.VALUE_PAGES_STACK_3))

    def _set_display_page_layout(self, value):
        """ Set the display to either one page or two,
        depending on what value is in the book entry"""
        self.dlbook.set_property(DbKeys.SETTING_PAGE_LAYOUT, value)
        self.ui.pager.set_display(value)
        self._set_menu_page_options(value)
        self._load_pages()

    def _lost_and_found_book(self, book_name: str) -> str:
        self.logger.warning(f'Could not locate book {book_name}')
        if QMessageBox.Yes != QMessageBox.critical(
            None,
            "",
            "Book cannot be located.\nWould you like to find it?",
                QMessageBox.No | QMessageBox.Yes):
            return None

        (filename, _) = QFileDialog.getOpenFileName(
            None,
            book_name,
            "",
            filter="(*.pdf *.PDF)")

        return filename

    # GO ACTIONS
    def _action_go_page(self) -> None:
        get_page_number = PageNumber(
            self.dlbook.page_to_relative(), self.dlbook.is_page_relative())
        if get_page_number.exec() == 1:
            pn = get_page_number.page
            if get_page_number.relative:
                pn = self.dlbook.page_to_absolute(pn)
            self.goto_page(pn)

    def _action_go_page_first(self) -> None:
        self.dlbook.pagenumber = self.dlbook.get_first_page_shown()
        self._load_pages()
        self.update_status_bar()

    def _action_go_page_last(self) -> None:
        self.dlbook.pagenumber = self.dlbook.get_last_page_shown()
        self._load_pages()
        self.update_status_bar()

    #####
    def intro_image(self) -> None:
        """Display an introductory image if one is found
        """
        intro_image_path = os.path.join(os.path.dirname(
            __file__), "images", "sheetmusic.png")
        if os.path.isfile(intro_image_path):
            qpx_map = QPixmap(intro_image_path)
            self.ui.pager.staticPage(qpx_map)
            self.show()


def main_is_frozen():
    """ Return true if code has been packaged as 'frozen' """
    return (hasattr(sys, "frozen") or
            hasattr(sys, "importers") or
            (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')))


def get_main_dir():
    """ Get main directory Take into account if file is frozen or not """
    if main_is_frozen():
        # print 'Running from path', os.path.dirname(sys.executable)
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


if __name__ == "__main__":
    syspref = SystemPreferences()
    dbLocation = syspref.dbpath
    mainDirectory = syspref.dbdirectory

    q_app = QApplication([])
    # This will initialise the system. It requires prompting so uses dialog box
    if not isfile(dbLocation) or not os.path.isdir(mainDirectory):
        from util.beginsetup import Initialise
        ini = Initialise()
        ini.run(dbLocation)
        del ini
        # force to re-read
        dbLocation = syspref.dbpath
        mainDirectory = syspref.get_dbdirectory

    DbConn.open_db(dbLocation)
    setup = Setup()

    setup.init_data()
    setup.logging(mainDirectory)
    setup.system_update()

    logger = logging.getLogger('main')

    del syspref
    del setup

    window = SheetMusic()
    window.connect_menus()
    window.restore_window_from_settings()
    window.show()

    window.open_lastbook()
    window.setup_wheel_timer()
    window.show()
    rtn = q_app.exec()
    DbConn.destroy_connection()
    sys.exit(rtn)
