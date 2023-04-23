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
import gc
import logging
import os
import platform
import sys

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow,  QMessageBox, QDialog, QFileDialog
from PySide6.QtGui import QPixmap, QAction, QPixmapCache

from qdb.dbconn import DbConn
from qdb.dbsystem import DbSystem
from qdb.keys import BOOK, BOOKPROPERTY, BOOKSETTING, BOOKMARK, DbKeys, NOTE, ProgramConstants
from qdb.setup import Setup
from qdb.dbnote import DbNote
from qdb.log import DbLog, Trace

from qdil.preferences import DilPreferences, SystemPreferences
from qdil.book import DilBook
from qdil.bookmark import DilBookmark

from ui.main import UiMain
from ui.properties import UiProperties
from ui.bookmark import UiBookmark
from ui.file import Openfile, Deletefile, DeletefileAction, Reimportfile
from ui.note import UiNote

from util.convert import toBool
from util.toollist import GenerateToolList
from util.toolconvert import ImportSettings


class MainWindow(QMainWindow):
    MAX_PAGES = 3
    RESIZE_TIMER = 100

    def __init__(self):
        super().__init__()

        self.loadUi()
        self.logger = DbLog( 'MainWindow')
        self.logger.debug('Program starting')
        self.book = DilBook()
        self.system = DbSystem()
        self.bookmark = DilBookmark()
        self._notelist = None
        self.import_dir = self.pref.getValue(DbKeys.SETTING_LAST_IMPORT_DIR)
        tl = GenerateToolList()
        self.toollist = tl.list()
        
        del tl

        self._perform_resize = False
        self._timer = QTimer()
        self._timer.timeout.connect( self._set_page_size )
        self._timer.setSingleShot( True )

    def loadUi(self) -> None:
        self.pref = DilPreferences()
        self.ui = UiMain()
        self.ui.setupUi(self)

    def pageList(self, start_page, len_list) -> list:
        """ pageList creates a list, MAX_PAGES long, of the pages. The first entry will always be the one requests."""
        plist = [0]*self.MAX_PAGES
        if start_page < 1:
            start_page = 1
        totalpages = self.book.count()
        for i in range(0, len_list):
            if start_page+i > totalpages:
                break
            plist[i] = start_page+i
        return plist

    def loadPages(self) -> bool:
        """ Load all pages into the book at once. This loads the MAX_PAGES every time.

            This attempts to optimise page loads and display by looking at the number of
            pages we load.
        """
        if self.book.isOpen():
            page = self.book.pagenumber
            # work some 'magic' Show page-n...page IF page is last page.
            totalPages = self.book.count()
            showingPages = self.ui.pager.numberPages()
            if page == totalPages and showingPages and showingPages > 1:
                plist = self.pageList(page-showingPages+1, self.MAX_PAGES)
                self._loadPageWidgetList(plist)
            else:
                self._loadPageWidgetList(self.pageList(page, self.MAX_PAGES))
        return self.book.isOpen()

    def reloadPages(self) -> bool:
        if self.book.isOpen():
            self._loadPageWidgetList(self.ui.pager.page_numbers())
        return self.book.isOpen()

    def _loadPageWidgetList(self, plist: list):
        if len(plist) < self.MAX_PAGES:
            plist.extend([0] * (self.MAX_PAGES - len(plist)))
        return self._loadPageWidget(plist[0], plist[1], plist[2])

    def _loadPageWidget(self, pg1: int, pg2: int, pg3: int):
        self.logger.debug( Trace.callstr())
        page1 = self.book.page_filepath(pg1)
        page2 = self.book.page_filepath(pg2)
        page3 = self.book.page_filepath(pg3)
        self.logger.debug( 'Pages: {}, {}, {}'.format( pg1, pg2, pg3))
        self.ui.pageWidget().resize(self.ui.stacks.size())
        self.ui.pager.loadPages(page1, pg1, page2, pg2, page3, pg3)
        self.book.pagenumber = (pg1)
        self.update_status_bar()

    def _update_pages_shown(self, absolute_page_number: int = None) -> None:
        """ Update status bar with page numbers """
        self.ui.set_absolute_page(
            absolute_page_number, self.book.count(), self.book.relative_offset)
        lbl = 'Page' if self.book.isPageRelative(
            absolute_page_number) else "Book"
        self.ui.label_page_relative.setText("{}:{:4d}".format(
            lbl, self.book.page_to_relative(absolute_page_number)))

    def updateBookmarkMenuNav(self, bookmark=None):
        has_bookmarks = (self.bookmark.count() > 0)
        self.ui.action_bookmark_previous.setEnabled(has_bookmarks)
        self.ui.action_bookmark_next.setEnabled(has_bookmarks)
        self.ui.action_bookmark_show_all.setEnabled(has_bookmarks)
        self.ui.action_bookmark_delete_all.setEnabled(has_bookmarks)

        if bookmark is not None:
            self.ui.action_bookmark_previous.setDisabled(
                self.bookmark.isFirst(bookmark))
            self.ui.action_bookmark_next.setDisabled(
                self.bookmark.isLast(bookmark))

    def _update_note_indicator(self, page_number: int):
        nlist = self.getNoteList(self.book.getID())
        if len(nlist):
            self.ui.setBookNote((0 in nlist))
            self.ui.setPageNote((page_number in nlist), page_number)
        else:
            self.ui.setBookNote(False)
            self.ui.setPageNote(False)

    def update_status_bar(self) -> None:
        """ Update status with page numbers, slider position and note indicators """
        absolute_page_number = self.book.pagenumber

        self.ui.slider_page_position.setMaximum(self.book.count())
        self.ui.slider_page_position.setValue(absolute_page_number)

        self._update_pages_shown(absolute_page_number)
        self._update_note_indicator(absolute_page_number)

    def restoreWindowFromSettings(self) -> None:
        self.pref.restoreMainWindow(self.ui.getWindow())
        self.pref.restoreShortcuts(self.ui)
        self._action_view_status_bar(self.pref.getValueBool(
            DbKeys.SETTING_WIN_STATUS_ENABLED, True))

    def getNoteList(self, book_id: int, refresh=False) -> dict:
        if book_id is not None and (self._notelist is None or refresh):
            self._notelist = {}
            dbnote = DbNote()
            returnlist = dbnote.getAll(book_id)
            for note in returnlist:
                self._notelist[note[NOTE.page]] = note
        return self._notelist

    def _show_png(self):
        pass
    def _show_pdf( self ):
        pass

    def open_book(self, newBookName: str, page=None) -> None:
        """ """
        self.close_book()
        self.logger.debug( f"BEGIN '{newBookName}'" )
        self.logger.debug( Trace.callstr() )
        rtn = QMessageBox.Retry
        while rtn == QMessageBox.Retry:
            rtn = self.book.open(newBookName, page)

        if rtn == QMessageBox.AcceptRole:
            book_layout = self.book.get_property(BOOKPROPERTY.layout, system=True)
            smart_page_turn = toBool(self.book.get_property(DbKeys.SETTING_SMART_PAGES, system=True))
            aspect_ratio = self.book.keep_aspect_ratio
            self.book.pagenumber = self.book.lastPageRead 

            self.ui.showPager( self.book.getFileType(), self.book.renderbookpdf() )
            self.ui.pageWidget().setDisplay(book_layout)
            self.ui.pageWidget().setSmartPageTurn( smart_page_turn )
            self.ui.pageWidget().setKeepAspectRatio(aspect_ratio)
            self.ui.pageWidget().dimensions = self.book.get_property( BOOKSETTING.dimensions )
            self.loadPages()

            # Update page and menu displays
            self.setTitle()
            self._set_menu_book_options(True)
            self._set_menu_page_options(book_layout )
            self.ui.actionAspectRatio.setChecked(aspect_ratio)
            self.ui.actionSmartPages.setChecked( smart_page_turn )

            self.bookmark.open(newBookName )
            self.updateBookmarkMenuNav(self.bookmark.getBookmarkPage(page))

            self.ui.pageWidget().show()
            self.update_status_bar()
        else:
            self.logger.warning( f"Couldn't open {newBookName}")
            if rtn == QMessageBox.DestructiveRole:
                self.book.delBook(newBookName)
            self.openLastBook( noretry=newBookName)
        self.logger.debug(f'END "{newBookName}"')

        return

    def close_book(self) -> None:
        """ Close the book, save a pointer to it, and hide the menu items. """
        self._notelist = None
        if self.book.isOpen():
            self.pref.setValue(DbKeys.SETTING_LAST_BOOK_NAME,
                               self.book.title)
            self.book.close()
            self.ui.pager.clear()
            cache = QPixmapCache()
            cache.clear()
        self._set_menu_book_options(False)
        self.ui.mainWindow.hide()
        gc.collect()

    def setupWheelTimer(self) -> None:
        self.wheelTimer = QTimer(self)
        self.wheelTimer.setInterval(1000)  # 500 msec == .5 seconds
        self.wheelTimer.setSingleShot(True)
        self.direction = None

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if (event.type() == QEvent.Gesture):
            object.blockSignals(True)
            if (event.GestureType() == Qt.SwipeGesture):
                if (event.horizontalDirection() == 'Left'):
                    self.page_previous()
                if (event.horizontalDirection() == 'Right'):
                    self.page_forward()
                object.blockSignals(False)
                return True
        ###
        # TODO: Need a better way to reduce page flips, otherwise
        # the screen acts erratic.
        ###
        if (event.type() == QEvent.Wheel):
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
                            self.page_previous()
                        else:
                            self.page_forward()

                        self.direction = None
                else:
                    if x < 0:
                        self.direction = 'Left'
                    else:
                        self.direction = 'Right'
            object.blockSignals(False)
            return True
        # End Wheel

        return False

    def _set_page_size( self ):
        self.ui.pageWidget().resize(self.ui.stacks.size())
        self.reloadPages()


    def resizeEvent(self, event):
        if self._timer.isActive():
            self._timer.stop()
        self._timer.start( MainWindow.RESIZE_TIMER )
            

    def keyPressEvent(self, ev) -> None:
        # if False and (ev.type() == QEvent.KeyPress):
        #    key = ev.key()
        #    if (key == Qt.Key_Left):
        #        self.goFirstBookmark() if ev.modifiers() & Qt.ControlModifier else self.page_previous()
        #    if (key == Qt.Key_Right):
        #        self.goLastBookmark() if ev.modifiers() & Qt.ControlModifier else self.page_forward()

        super().keyPressEvent(ev)

    def closeEvent(self, event) -> None:
        """ called when the program is closed """
        self.pref.saveMainWindow(self.ui.getWindow())
        self.pref.setValue(DbKeys.SETTING_LAST_IMPORT_DIR,
                           self.import_dir, replace=True)
        self.close_book()
        DbConn.closeDB()

    def page_previous(self) -> None:
        pg = self.ui.pager.getLowestPageShown()-1
        if self.book.isValidPage(pg):
            self.ui.pager.previousPage(
                self.book.page_filepath(pg), pg, end=(pg == 1))
            self.book.pagenumber = (pg)
            self.update_status_bar()

    def page_forward(self) -> None:
        pg = self.ui.pager.getHighestPageShown()+1
        if self.book.isValidPage(pg):
            self.book.pagenumber = (pg)
            self.ui.pager.nextPage(self.book.page_filepath(
                pg), pg, end=(pg == self.book.count()))
            self.update_status_bar()

    def go_to_page(self, page: int) -> None:
        ''' Set the page number to the page passed and display
            page number must be absolute, not relative.
        '''
        if page:
            self.book.pagenumber = (page)
            self.loadPages()
            self.update_status_bar()

    def goFirstBookmark(self) -> None:
        bmk = self.bookmark.first()
        self.book.pagenumber = (bmk[BOOKMARK.page])
        self.loadPages()

    def goLastBookmark(self) -> None:
        bmk = self.bookmark.getLast()
        self.book.pagenumber = (bmk[BOOKMARK.page])
        self.loadPages()

    def connectMenus(self) -> None:
        """ Connect menus and events to the routines handling the function"""
        # FILE:
        self.ui.menuFile.aboutToShow.connect(self._about_to_show_file_menu)
        self.ui.action_file_open.triggered.connect(self._action_file_open)
        self.ui.menuOpenRecent.aboutToShow.connect(
            self._about_to_show_file_recent)
        self.ui.menuOpenRecent.triggered.connect(self._action_file_open_recent)
        self.ui.action_file_reopen.triggered.connect(self._action_file_reopen)
        self.ui.action_file_close.triggered.connect(self._action_file_close)
        self.ui.action_file_delete.triggered.connect(self._action_file_delete)
        # --------------
        self.ui.action_file_import_document.triggered.connect(
            self._action_file_import_document )
        self.ui.action_file_import_document_dir.triggered.connect(
            self._action_file_import_document_dir )
        # ---------------
        self.ui.action_file_select_import.triggered.connect(
            self._action_file_select_import)
        self.ui.action_file_import_PDF.triggered.connect(
            self._action_file_import_PDF)
        self.ui.action_file_import_dir.triggered.connect(
            self._action_file_import_dir)
        self.ui.action_file_reimport.triggered.connect(
            self._action_file_reimport)
        self.ui.action_file_import_images.triggered.connect(
            self._action_file_import_images)
        self.ui.action_file_import_images_dir.triggered.connect(
            self._action_file_import_images_dir)
        #------
        self.ui.action_file_library_consolidate.triggered.connect(
            self._action_file_library_consolidate )
        self.ui.action_file_library_check.triggered.connect(
            self._action_file_library_check )
        self.ui.action_file_library_stats.triggered.connect(
            self._action_file_library_stats )

        # EDIT:
        self.ui.menuEdit.aboutToShow.connect(self._about_to_show_edit_menu)
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
        self.ui.actionOne_Page.triggered.connect(self._action_view_one_page)
        self.ui.actionTwo_Pages.triggered.connect(self._action_view_two_side)
        self.ui.actionTwo_Pages_Stacked.triggered.connect(
            self._action_view_two_stack)
        self.ui.actionThree_Pages.triggered.connect(
            self._action_view_three_side)
        self.ui.actionThree_Pages_Stacked.triggered.connect(
            self._action_view_three_stack)
        # --------------
        self.ui.actionAspectRatio.triggered.connect(
            self._action_view_aspect_ratio)
        self.ui.actionViewStatus.triggered.connect(
            self._action_view_status_bar)
        self.ui.actionSmartPages.triggered.connect(
            self._action_view_smart_pages)

        # GO:
        self.ui.actionGo_to_Page.triggered.connect(self._action_go_page)
        self.ui.actionFirstPage.triggered.connect(self._action_go_page_first)
        self.ui.actionLastPage.triggered.connect(self._action_go_page_last)
        # --------------
        self.ui.actionUp.triggered.connect(self.page_previous)
        self.ui.actionDown.triggered.connect(self.page_forward)
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
        self.ui.btn_bookmark.clicked.connect(self.actionClickedBookmark)

        # TOOLS

        self.ui.menuToolScript.aboutToShow.connect(
            self._about_to_show_script_list)
        self.ui.action_tool_check.triggered.connect(self._action_tool_check)
        self.ui.action_tool_refresh.triggered.connect(
            self._action_tool_refresh)
        self.ui.menuToolScript.triggered.connect(self._action_tool_script)

        # HELP:
        self.ui.action_help_about.triggered.connect(self._action_help_about)
        self.ui.action_help.triggered.connect(self._action_help)

        # INTERNAL
        self.ui.slider_page_position.valueChanged.connect(
            self._action_slider_changed)
        self.ui.slider_page_position.sliderReleased.connect(
            self._action_slider_released)

        # self.ui.actionBookmark.triggered.connect(self.actionGoBookmark)
        # self.ui.twoPagesSide.installEventFilter( self)

    def openLastBook(self, noretry:str = None) -> None:
        if self.pref.getValueBool(DbKeys.SETTING_LAST_BOOK_REOPEN, True):
            recent = self.book.getRecent()
            if recent is None or len(recent) == 0:
                self.logger.info('No last book to open')
            else:
                last_book_name = recent[0][BOOK.name]
                self.logger.debug(f'Recent book "{last_book_name}" noretry: "{noretry}"')
                if noretry != last_book_name:
                    self.open_book(recent[0][BOOK.name])
            

    def setTitle(self, bookmark: str = None) -> None:
        """ Title is made of the title and bookmark if there is one """
        if bookmark:
            title = "{}: {} - {}".format(ProgramConstants.system_name,
                                         self.book.title, bookmark)
        else:
            title = "{}: {}".format(
                ProgramConstants.system_name, self.book.title)
        self.ui.mainWindow.setWindowTitle(title)
        self.ui.mainWindow.show()

    def _finishBookmarkNavigation(self, bmk: dict) -> None:
        if bmk is not None and BOOKMARK.page in bmk and bmk[BOOKMARK.page] is not None:
            self.ui.action_bookmark_previous.setDisabled(
                self.bookmark.isFirst(bmk))
            self.ui.action_bookmark_next.setDisabled(self.bookmark.isLast(bmk))
            self.go_to_page(bmk[BOOKMARK.page])

    def _action_slider_changed(self, absolute_page_number) -> None:
        """ The slider has changed so update page numbers """
        self._update_pages_shown(absolute_page_number)
        self._update_note_indicator(absolute_page_number)

    def _action_slider_released(self) -> None:
        """ Slider released so update the progress bar. """
        self.go_to_page(self.sender().value())

    def _actionNote(self, page: int, seq: int, titleSuffix: str):
        dbnote = DbNote()
        uinote = UiNote()
        id = self.book.getID()
        note = dbnote.getNote(id, page=page, seq=seq)

        uinote.setText(note[NOTE.note])
        uinote.setLocation(note[NOTE.location])
        uinote.setWindowTitle(
            "{} - {}".format(self.book.title, titleSuffix))
        uinote.setID(
            (note[NOTE.id] if NOTE.id in note and note[NOTE.id] > 0 else None))
        rtn = uinote.exec()
        if rtn:
            if uinote.delete() and NOTE.id in note:
                dbnote.deleteNote(note)
            elif uinote.textChanged():
                note[NOTE.note] = uinote.text()
                note[NOTE.location] = uinote.location()
                dbnote.add(note)
                self.ui.setBookNote(True)

    def actionClickedBookmark(self) -> None:
        if self.ui.btn_bookmark.text() != "":
            self.actionGoBookmark()

    def _about_to_show_script_list(self) -> None:
        self.ui.menuToolScript.clear()
        keys = sorted(self.toollist.keys())
        for key in keys:
            recent = self.ui.menuToolScript.addAction(key)
            recent.setData(self.toollist[key])
        self.ui.menuToolScript.setEnabled(len(keys) > 0)

    # FILE ACTIONS
    def _about_to_show_file_menu(self) -> None:
        is_import_set = (ImportSettings.get_select() is not None)
        self.ui.action_file_import_PDF.setEnabled(is_import_set)
        self.ui.action_file_import_dir.setEnabled(is_import_set)
        #self.ui.action_file_reimport.setEnabled(is_import_set)

    def _action_file_open(self) -> None:
        of = Openfile()
        of.exec()
        if of.bookName is not None:
            self.open_book(of.bookName)

    def _action_file_open_recent(self, action: QAction) -> None:
        if action is not None:
            self.open_book(action.data())

    def _about_to_show_file_recent(self) -> None:
        show_filepath = self.pref.getValueBool(
            DbKeys.SETTING_SHOW_FILEPATH, DbKeys.VALUE_SHOW_FILEPATH)
        self.ui.menuOpenRecent.clear()
        fileNames = DilBook().getRecent()
        if fileNames is not None and len(fileNames) > 0:
            if show_filepath:
                format_line = '&{:2d}.  {}   {} {}'
            for entry, bookEntry in enumerate(fileNames, start=1):
                if show_filepath:
                    recent_label = format_line.format(
                        entry, bookEntry[BOOK.name], "\U0001F4C1", bookEntry[BOOK.location])
                else:
                    recent_label = '&{:2d}.  {}'.format(
                        entry, bookEntry[BOOK.name])
                recent_action = self.ui.menuOpenRecent.addAction(recent_label)
                recent_action.setData(bookEntry[BOOK.name])
        # end if len(fileNames)
        self.ui.menuOpenRecent.setEnabled((len(fileNames) > 0))

    def _action_file_reopen(self) -> None:
        self.close_book()
        self.openLastBook()

    def _action_file_close(self) -> None:
        self.close_book()

    def _action_file_delete(self) -> None:
        df = Deletefile()
        if df.delete():
            self.logger.info( f'Deleted book {df.bookName}')

    def _show_import_status(self, good_completion, number_files:int ):
        dlg = QMessageBox()
        dlg.setIcon( QMessageBox.Information )
        dlg.setWindowTitle( 'Import PDF Documents')
        dlg.setStandardButtons( QMessageBox.StandardButton.Ok )
        if good_completion :
            dlg.setText( f"Imported {number_files} documents." )
            print('ok')
        else:
            dlg.setText( "Failed to import documents")
            print('fail')
        dlg.show()
        rtn=dlg.exec()

    def _action_file_import_document(self)->None:
        from util.toolconvert import UiImportPDFDocuments
        uiconvert = UiImportPDFDocuments()
        uiconvert.setBaseDirectory(self.import_dir)
        uiconvert.process_files()
        ui_completion = uiconvert.add_books_to_library()
        self.import_dir = str(uiconvert.baseDirectory())
        len_files = len( uiconvert.importFiles() )
        del uiconvert
        self._show_import_status( ui_completion , len_files )
        
        print( ui_completion, 'done with action file import document')
        

    def _action_file_import_document_dir(self)->None:
        from util.toolconvert import UiImportPdfDirectory
        uiconvert = UiImportPdfDirectory()
        uiconvert.setBaseDirectory(self.import_dir)
        uiconvert.process_files()
        ui_completion = uiconvert.add_books_to_library()
        self.import_dir = str( uiconvert.baseDirectory() )
        del uiconvert

    def _action_file_select_import(self) -> None:
        """ Select a PDF import script """
        from util.toolconvert import UiImportSetting
        importset = UiImportSetting()
        importset.pick_import()

    def _action_file_import_PDF(self) -> None:
        from util.toolconvert import UiConvertFilenames
        uiconvert = UiConvertFilenames()
        uiconvert.setBaseDirectory(self.import_dir)
        uiconvert.process_files()
        if uiconvert.add_books_to_library():
            QMessageBox.information(
                None,
                'Import PDF Files to Images',
                "Converted {} PDFs.".format( len( uiconvert.importFiles() )),
                QMessageBox.Ok
            )
        self.import_dir = str(uiconvert.baseDirectory())
        del uiconvert

    def _action_file_import_dir(self) -> None:
        from util.toolconvert import UiConvertPDFDocumentDirectory
        uiconvert = UiConvertPDFDocumentDirectory()
        uiconvert.setBaseDirectory(self.import_dir)
        uiconvert.process_files()
        ui_completion = uiconvert.add_books_to_library()
        self.import_dir = uiconvert.baseDirectory()
        del uiconvert

    def _action_file_reimport(self) -> None:
        rif = Reimportfile()
        if rif.exec() == QMessageBox.Accepted:
            self.logger.info('Re-import book {}'.rif.bookName )
            book = self.book.getBook(book=rif.bookName)
            from util.toolconvert import UiConvertFilenames
            uiconvert = UiConvertFilenames()
            if not isfile(book[BOOK.source]):
                book[BOOK.source] = self._lost_and_found_book(book[BOOK.name])
                if book[BOOK.source] is None:
                    return

            if uiconvert.processFile(book[BOOK.source]):
                ui_completion = uiconvert.add_books_to_library()
            del uiconvert
        del rif

    def _action_file_import_images( self )->None:
        from ui.addbook import UiAddBook
        addbook = UiAddBook()
        addbook.import_book()

    def _action_file_import_images_dir( self )->None:
        from ui.addbook import UiAddBook
        addbook = UiAddBook()
        addbook.import_directory()

    def _action_file_library_consolidate( self )->None:
        from ui.library import UiLibraryConsolidate
        UiLibraryConsolidate().exec()

    def _action_file_library_check( self )->None:
        from ui.library import UiLibraryCheck
        UiLibraryCheck().exec()

    def _action_file_library_stats(self)->None:
        from ui.library import UiLibraryStats
        UiLibraryStats().exec()

    # EDIT ACTIONS
    def _about_to_show_edit_menu(self) -> None:
        edit_label = self.ui.action_edit_page.text().split('#', 1)
        self.ui.action_edit_page.setEnabled(self.book.isOpen())
        if self.book.isOpen():
            page = self.book.page_to_relative()
            if self.book.isPageRelative(page):
                tag = "{} / Book: {}".format(page, self.book.pagenumber)
            else:
                tag = "{}".format(page)
            self.ui.action_edit_page.setText(
                "{} #{}".format(edit_label[0], tag))
        else:
            self.ui.action_edit_page.setText(edit_label[0])

    def _action_edit_page(self) -> None:
        script = None
        while script is None:
            script = self.pref.getValue(
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
        vars = [
            "-BOOK",        self.book.filepath(),
            "-PAGE",        self.book.page_filepath(
                self.book.pagenumber , required=False),
            "-TITLE",        self.book.title,
            "-O",    platform.platform(terse=True),
        ]
        runner = RunSilentRunDeep(script, vars)
        runner.run()
        self._action_refresh()

    def _action_edit_properties(self) -> None:
        property_editor = UiProperties(self.book.get_properties() )
        if property_editor.exec():
            if self.book.update_properties( property_editor.get_changes() ):
                bookname = self.book.title
                self.open_book( bookname )

    def _action_edit_preferences(self) -> None:
        try:
            from ui.preferences import UiPreferences
            pref = UiPreferences()
            pref.formatData()
            pref.exec()
            changes = pref.getChanges()
            if len(changes) > 0:
                self.pref.saveAll(changes)
            # settings = self.pref.getAll()
            # self.ui.setNavigationShortcuts(settings)
            # self.ui.setBookmarkShortcuts(settings)
                self.open_book( self.book.title )
        except Exception as err:
            self.logger.critical('Error opening preferences: {}'.format( str(err)))
            QMessageBox.critical(
                None,
                ProgramConstants.system_name,
                "Error opening preferences:\n{}".format(str(err)),
                QMessageBox.Cancel
            )

    def _action_edit_note_book(self) -> None:
        self._actionNote(page=0, seq=0, titleSuffix='(Book Note)')

    def _action_edit_note_page(self, id):
        absolute_page = self.book.pagenumber
        if self.book.isPageRelative(absolute_page):
            title = "Page: {} (Book: {})".format(
                self.book.page_to_relative(), absolute_page)
        else:
            title = "Book: {}".format(absolute_page)
        self._actionNote(page=absolute_page, seq=0, titleSuffix=title)

    # VIEW ACTIONS
    def _action_refresh(self) -> None:
        cache = QPixmapCache()
        cache.clear()
        self.open_book( self.book.title )
        

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
        self.pref.setValueBool(
            DbKeys.SETTING_WIN_STATUS_ENABLED, state, replace=True)
        self.ui.actionViewStatus.setChecked(state)
        self.ui.statusbar.setVisible(state)

    def _action_view_aspect_ratio(self, state) -> None:
        self.book.keep_aspect_ratio = (state)
        self.ui.pager.setKeepAspectRatio( state )
        self.loadPages()

    def _action_view_smart_pages(self, state: bool) -> None:
        self.book.set_property(DbKeys.SETTING_SMART_PAGES, state)
        self.ui.pager.setSmartPageTurn( state )
        self.book.set_property( DbKeys.SETTING_SMART_PAGES, state) 

    # BOOKMARK ACTIONS
    def _action_bookmark_show(self) -> None:
        from ui.bookmark import UiBookmark, UiBookmarkEdit
        bmk = UiBookmark()
        while True:
            bookmarkList = self.bookmark.getAll()
            if len(bookmarkList) == 0:
                QMessageBox.information(
                    None, "Bookmarks", "There are no bookmarks", QMessageBox.Cancel)
                break
            if bmk.setupData(bookmarkList, relativeOffset=self.book.relative_offset()):
                bmk.exec()
                if not bmk.selected[BOOKMARK.page]:
                    break
                markName = bmk.selected[BOOKMARK.name]
                if bmk.action == bmk.actionEdit:
                    bmkEdit = UiBookmarkEdit(totalPages=self.book.count(
                    ), numberingOffset=self.book.relative_offset())
                    bmkEdit.setWindowTitle(
                        "Edit bookmark for '{}'".format(self.book.title))
                    bmkEdit.setupData(bmk.selected)
                    if bmkEdit.exec() == QDialog.Accepted:
                        changes = bmkEdit.getChanges()
                        if len(changes) > 0:
                            self.bookmark.add(
                                book=self.book.getID(),
                                bookmark=changes[BOOKMARK.name],
                                page=changes[BOOKMARK.page]
                            )
                    continue
                if bmk.action == bmk.actionGo:
                    self._finishBookmarkNavigation(bmk.selected)
                if bmk.action == bmk.action_file_delete:
                    self.bookmark.delete(
                        book=self.book.getID(), bookmark=bmk.selected[BOOKMARK.name])
                break
        self.updateBookmarkMenuNav()

    def _action_bookmark_current(self) -> None:
        self.bookmark.thisBook(
            self.book.title,
            self.book.page_to_relative(),
            self.book.pagenumber)
        self.updateBookmarkMenuNav()

    def _action_bookmark_add(self) -> None:
        from ui.bookmark import UiBookmarkAdd
        dlg = UiBookmarkAdd(
            totalPages=self.book.count(),
            numberingOffset=self.book.relative_offset())
        dlg.setWindowTitle(
            "Add Bookmark for '{}'".format(self.book.title))
        while dlg.exec() == QDialog.Accepted:
            changes = dlg.getChanges()
            self.bookmark.saveBookmark(
                bookmarkName=changes[BOOKMARK.name],
                pageNumber=changes[BOOKMARK.page])
            if dlg.button_was_save:  # One shot operation
                break
            dlg.clear()
        self.updateBookmarkMenuNav()

    def _action_bookmark_go_previous(self) -> None:
        bmk = self.bookmark.getPrevious(self.book.pagenumber)
        self._finishBookmarkNavigation(bmk)

    def _action_bookmark_go_next(self) -> None:
        bmk = self.bookmark.getNext(self.book.pagenumber)
        self._finishBookmarkNavigation(bmk)

    def _action_bookmark_delete_all(self) -> None:
        rtn = QMessageBox.warning(
            None,
            "{}".format(self.book.title),
            "Delete all booksmarks for book?\nThis cannot be undone.",
            QMessageBox.No | QMessageBox.Yes
        )
        if rtn == QMessageBox.Yes:
            self.logger.info('Delete all bookmarks for {}'.self.book.title )
            self.bookmark.delete_all(book=self.book.title)
            self.updateBookmarkMenuNav()

    # TOOL ACTIONS
    def _action_tool_refresh(self, action: QAction) -> None:
        tl = GenerateToolList()
        self.toollist = tl.rescan()
        self.ui.menuToolScript.clear()

    def _action_tool_check(self) -> None:
        from qdil.book import DilBook
        DilBook().updateIncompleteBooksUI()
        pass

    def _action_tool_script(self, action: QAction) -> None:
        if action is not None:
            if action.text() in self.toollist:
                from ui.runscript import UiRunSimpleNote, UiRunScript
                key = action.text()
                if self.toollist[key].isSimple():
                    runner = UiRunSimpleNote(self.toollist[key].path())
                else:
                    runner = UiRunScript(self.toollist[key].path())
                runner.run()

    def actionGoBookmark(self) -> None:
        uiBookmark = UiBookmark(self.book.title, self.bookmark.getAll(), self.book.relative_offset )
        uiBookmark.exec()
        newPage = uiBookmark.selectedPage
        if newPage:
            self.go_to_page(newPage)
            self.setTitle(uiBookmark.selectedBookmark)
        del uiBookmark

    def _set_menu_book_options(self, show=True) -> None:
        """ Enable menus when file is open"""
        self.ui.action_edit_properties.setEnabled(show)
        self.ui.action_file_close.setEnabled(show)
        self.ui.action_file_reopen.setEnabled(show)
        #self.ui.action_file_delete.setEnabled(show)
        self.ui.action_refresh.setEnabled(show)

        self.ui.action_bookmark_current.setEnabled(show)
        self.ui.action_bookmark_show_all.setEnabled(show)
        self.ui.action_bookmark_delete_all.setEnabled(show)
        self.ui.action_bookmark_add.setEnabled(show)

        self.ui.actionUp.setEnabled(show)
        self.ui.actionDown.setEnabled(show)
        self.ui.actionGo_to_Page.setEnabled(show)
        self.ui.actionFirstPage.setEnabled(show)
        self.ui.actionLastPage.setEnabled(show)

        self.ui.actionAspectRatio.setEnabled(show)
        self.ui.actionSmartPages.setEnabled(show)
        self.ui.actionOne_Page.setEnabled(show)
        self.ui.actionTwo_Pages.setEnabled(show)
        self.ui.actionTwo_Pages_Stacked.setEnabled(show)
        self.ui.actionThree_Pages.setEnabled(show)
        self.ui.actionThree_Pages_Stacked.setEnabled(show)

        self.ui.action_edit_note_book.setEnabled(show)
        self.ui.action_edit_note_page.setEnabled(show)

        if not show:
            self._set_menu_page_options('off')

    # HELP
    def _action_help_about(self) -> None:
        from ui.about import UiAbout
        UiAbout().exec()

    def _action_help(self) -> None:
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
            self.logger.error(
                "Exception occured during help: {}".format(str(err)))
        finally:
            DbConn.openDB()

    # # # #
    def _set_menu_page_options(self, layoutType: str) -> None:
        if layoutType is None:
            layoutType = self.system.getValue(
                DbKeys.SETTING_PAGE_LAYOUT, DbKeys.VALUE_PAGES_SINGLE)
        self.ui.actionOne_Page.setChecked(
            (layoutType == DbKeys.VALUE_PAGES_SINGLE))
        self.ui.actionTwo_Pages.setChecked(
            (layoutType == DbKeys.VALUE_PAGES_SIDE_2))
        self.ui.actionTwo_Pages_Stacked.setChecked(
            (layoutType == DbKeys.VALUE_PAGES_STACK_2))
        self.ui.actionThree_Pages.setChecked(
            (layoutType == DbKeys.VALUE_PAGES_SIDE_3))
        self.ui.actionThree_Pages_Stacked.setChecked(
            (layoutType == DbKeys.VALUE_PAGES_STACK_3))

    def _set_display_page_layout(self, value):
        """ Set the display to either one page or two, depending on what value is in the book entry"""
        self.book.set_property(DbKeys.SETTING_PAGE_LAYOUT, value)
        self.ui.pager.setDisplay(value)
        self._set_menu_page_options(value)
        self.loadPages()

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
        from ui.page import PageNumber
        getPageNumber = PageNumber(
            self.book.page_to_relative(), self.book.isPageRelative())
        if getPageNumber.exec() == 1:
            pn = getPageNumber.page
            if getPageNumber.relative:
                pn = self.book.page_to_absolute(pn)
            self.go_to_page(pn)

    def _action_go_page_first(self) -> None:
        self.book.pagenumber = (self.book.getFirstPageShown())
        self.loadPages()
        self.update_status_bar()

    def _action_go_page_last(self) -> None:
        self.book.pagenumber = (self.book.getLastPageShown())
        self.loadPages()
        self.update_status_bar()

    #####
    def introImage(self) -> None:
        imagePath = os.path.join(os.path.dirname(
            __file__), "images", "sheetmusic.png")
        if os.path.isfile(imagePath):
            px = QPixmap(imagePath)
            self.ui.pager.staticPage(px)
            self.show()


if __name__ == "__main__":
    sy = SystemPreferences()
    dbLocation = sy.getPathDB()          # Fetch the system settings
    mainDirectory = sy.getDirectory()       # Get directory

    app = QApplication([])
    # This will initialise the system. It requires prompting so uses dialog box
    if not isfile(dbLocation) or not os.path.isdir(mainDirectory):
        from util.beginsetup import Initialise
        ini = Initialise()
        ini.run(dbLocation)
        del ini
        # force to re-read
        dbLocation = sy.getPathDB()          # Fetch the system settings
        mainDirectory = sy.getDirectory()       # Get directory

    DbConn.openDB(dbLocation)
    setup = Setup()

    setup.initData()
    setup.logging(mainDirectory)
    setup.system_update()

    logger = logging.getLogger('main')

    del sy
    del setup

    window = MainWindow()
    window.connectMenus()
    window.restoreWindowFromSettings()
    window.show()

    window.openLastBook()
    window.setupWheelTimer()
    window.show()
    rtn = app.exec()
    DbConn.destroyConnection()
    sys.exit(rtn)
