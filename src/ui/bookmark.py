"""
User Interface : Bookmarks

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import sys

from PySide6.QtWidgets import (
    QApplication, QDialog, QGridLayout,
    QDialogButtonBox, QTableWidget,
    QLineEdit, QCheckBox, QVBoxLayout,
    QHeaderView, QAbstractItemView,
    QTableWidgetItem, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from qdb.fields.bookmark import BookmarkField
from util.convert import to_int


class TableItem(QTableWidgetItem):
    """ Create a QTablewidgetItem with optional protected status"""

    def __init__(self, name, protected: bool = False):
        super().__init__(name)
        self.protected_data = None
        self._set_protected = None
        self._set_protected(protected)

    def set_protected(self, state: bool = False) -> None:
        """ Set protected state for table item """
        self._set_protected = state is True

    def is_protected(self) -> bool:
        """ Return current protected state """
        return self._set_protected


class UiBookmarkBase(QDialog):
    """UI inteface basic class for creating bookmark

    Args:
        QDialog (QDialog): extend dialog class
    """

    HDR_COL_0 = "Bookmark Name"
    HDR_COL_1 = "Page Shown"
    HDR_COL_2 = "Book Page"
    COL_NAME = 0
    COL_PAGE_SHOWN = 1
    COL_PAGE_BOOK = 2

    def __init__(self):
        """Setup the class, initialise variables
        """
        super().__init__()
        self.bookmark_table = None
        self.bookmark_name = None
        self.bookmark_page = None
        self.book_page = None
        self.page_shown = None

    def create_table_bookmark(self, columns=3):
        """ Create a table to display bookmarks """
        self.bookmark_table = QTableWidget(1, columns)
        self.bookmark_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.bookmark_table.clear()

        self.bookmark_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmark_table.verticalHeader().hide()
        self.bookmark_table.setShowGrid(True)

        self.bookmark_name = QTableWidgetItem()
        self.book_page = QTableWidgetItem()
        self.page_shown = QTableWidgetItem()

        self.book_page.setToolTip(
            "This is the absolute page numer in the book, not the page number displayed")
        self.page_shown.setToolTip(
            "The page number displayed. This is usually not the absolute page number in the book.")

        self.bookmark_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.book_page.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.page_shown.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.bookmark_name.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.book_page.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.page_shown.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

        self.bookmark_table.setItem(0, self.COL_NAME, self.bookmark_name)
        self.bookmark_table.setItem(0, self.COL_PAGE_BOOK, self.book_page)
        self.bookmark_table.setItem(0, self.COL_PAGE_SHOWN, self.page_shown)
        self.bookmark_table.adjustSize()

        self.bookmark_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmark_table.verticalHeader().hide()
        self.bookmark_table.setShowGrid(False)

    def set_values(self, name: str, page: int, relative: int):
        """ Set bookmark value """
        self.bookmark_name.setText(name)
        self.book_page.setText(page)
        self.page_shown.setText(relative)

    def clear(self):
        """ Clear bookmark table and reset headers """
        self.bookmark_table.clear()
        self.bookmark_table.setHorizontalHeaderLabels(
            (self.HDR_COL_0, self.HDR_COL_1, self.HDR_COL_2))


class UiBookmarkSingle(QDialog):
    """Display the values for a single bookmark
        This is meant to be extended not instantiated

    Args:
        QDialog (class): QDialog base class

    Raises:
        NotImplementedError: class was not properly extended

    Returns:
        UiBookmarkSingle: class that handles dialog
    """
    book_page_labelChecked = 'Book Page Number Shown'
    book_page_labelUnchecked = 'Book Page Number      '
    BtnCancel = 'Cancel'
    BtnSave = 'Save'

    def __init__(self, parent=None,
                 heading: str = None,
                 totalPages: int = None,
                 numbering_offset: int = None):
        super().__init__()

        self.bookmark_name = None
        self.book_page = None
        self.book_page_label = None
        self.page_shown = None
        self.err_msg = None
        self.button_was_save = None
        self.selected_row = None
        self.parent = parent

        self.setup()
        self.set_total_pages(totalPages)
        self.set_numbering_offset(numbering_offset)

        _main_layout = QVBoxLayout()
        _main_layout.addWidget(self._create_heading())
        _main_layout.addLayout(self._create_grid_layout())
        _main_layout.addWidget(self._create_buttons())
        self.setLayout(_main_layout)
        self.setSizeGripEnabled(True)

        self.set_heading(heading)

        self.resize(500, 200)
        self.changes = {}

    def setup(self):
        """ Setup base values """
        self.changes = {}
        self.numbering_offset = None
        self.page_valid = QIntValidator(1, 999, self)
        self.button_was_save = None

    def set_total_pages(self, totalpages: int = None):
        """ Set total pages for book """
        if totalpages is not None:
            self.page_valid.setTop(totalpages)

    def set_numbering_offset(self, pageoffset: int = None):
        """ When do pages actually start? """
        if pageoffset is not None:
            self.numbering_offset = pageoffset

    def set_fields(self, name: str, page: int, is_relative: bool = False):
        """ Set bookmark fields """
        self.bookmark_name.setText(name)
        if self.numbering_offset is not None:
            self.page_shown.setChecked(is_relative)
            self.page_shown.setEnabled(True)
        else:
            self.page_shown.setChecked(False)
            self.page_shown.setEnabled(False)
        self.book_page.setText(str(page))

    def _create_heading(self) -> QLabel:
        self.heading = QLabel()
        return self.heading

    def _create_grid_layout(self) -> QGridLayout:
        grid_layout = QGridLayout()
        row = 0
        row = self._create_name(grid_layout, row)
        row = self._create_page(grid_layout, row)
        row = self._create_shown(grid_layout, row)
        row = self._create_error(grid_layout, row)
        return grid_layout

    def _create_name(self,  grid: QGridLayout, row) -> int:
        self.bookmark_name = QLineEdit()
        grid.addWidget(QLabel("Bookmark Name"), row, 0)
        grid.addWidget(self.bookmark_name, row, 1)
        return row+1

    def _create_page(self, grid: QGridLayout, row) -> int:
        self.book_page = QLineEdit()
        self.book_page.setValidator(self.page_valid)
        self.book_page.textChanged.connect(self.page_numberChanged)
        self.book_page_label = QLabel(self.book_page_labelUnchecked)
        grid.addWidget(self.book_page_label, row, 0)
        grid.addWidget(self.book_page, row, 1)
        return row+1

    def _create_shown(self, grid: QGridLayout, row) -> int:
        self.page_shown = QCheckBox()
        self.page_shown.setText("Page number is page shown.")
        self.page_shown.setCheckable(self.numbering_offset is not None)
        if self.numbering_offset is not None:
            self.page_shown.setFocusPolicy(Qt.StrongFocus)
        self.page_shown.stateChanged.connect(self.checkbox_state_changed)
        grid.addWidget(self.page_shown, row, 1)
        return row+1

    def _create_error(self, grid: QGridLayout, row: int) -> int:
        self.err_msg = QLabel()
        grid.addWidget(self.err_msg, row, 1)
        return row+1

    def error(self, message: str = None):
        """ Display an error message in text area """
        if message is None:
            self.err_msg.clear()
        else:
            self.err_msg.setText(message)

    def set_heading(self, heading: str = None):
        """ Set Heading for dialog box """
        if heading is None:
            self.heading.clear()
        else:
            self.heading.setText(heading)

    def get_changes(self) -> dict:
        """Return a dictionay of key/value pairs of only
        field changes

        Returns:
            dict: [key]: changed-value
        """
        self.changes = {BookmarkField.NAME: self.bookmark_name.text().strip()}
        page_number = to_int(self.book_page.text().strip(), 0)

        # now fix up page depending on if they checked the box
        # (They can't check it if there is no page offset)
        if self.page_shown.checkState() == Qt.Checked:
            page_number += self.numbering_offset - 1
        if page_number > self.page_valid.top():
            page_number = self.page_valid.top()
        self.changes[BookmarkField.PAGE] = page_number
        return self.changes

    def clear(self):
        """ Clear the form and values """
        self.changes = {}
        self.page_shown.setChecked(False)
        self.bookmark_name.clear()
        self.book_page.clear()
        self.show()
        self.bookmark_name.setFocus()

    def has_acceptable_input(self) -> bool:
        """ Check input fields """
        if not self.book_page.has_acceptable_input():
            self.error(
                f"ERROR: Page must be between 1 and {self.page_valid.top()}")
            return False
        self.get_changes()
        if len(self.changes[BookmarkField.NAME]) <= 0:
            self.error("ERROR: Name must be entered")
            return False
        self.error()
        return True

    def checkbox_state_changed(self, state):
        """ Indicate a change """
        if state == Qt.Checked:
            self.book_page_label.setText(self.book_page_labelChecked)
            self.page_number_changed(self.book_page.text())
        else:
            self.book_page_label.setText(self.book_page_labelUnchecked)
            self.error()

    def page_number_changed(self, pagestr: str):
        """ Page shown has changed """
        if self.page_shown.checkState() == Qt.Checked:
            page = to_int(pagestr, 1) + self.numbering_offset-1
            self.error(f"(Book page is {page})")

    def _action_button_clicked(self, button):
        """ Either save or cancel was clicked"""
        self.button_was_save = button.text() == 'Save'
        if button.text() == 'Cancel':
            self.changes = {}
            self.reject()

        if self.has_acceptable_input():
            self.accept()

    # VIRTUAL FUNCTIONS
    def _create_buttons(self) -> QDialogButtonBox:
        raise NotImplementedError()


class UiBookmarkEdit(UiBookmarkSingle):
    """
        UiBookmarkEdit will edit one entry
    """

    def __init__(self, totalPages: int = None, numbering_offset: int = None, parent=None):
        super().__init__(totalPages=totalPages,
                         numbering_offset=numbering_offset, parent=parent)

    def setup_data(self, bookmark_entry: dict = None):
        """ figure out if this could be a relative page """
        page = bookmark_entry[BookmarkField.PAGE]
        is_relative = False
        if self.numbering_offset is not None:
            if page >= self.numbering_offset:
                page = page - self.numbering_offset + 1
                is_relative = True
        self.set_fields(bookmark_entry[BookmarkField.NAME], page, is_relative)

    def _create_buttons(self) -> QDialogButtonBox:
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.buttons.clicked.connect(self._action_button_clicked)
        return self.buttons


class UiBookmarkAdd(UiBookmarkSingle):
    """
        Add bookmark(s) for any page
    """
    labelTextNoPage = "Enter the <b>Bookmark Name</b>, and the <b>Book Page</b>."
    BtnSaveContinue = "Save and add more..."

    def __init__(self, heading: str = None, totalPages: int = None, numbering_offset: int = None):
        super().__init__(totalPages=totalPages, numbering_offset=numbering_offset)

    def _create_buttons(self, ) -> QDialogButtonBox:
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.BtnSaveContinue,
                               QDialogButtonBox.ApplyRole)
        self.buttons.addButton(QDialogButtonBox.Save)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.clicked.connect(self._action_button_clicked)
        return self.buttons

    def setup_data(self, current_page: int, is_page_relative: bool = False):
        """Setup page

        Args:
            current_page (int): Current page number
            is_page_relative (bool, optional):
                True if current_page is relative.
                Defaults to False.
        """
        self.book_page.setText(to_int(current_page, 1))
        if is_page_relative and self.numbering_offset is not None:
            self.page_shown.setChecked(True)

    def setup_fields(self, name: str, page: int = None):
        """Setup bookmark form fields

        Args:
            name (str): Name of bookmark
            page (int, optional):
                Page number.
                Defaults to None.
        """
        self.bookmark_name.setText(name)
        if page is not None:
            self.book_page.setText(str(page))
            self.bookmark_name.setFocus()
        else:
            self.book_page.setFocus(Qt.OtherFocusReason)


class UiBookmark(UiBookmarkBase):
    '''
    This is a disposable class (don't keep instances of it alive). This handles goto and destroy
    '''
    action_file_delete = 'delete'
    action_Go = 'go'
    action_Edit = 'edit'

    def __init__(self,
                 heading: str = None,
                 bookmark_list: list = None,
                 numbering_offset: int = None):
        super().__init__()

        self.selected = {}
        self.action_ = ''
        self.selected_row = None

        self.create_table_bookmark()
        self._create_buttons()
        _main_layout = QGridLayout()
        _main_layout.addWidget(self.bookmark_table, 3, 0, 1, 3)
        _main_layout.addWidget(self.buttons)
        self.setLayout(_main_layout)

        self.setWindowTitle(heading)
        self.setup_data(bookmark_list, numbering_offset)
        self.resize(500, 400)

    def create_table_bookmark(self, columns=3) -> None:
        del columns
        super().create_table_bookmark(columns=3)

        self.bookmark_table.cellClicked.connect(self.single_click)
        self.bookmark_table.cellDoubleClicked.connect(
            self.double_click)

    def single_click(self, row:int, column:int):
        """A single click occured

        Args:
            row (int): Row click occured
            column (int): Column click occured
        """
        del column
        self.selected_row = row
        self.delete_button.setEnabled(True)
        self.go_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.selected[BookmarkField.PAGE] = to_int(
            self.bookmark_table.item(row, self.COL_PAGE_BOOK).text())
        self.selected[BookmarkField.NAME] = self.bookmark_table.item(
            row, self.COL_NAME).text()

    def double_click(self, row:int, column:int):
        """A double click occured
        Perform a single click then act as if the
        'accept' bookmark button was pressed

        Args:
            row (int): Row click occured
            column (int): Column click occured
        """
        self.single_click(row, column)
        self._action_button_accepted()

    def _create_buttons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Open |
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Discard |
            QDialogButtonBox.Apply
        )
        self.buttons.clicked.connect(self._action_button_clicked)
        self.buttons.accepted.connect(self._action_button_accepted)
        self.buttons.rejected.connect(self._action_button_cancel)

        self.go_button = self.buttons.button(QDialogButtonBox.Open)
        self.go_button.setText('Go')
        self.go_button.setEnabled(False)

        self.delete_button = self.buttons.button(QDialogButtonBox.Discard)
        self.delete_button.setText("Delete")
        self.delete_button.setObjectName('Delete')
        self.delete_button.setEnabled(False)

        self.edit_button = self.buttons.button(QDialogButtonBox.Apply)
        self.edit_button.setText("Edit")
        self.edit_button.setObjectName("Edit")
        self.edit_button.setEnabled(False)

    def _action_button_clicked(self, button):
        if button.objectName() == 'Delete':
            self.action_ = self.action_file_delete
            self.return_select()
        if button.objectName() == 'Edit':
            self.action_ = self.action_Edit
            self.return_select()

    def _action_button_cancel(self):
        self.selected[BookmarkField.PAGE] = None
        self.reject()

    def _action_button_accepted(self):
        self.action_ = self.action_Go
        self.return_select()

    def return_select(self):
        """ If a bookmark was selected, return 'Accept'"""
        if self.selected[BookmarkField.PAGE]:
            self.accept()
        self.reject()

    def _format_page_item(self,
                          bookmark_name,
                          bookmark_page,
                          bookmark_relative=None,
                          protect_item: bool = False):
        name = TableItem(bookmark_name, protect_item)
        name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        page = TableItem(f"{bookmark_page:>6}", protect_item)
        page.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        if bookmark_relative is not None and bookmark_relative > 0:
            relative = TableItem("f{bookmark_relative:>6}")
        else:
            relative = TableItem(f"{0:>6}")
        relative.set_protected(protect_item)
        relative.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return (name, page, relative)

    def _insert_bookmark_entry(self, bookmark_item: list):
        row = self.bookmark_table.row_count()
        self.bookmark_table.insertRow(row)

        self.bookmark_table.setItem(row, self.COL_NAME, bookmark_item[0])
        self.bookmark_table.setItem(row, self.COL_PAGE_BOOK, bookmark_item[1])
        self.bookmark_table.setItem(row, self.COL_PAGE_SHOWN, bookmark_item[2])

    def setup_data(self, bookmark_list: list[dict], relative_offset: int = 0) -> bool:
        """ Setup bookmark data from a list of bookmarks"""
        if bookmark_list is None or len(bookmark_list) == 0:
            self.reject()
            return False
        self.clear()
        for bookmark in bookmark_list:
            self._insert_bookmark_entry(
                self._format_page_item(
                    bookmark[BookmarkField.NAME],
                    bookmark[BookmarkField.PAGE],
                    (None if relative_offset is None
                     else bookmark[BookmarkField.PAGE]-relative_offset+1)
                )
            )
        return True

    def clear(self) -> None:
        super().clear()
        self.selected[BookmarkField.PAGE] = None
        self.bookmark_table.setRowCount(0)

    def on_bookmark_selected(self) -> None:
        """ Placeholder - override """
        return None


if __name__ == "__main__":
    app = QApplication()
    window = UiBookmarkAdd()
    window.set_values("", "10", "")
    window.set_range(100, 10)
    window.show()
    app.exec()
    rtn = window.result()
    if rtn == UiBookmarkAdd.SAVE:
        print("... SAVE")
    if rtn == UiBookmarkAdd.SAVE_CONTINUE:
        print("... SAVE and CONTINUE")
    if rtn == UiBookmarkAdd.CANCEL:
        print("... CANCEL")
    sys.exit(0)
