"""
User Interface :  Bottom Sheet

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

# NOTE: There is some weird stuff with 3 pages. C++ deletes SheetMusicWidgets
# even when the references are just fine. There are some sloppy fixes to
# get around this. Sorry. I'll continue to try and change this.

from PySide6.QtCore import QSize
from PySide6.QtGui import (Qt)
from PySide6.QtWidgets import (
    QHBoxLayout, QSizePolicy, QWidget,
    QMainWindow, QVBoxLayout)
from qdb.keys import DbKeys
from qdb.log import DbLog
from ui.borderglow import BorderGlow
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget
from util.pdfclass import PdfDimensions


class BottomSheet():
    """BottomSheet is the base for display sheets

    Raises:
        RuntimeError: Throw when not extended
        ValueError: No layout set

    """
    FORWARD = True
    BACKWARD = False

    LAYOUT_WIDTH = 'width'
    LAYOUT_HEIGHT = 'height'
    LAYOUT_PAGES = 'count'
    LAYOUT_SETUP = '©up'
    LAYOUT_CREATE = 'layout'
    ALL_PAGES = 3

    _layout = {
        DbKeys.VALUE_PAGES_SINGLE:  {
            LAYOUT_WIDTH:  1,
            LAYOUT_HEIGHT: 1,
            LAYOUT_PAGES:  1},
        DbKeys.VALUE_PAGES_SIDE_2:  {
            LAYOUT_WIDTH:  2,
            LAYOUT_HEIGHT: 1,
            LAYOUT_PAGES:  2},
        DbKeys.VALUE_PAGES_SIDE_3:  {
            LAYOUT_WIDTH:  3,
            LAYOUT_HEIGHT: 1,
            LAYOUT_PAGES:  3},
        DbKeys.VALUE_PAGES_STACK_2: {
            LAYOUT_WIDTH:  1,
            LAYOUT_HEIGHT: 2,
            LAYOUT_PAGES: 2},
        DbKeys.VALUE_PAGES_STACK_3: {
            LAYOUT_WIDTH:  1,
            LAYOUT_HEIGHT: 3,
            LAYOUT_PAGES:  3},
    }

    def __init__(self, main_window: QMainWindow, name: str):
        self._page_refs = []
        self._dimensions = None
        self._direction = self.FORWARD
        self._current_layout = None
        self._current_layout_mode = None
        self._window_height = None
        self._window_width = None
        self._page_width = None
        self._page_height = None
        self._smart_turn = False
        self._pdfmode = False
        self.layout_pages_stacked = None
        self.layout_pages_side = None

        self.border_glow = BorderGlow()
        self._define_layout()
        self._set_size(main_window)
        self.logger = DbLog('BottomSheet')

        self.create_main_pagewidget(name)

    def _define_layout(self) -> dict:
        """
            Fill in layouts  """
        self._layout[DbKeys.VALUE_PAGES_SINGLE][self.LAYOUT_SETUP] = self._create_layout_sidebyside()
        self._layout[DbKeys.VALUE_PAGES_SIDE_2][self.LAYOUT_SETUP] = self._create_layout_sidebyside()
        self._layout[DbKeys.VALUE_PAGES_SIDE_3][self.LAYOUT_SETUP] = self._create_layout_sidebyside()
        self._layout[DbKeys.VALUE_PAGES_STACK_2][self.LAYOUT_SETUP] = self._create_layout_stacked()
        self._layout[DbKeys.VALUE_PAGES_STACK_3][self.LAYOUT_SETUP] = self._create_layout_stacked()

    # -----------------------------------------------
    #     ACTION / CREATION METHODS
    # -----------------------------------------------
    #
    def _add_page_widget(self, page: int) -> None:
        """ Add the page widget to the layout if it isn't there already """
        if not self._page_refs[page].is_visible():
            if self._current_layout.indexOf(self._page_refs[page].widget()) < 0:
                self._current_layout.insertWidget(
                    page, self._page_refs[page].widget(),  0)
        self._page_refs[page].show()

    def create_main_pagewidget(self, name: str) -> QWidget:
        """ This will create the main widget used to hold the pages"""
        self.main_pagewidget = QWidget()
        self.main_pagewidget.setObjectName(name)
        self.main_pagewidget.setEnabled(True)
        self.main_pagewidget.setVisible(True)
        self.main_pagewidget.grabGesture(Qt.SwipeGesture)
        self.main_pagewidget.setSizePolicy(
            self._create_sizepolicy(self.main_pagewidget))
        return self.main_pagewidget

    def content_generator(self, obj_name: str):
        """ This is a base class. Derived classes must define this method """
        raise RuntimeError('ContentGenerator not overridden')

    def _create_pages(self):
        """ Create all of the page content display widgets
            content generator must take one parm: label and
            return a display widget that conforms to the
            interface 'ISheetMusicDisplay'
        """

        self._page_refs = [self.content_generator(f"page-{ index+1 }")
                           for index in range(BottomSheet.ALL_PAGES)]
        for page in self._page_refs:
            page.widget().setStyleSheet("background: black")
            page.widget().hide()

    def _create_sizepolicy(self, widget) -> QSizePolicy:
        """ Create the page size policy used for the display widget"""
        size_policy = QSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        size_policy.setHeightForWidth(widget.size_policy().hasHeightForWidth())
        return size_policy

    def _create_layout_sidebyside(self) -> QHBoxLayout:
        self.layout_pages_side = QHBoxLayout()
        self.layout_pages_side.setObjectName("horizontalLayoutWidget")
        self.layout_pages_side.setContentsMargins(0, 0, 0, 0)
        return self.layout_pages_side

    def _create_layout_stacked(self) -> QVBoxLayout:
        self.layout_pages_stacked = QVBoxLayout()
        self.layout_pages_stacked.setObjectName("VerticalLayoutWidget")
        self.layout_pages_stacked.setContentsMargins(0, 0, 0, 0)
        return self.layout_pages_stacked

    def _set_size(self, window_size: QMainWindow | QSize) -> bool:
        """ Save the size for the main window. This will accept
            QMainWindow, QSize. Do not call this
            directly; resize will call it and it should be called first
        """
        if window_size is not None:
            if isinstance(window_size, QMainWindow):
                window_size = window_size.size()
            if isinstance(window_size, QSize):
                self._window_width = window_size.width()
                self._window_height = window_size.height()
        return self._window_width is not None and self._window_height is not None

    def _size_pages(self):
        self._page_width = int(
            self._window_width / self._get_layout_value(self.LAYOUT_WIDTH))
        self._page_height = int(
            self._window_height / self._get_layout_value(self.LAYOUT_HEIGHT))
        if self._page_width and self._page_height:
            for index in range(self.number_pages()):
                self._page_refs[index].resize(
                    self._page_width, self._page_height)

    def resize(self, size: QSize | None = None) -> None:
        """ This must be called everytime the window is resized and on startup
            You should pass the qsize or width in. It will be called on creation
            to set sizes correctly
        """
        if self._set_size(size) and self._current_layout_mode:
            self._size_pages()

    def show(self) -> None:
        """ Display the pages, resize to fit and force the main widget to display"""
        self.show_pages()
        self.main_pagewidget.show()

    def show_pages(self, maxpages: int = 0) -> None:
        """ Show all the pages and issue a resize """
        if maxpages == 0 or maxpages > self.number_pages():
            maxpages = self.number_pages()
        for index in range(maxpages):
            self._add_page_widget(index)

    def _hide_page(self, page: int) -> None:
        """ Index is offset from zero """

        if self._page_refs[page].is_visible():
            self._current_layout.removeWidget(self._page_refs[page])
        self._page_refs[page].hide()

    def hide_pages(self, maxpage: int = 0) -> None:
        """ Remove all from the page layout """
        if maxpages == 0 or maxpages > len(self._page_refs):
            maxpages = len(self._page_refs)
        for page in range(0, maxpage):
            self._hide_page(page)

    def clear(self):
        """ Clear all pages (displayed or not), but do not remove them from layout"""
        self.border_glow.stop()
        for page in self._page_refs:
            page.clear()

    # -----------------------------------------------
    #        PROPERTY METHODS
    # -----------------------------------------------
    #
    def dimensions(self) -> PdfDimensions:
        """ Get the PDF dimensions from current document """
        if self._dimensions is None:
            self.set_dimensions(PdfDimensions())
        return self._dimensions

    def set_dimensions(self, dimensions: PdfDimensions):
        """ Set the widgets dimensions """
        self._dimensions = dimensions
        for page in self._page_refs:
            page.widget().dimensions = self.dimensions

    @property
    def keep_aspect_ratio(self) -> bool:
        """ Only return the flag from page one
            All pages have the same flag set and page one is always displayed"""
        return self._page_refs[0].keep_aspect_ratio

    @keep_aspect_ratio.setter
    def keep_aspect_ratio(self, flag: bool):
        """ Set aspect ratio flag for all pages """
        for page in self._page_refs:
            page.keep_aspect_ratio = flag
            page.widget().keep_aspect_ratio = flag

    def _get_layout_value(self, key):
        return self._layout[self._current_layout_mode][key]

    def _remove_current_layout(self) -> None:
        if self._current_layout_mode is not None and self._current_layout is not None:
            # self.hide_pages()                            # Remove all pages from layout
            QWidget().setLayout(self._current_layout)  # Set current to dummy widget
            self._current_layout = None

    def set_display(self, layout: str) -> None:
        """This will set the page layout to be either side-by-side or stacked
            If there is a setup mode already set, it will be removed and replaced

        Args:
            layout (str): layout mode, defined in self._layout array
            Options are single, double, triple, side, stacked

        Raises:
            ValueError: Invalid layout
        """
        if layout not in self._layout:
            raise ValueError(
                f"Internal error: Unknown layout requested layout {layout}")
        if self._current_layout_mode != layout:
            self._current_layout_mode = layout
            self._remove_current_layout()
            self._current_layout = self._layout[layout][self.LAYOUT_SETUP]()
            self._create_pages()
            numpages = self.number_pages()
            for index in range(numpages):
                self._current_layout.insertWidget(
                    index, self._page_refs[index].widget())
            self.show_pages(numpages)
            self.main_pagewidget.setLayout(self._current_layout)
            self._size_pages()

    def set_smartpage(self, state: bool) -> bool:
        """ Set the smart turn feature and return the previous state """
        rtn = self._smart_turn
        self._smart_turn = state
        return rtn

    @property
    def usepdf(self) -> bool:
        """ return if we are setting PDF mode or not """
        return self._pdfmode

    @usepdf.setter
    def set_usepdf(self, state: bool) -> None:
        self._pdfmode = state
        for page in self._page_refs:
            page.pdfdisplaymode = state

    #  -----------------------------------------------
    #         PAGE MOVEMENT METHODS
    #  -----------------------------------------------

    def _roll_forward(self, page_number: int) -> bool:
        """
            OK, so we have up to 'n' pages loaded but on 'p' pages are
            displayed. If we have the page already, promote that by 'rolling'
            forward.
            * page must be in list of pages held
            * can't be displaying all of the pages
            * page isn't displayed
        """
        roll = False
        while (page_number in self.page_numbers() and
                not self.is_shown(page_number) and
                self.number_pages() != self.ALL_PAGES
               ):
            roll = True
            self._page_refs[0].copy(self._page_refs[1])
            self._page_refs[1].copy(self._page_refs[2])
            self._page_refs[2].clear()
        return roll

    def _roll_forward_zeros(self, endpage: int):
        if endpage != 0:
            while self._page_refs[0].page_number() == 0:
                self._page_refs[0].copy(self._page_refs[1])
                self._page_refs[1].copy(self._page_refs[2])
                self._page_refs[2].clear()

    def _simple_next_page(self, content: object, page_number: int):
        pageshown = self.number_pages()
        if pageshown == 1:
            self._page_refs[0].set_content_page(content, page_number)
        elif pageshown == 2:
            self._page_refs[0].copy(self._page_refs[1])
            self._page_refs[1].set_content_page(content, page_number)
        else:
            self._page_refs[0].copy(self._page_refs[1])
            self._page_refs[1].copy(self._page_refs[2])
            self._page_refs[2].set_content_page(content, page_number)

    def _simple_previous_page(self, content: object, page_number: int):
        self._page_refs[2].copy(self._page_refs[1])
        self._page_refs[1].copy(self._page_refs[0])
        self._page_refs[0].set_content_page(content, page_number)

    def _smart_page(self, plw: ISheetMusicDisplayWidget, content: object, page_number: int) -> None:
        self.border_glow.stop()
        plw.set_content_page(content, page_number)
        self.border_glow.start(plw.widget())

    def load_pages(self,
                   content_1: object, page_number1: int,
                   content_2: object, page_number2: int,
                   content_3: object, page_number3: int):
        """ load_pages should be called whenever a book is opened. It setups for
            either 'smart' page turn or for simple page turning.
        """
        # pylint: disable=C0209
        self.logger.debug('Load {} {} {}'.format(
            page_number1, page_number2, page_number3))
        # pylint: enable=C0209
        self._page_refs[0].dimensions = self.dimensions
        self._page_refs[0].set_content_page(content_1, page_number1)
        self._page_refs[1].dimensions = self.dimensions
        self._page_refs[1].set_content_page(content_2, page_number2)
        self._page_refs[2].dimensions = self.dimensions
        self._page_refs[2].set_content_page(content_3, page_number3)
        self._direction = self.FORWARD
        self._size_pages()

    def next_page(self, content: object, page_number: int, end: bool = False):
        """ go to next page """
        if not end or not self.is_shown(page_number):
            if self._smart_turn and self.number_pages() > 1:
                self._smart_page(self.first_page_widget(),
                                 content, page_number)
            else:
                self._simple_next_page(content, page_number)
        self._direction = self.FORWARD

    def previous_page(self, content: object, page_number: int, end: bool = False):
        """ Go to previous page """
        if not end or not self.is_shown(page_number):
            if self._smart_turn and self.number_pages() > 1:
                self._smart_page(self.last_page_widget(), content, page_number)
            else:
                self._simple_previous_page(content, page_number)
        self._direction = self.BACKWARD

    # -----------------------------------------------
    #      PAGE NUMBER INFORMATION METHODS
    # -----------------------------------------------

    def current_pages(self) -> list[str]:
        """ Return a list of printable page descriptions (Used for debugging/logging)"""
        rtn = []
        if self._current_layout is not None:
            for i in range(self._current_layout.count()):
                item = self._current_layout.itemAt(i).widget()
                desc = f"Item {i}: type: {type(item)} Objectname: {item.objectName}"
                rtn.append(desc)
        return rtn

    def page_numbers(self) -> list[int]:
        """Return page numbers displayed

        Returns:
            list[int]: List of current page numbers
        """
        return [page.page_number() for page in self._page_refs]

    def page_numbers_displayed(self) -> list[int]:
        """ Return all the page numbers currently displayed """
        return self.page_numbers()[0:self.number_pages()]

    def get_lowest_page_shown(self):
        """ Return the lowest page in the array that can be seen"""
        return min(self.page_numbers_displayed())

    def get_highest_page_shown(self):
        """ Return the highest page number in the array seen"""
        return max(self.page_numbers_displayed())

    def get_page_for_position(self, position: int) -> int:
        """ Return the page number for a position """
        return self.page_numbers()[position-1]

    def number_pages(self) -> int:
        """ Return how many pages will be shown for this layout """
        if self._current_layout_mode is None:
            return 0
        return self._layout[self._current_layout_mode][self.LAYOUT_PAGES]

    # -----------------------------------------------
    #     PAGE FIND METHODS
    # -----------------------------------------------

    def _find_page_by_pagenumber(self, page_number: int) -> ISheetMusicDisplayWidget | None:
        """ find the pagelabelwidget that is displayed and return to caller """
        search_list = self.page_numbers_displayed()
        if page_number in search_list:
            return self.all_pages()[search_list.index(page_number)]
        return None

    def set_pagelabel_stylesheet(self, page_number: int, style: str = "") -> bool:
        """ pagelabelwidget and set the stylesheet """
        page = self._find_page_by_pagenumber(page_number)
        if page:
            page.setStyleSheet(style)

    def is_shown(self, page: int) -> bool:
        """ Check to see if a page is currently displayed """
        return page in self.page_numbers_displayed()

    # -----------------------------------------------
    #        Object Access METHODS
    # -----------------------------------------------

    def get_widgets_in_page_order(self) -> list[ISheetMusicDisplayWidget]:
        """
        Return the widgets in page order

        Created to handle any number of pages. Bit over the top but didn't
        want to rewrite it again.
        """
        pnum = self.number_pages()
        if pnum == 1:
            return [self._page_refs[0]]

        key_pages = {}
        ordered = []

        for page in [self._page_refs[0], self._page_refs[1], self._page_refs[2]][0: pnum]:
            key_pages[page.page_number()] = page

        for key in sorted(key_pages):
            ordered.append(key_pages[key])
        return ordered

    def last_page_widget(self, offset: int = 0) -> ISheetMusicDisplayWidget:
        """ Return the last, highest, page widget in page order """
        ordered = self.get_widgets_in_page_order()
        index = max(len(ordered)-1-offset, 0)
        return ordered[index]

    def first_page_widget(self) -> ISheetMusicDisplayWidget:
        """ Return the first page widget in page order """
        return self.get_widgets_in_page_order()[0]

    def get_pager_widget(self):
        """ Get the main pager widget"""
        return self.main_pagewidget

    def all_pages(self) -> list:
        """ Return a list of all the page widgets"""
        return self._page_refs
