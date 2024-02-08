"""
User Interface : Module holds Validator, Properties and Property settings
    UI interfaces

 NOTE: There is some weird stuff with 3 pages. C++ deletes PxPageWidgets
 even when the references are just fine. There are some sloppy fixes to
 get around this. Sorry. I'll continue to try and change this.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import re
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QValidator
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit, QMessageBox,
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton, QCheckBox)

from qdb.keys import DbKeys
from qdb.mixin.fieldcleanup import MixinFieldCleanup
from qdb.fields.book import BookField
from qdb.dbbook import DbComposer, DbGenre
from qdb.dbbooksettings import DbBookSettings
from qdil.preferences import DilPreferences
from ui.edititem import UiGenericCombo
from util.convert import to_int, decode


class SimpleValidator(QValidator):
    """validation routines

    Args:
        QValidator (_type_): Base validator class

    """
    badChars = r'[?%\\|/\n\t\r]+'

    def validate(self, arg1: str, arg2):
        del arg2
        if len(arg1.strip()) == 0:
            return QValidator.Invalid
        if re.search(self.badChars, arg1) or arg1.startswith(' '):
            return QValidator.Invalid
        return QValidator.Acceptable


class UiProperties(MixinFieldCleanup, QDialog):
    '''
    This creates a simple grid and populates it with info from the Book
    Changes can be made and data will be returned if a change is made.
    '''
    bpData = 0
    bpLabel = 1

    btn_txt_ignore = 'Continue With No Changes'
    btn_txt_cancel = 'Cancel'
    btn_txt_apply = 'Apply Changes and Continue'

    pdf_options = {'Use System Setting': None,
                   'Image conversion': False, 'PDF Page render': True}
    pdf_values = {None: 'Use System Setting',
                  '0': 'Image conversion', '1': 'PDF Page render'}

    staticBookInformation = [
        [BookField.LOCATION,     'Book location'],
        [BookField.TOTAL_PAGES,   'Total pages'],
        [BookField.SOURCE,       'Original book source'],
        [BookField.DATE_ADDED,    'Date added'],
        [BookField.PDF_CREATED,   'PDF Creation date'],
        [BookField.FILE_CREATED,  'File date created'],
        [BookField.FILE_MODIFIED, 'File date modified'],
    ]

    def __init__(self, properties: dict = None, parent=None):
        super().__init__(parent)
        self._btn_text = None
        self._save_toml_file = None

        self.selected_property = None
        self.selected_page = None
        self.changes = None


        self.dbbooksettings = DbBookSettings()

        self.create_properties_table()
        self.create_buttons()
        main_layout = QGridLayout()
        main_layout.addWidget(self._properties_table, 3, 0, 1, 3)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)
        self.cleanup_level = decode(
            code=DbKeys.ENCODE_INT,
            value=DilPreferences().get_value(
                key=DbKeys.SETTING_NAME_IMPORT,
                default=DbKeys.VALUE_NAME_IMPORT_FILE_0)
        )
        self.resize(700, 500)
        if properties:
            self.set_properties(properties)

    def clear(self):
        """ clear will remove all content from the QTable and reset counters"""
        self._properties_table.clear()
        self._properties_table.horizontalHeader().hide()
        self.selected_property = None
        self.selected_page = None
        self._properties_table.setRowCount(0)
        self.changes = {}
        # self._flag_changed = False
        self.default_button()

    def create_properties_table(self):
        """ Create a table widget and fill in headers """
        self._properties_table = QTableWidget()
        self._properties_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._properties_table.setColumnCount(1)
        self._properties_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self._properties_table.setShowGrid(True)
        self._properties_table.setDisabled(False)

    def add_buttons(self) -> None:
        """ OVERRIDE: Add additional buttons here. """
        return None

    def create_buttons(self):
        """ Create standard buttons dialog """
        self.btn_skip = QPushButton(self.btn_txt_ignore)
        self.btn_apply = QPushButton(self.btn_txt_apply)
        self.btn_cancel = QPushButton(self.btn_txt_cancel)
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.btn_skip, QDialogButtonBox.ResetRole)
        self.buttons.addButton(self.btn_apply, QDialogButtonBox.YesRole)
        self.buttons.addButton(self.btn_cancel, QDialogButtonBox.RejectRole)
        self.buttons.clicked.connect(self.button_clicked)
        self.add_buttons()

    def button_default_action(self):
        """ To extend button action, override and self._btn_text """
        self.accept()

    def button_clicked(self, btn):
        """ Called whenever a button is clicked on dialog"""
        self._btn_text = btn.text()
        if self._btn_text == self.btn_txt_ignore:
            self.changes = {}
            self.accept()
        elif self._btn_text == self.btn_txt_cancel:
            self.changes = {}
            self.reject()
        else:
            self.button_default_action()

    def is_reject(self) -> bool:
        """ determine if result is Rejected """
        return self.result() == self.DialogCode.Rejected

    def is_skip(self) -> bool:
        """ Return True if no chnanges, but pressed 'accepted' """
        return self.result() == self.DialogCode.Accepted and len(self.changes) == 0

    def is_apply(self) -> bool:
        """ Return True if changes and pressed accepted """
        return self.result() == self.DialogCode.Accepted and len(self.changes) > 0

    def _format_static_property(self, label: str, value, is_mustable: bool):
        header_w = QTableWidgetItem(str(label))
        page_w = QTableWidgetItem(str(value))
        if is_mustable:
            page_w.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
        else:
            page_w.setFlags(Qt.NoItemFlags)
        return (header_w, page_w)

    def _insert_property_entry(self, new_row: list):
        """Insert a row into the book's property table

        Args:
            new_row (list): [0] name, [1] Value
        """
        row = self._properties_table.row_count()
        self._properties_table.insertRow(row)
        self._properties_table.setVerticalHeaderItem(row, new_row[0])
        if isinstance(new_row[1],  QTableWidgetItem):
            self._properties_table.setItem(row, 0, new_row[1])
        else:
            self._properties_table.setCellWidget(row, 0, new_row[1])

    def default_button(self):
        """ If there are changes, activate buttons """
        apply = len(self.changes) > 0
        self.btn_apply.setDefault(apply)
        self.btn_apply.setEnabled(apply)
        self.btn_skip.setDefault((not apply))

    def changed_name(self, value):
        """ Mark name as changed """
        self.changes[BookField.NAME] = self.clean_field_value(value)
        self.default_button()

    def validate_page(self, value) -> bool:
        """ Check page number is valid """
        value = value.strip()
        i = to_int(value, -1)
        if value == '' or ( 0 >= i < 1000):
            return True
        QMessageBox.warning(self, 'Invalid Value',
                            'Page number must be 0 to 999')
        return False

    def changed_start(self, value):
        """ Mark start number changed """
        if self.validate_page(value):
            self.changes[BookField.NUMBER_STARTS] = to_int(value, 0)
            self.default_button()

    def changed_end(self, value):
        """ Mark ending number changed """
        if self.validate_page(value):
            self.changes[BookField.NUMBER_ENDS] = to_int(value, 0)
            self.default_button()

    def changed_link(self, value):
        """ Link text changed """
        self.changes[BookField.LINK] = value.strip()
        self.default_button()

    def changed_author(self, value):
        """ Author text changed """
        self.changes[BookField.AUTHOR] = value.strip()
        self.default_button()

    def changed_composer(self, value):
        """ Composer changed """
        self.changes[BookField.COMPOSER] = value.strip()
        self.default_button()

    def changed_genre(self, value):
        """ Genre text changed """
        self.changes[BookField.GENRE] = value.strip()
        self.default_button()

    def change_render(self, value):
        """ Render value changed """
        value = value.strip()
        self.changes[DbKeys.SETTING_RENDER_PDF] = UiProperties.pdf_options.get(
            value)
        self.default_button()

    def _named_property(self,
            label: str,
            musicbook: dict,
            value_key: str,
            on_change,
            key_is_int: bool = False,
            cleanup: bool = True,
            readonly: bool = False):
        """
        Create a named edit element for a table

        Args:
            label (str):
                Label to show for edit field
            musicbook (dict):
                Dictionary holding key/values for editing
            value_key (str):
                key in musicbook dictionary
            on_change (_type_):
                function to call when change occurs
            key_is_int (bool, optional):
                If key is an integer.
                Defaults to False.
            cleanup (bool, optional):
                Apply cleanup routine to element
                Defaults to True.
            readonly (bool, optional):
                True if it is read only.
                Defaults to False.
        """
        name = QLineEdit()
        if key_is_int:
            value = str(musicbook[value_key] if value_key in musicbook else 1)
        else:
            if value_key not in musicbook or musicbook[value_key] is None:
                musicbook[value_key] = ''
                value = ''
            else:
                if cleanup:
                    value = self.clean_field_value(str(musicbook[value_key]))
                else:
                    value = self.remove_ctrl_char(str(musicbook[value_key]))
        name.setText(value)
        if key_is_int:
            name.setValidator(QIntValidator(0, 999, self))
        else:
            name.setValidator(SimpleValidator())
        name.setReadOnly(readonly)
        name.setObjectName(value_key)
        name.textEdited.connect(on_change)
        self._insert_property_entry([QTableWidgetItem(label), name])

    def _combo_property_value(self, label: str, datasource,  current_entry, change_function):
        """ Create a combo (dropdown) option list based on a db entry and list"""
        gcmb = UiGenericCombo(True, datasource, current_entry, label)
        gcmb.currentTextChanged.connect(change_function)
        self._insert_property_entry([QTableWidgetItem(label), gcmb])

    def _combo_property(self,
                label: str,
                dbentry,
                musicbook: dict,
                value_key: str,
                on_change):
        """ Create a combo (dropdown) option list based on a db entry and list"""
        current_value = (str(musicbook[value_key])
                        if value_key in musicbook else 'Unknown')
        self._combo_property_value(label, dbentry, current_value, on_change)

    def _checkbox_property(self, label: str, ischecked: bool, on_change):
        cbox = QCheckBox()
        cbox.setText(label)
        cbox.setCheckable(True)
        cbox.setChecked(ischecked)
        cbox.stateChanged.connect(on_change)
        self._insert_property_entry([QTableWidgetItem(''), cbox])

    def add_additional_properties(self) -> None:
        """ OVERRIDE: To extend the editable rows, use this hook """
        return None

    def add_additional_static_properties(self) -> None:
        """ OVERRIDE: To extend the static rows, use this hook """
        return None

    def _add_source_type(self, musicbook: dict):
        """ Figure out what type of entry we have (PDF or PNG)
            display options based upon that
        """
        label = 'Book Display Using'
        if not os.path.exists(musicbook[BookField.LOCATION]):
            self._insert_property_entry(self._format_static_property(
                label, '(Book not found)', False))
            return

        if os.path.isdir(musicbook[BookField.LOCATION]):
            self._insert_property_entry(self._format_static_property(
                label, 'PNG (image files)', False))
            return

        pdf_render = self.dbbooksettings.get_setting(
            musicbook[BookField.ID],
            DbKeys.SETTING_RENDER_PDF,
            fallback=False, raw=True)
        current_entry = UiProperties.pdf_values[pdf_render]
        self._combo_property_value(
            label, UiProperties.pdf_options, current_entry, self.changeRender)

    def get_changes(self) -> dict:
        """ get the properties that have changed """
        return self.changes

    def set_properties(self, musicbook: dict):
        """
        musicbook is the database row for the book which can be indexed
        by name. We pick out the names and put them into the table.
        """
        self.setModal(True)
        self.setWindowTitle("Book properties for " + musicbook[BookField.NAME])

        self.clear()

        self._named_property('Book name', musicbook,
                           BookField.NAME, self.changed_name)

        self._combo_property('Composer', DbComposer(), musicbook,
                            BookField.COMPOSER, self.changed_composer)
        self._combo_property('Genre', DbGenre(),    musicbook,
                            BookField.GENRE,    self.changed_genre)

        self._named_property('Offset to page 1', musicbook,
                           BookField.NUMBER_STARTS, self.changed_start, key_is_int=True)
        self._named_property('Last page number', musicbook,
                           BookField.NUMBER_ENDS,   self.changed_end,  key_is_int=True)
        self._named_property('Web Link',         musicbook, BookField.LINK,
                           self.changed_link,  key_is_int=False, cleanup=False)
        self._named_property('Author',          musicbook, BookField.AUTHOR,
                           self.changed_author, key_is_int=False, cleanup=False)
        self.add_additional_properties()

        self._add_source_type(musicbook)
        for prop in self.staticBookInformation:
            data = musicbook[prop[self.bpData]
                             ] if prop[self.bpData] in musicbook else "(no data)"

            table_entry = self._format_static_property(
                prop[self.bpLabel],
                data,
                False,
            )
            self._insert_property_entry(table_entry)
        self.add_additional_static_properties()
        self._properties_table.resizeColumnsToContents()

        # self.adjustSize(  )


class UiPropertiesImages(UiProperties):
    """ Property images extends the Properties to provide a checkbox for saving TOML informatin"""

    def save_toml_file(self) -> bool:
        """ Return the state of saving the toml file """
        return self._save_toml_file

    def add_additional_properties(self):
        """ Additional properties have been set """
        self._save_toml_file = True
        self._checkbox_property('Save properties in file',
                               True, self.checkbox_changed)

    def checkbox_changed(self, state):
        """ set the toml file state """
        self._save_toml_file = state
