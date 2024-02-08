"""
 User interface : SelectItems widget

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""


from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,  QPushButton, QLabel,
    QListWidget,       QListWidgetItem,  QVBoxLayout
)
from PySide6.QtCore import Qt


class SelectItems(QDialog):
    """Select Items from a dropdown list in a dialog box

    Args:
        QDialog (QDialog): Class extends QDialog
    """
    YES = 0
    NO = 1
    TOGGLE = 2

    SELECT_ALL = 'Select All'
    REJECT_ALL = 'Ignore All'

    def __init__(self, title: str = None, heading: str = None):
        super().__init__()
        self._btns = [QPushButton('Yes'),
                      QPushButton('No'),
                      QPushButton(self.SELECT_ALL)]
        self._action_was_rejected = False
        self.data = {}
        self.total_selected = 0
        self.button_box = QDialogButtonBox()

        self.set_dialog(
            self._create_title(title),
            self._create_list(),
            self._create_button_box())

        if title is not None:
            self.setWindowTitle(title)
        self.set_heading(heading)
        self.resize(600, 500)


    def _set_toggle(self, count: bool = False):
        """Toggle the Select button text

        Args:
            count (bool, optional): force a recount.
                Defaults to False.
        """
        if count:
            self._any_selected()
        if self.total_selected == self.check_list.count():
            self._btns[self.TOGGLE].setText(self.REJECT_ALL)
        else:
            self._btns[self.TOGGLE].setText(self.SELECT_ALL)

    def _set_ok( self ):
        ok_state = self.total_selected > 0
        self._btns[ self.YES ].setEnabled( ok_state )

    def _any_selected(self) -> bool:
        """Check and tally the number of boxes checked

        Returns:
            bool: True if any are selected
        """
        self.total_selected = 0
        for row in range(0, self.check_list.count()):
            if self.check_list.item(row).checkState() == Qt.Checked:
                self.total_selected += 1
        return self.total_selected > 0

    def _action_accepted(self):
        """ They hit OK """
        self._action_was_rejected = False
        self.accept()

    def _action_rejected(self):
        """ They hit the IGNORE button"""
        self._action_was_rejected = True
        self.reject()

    def _action_toggle(self):
        """They hit the toggle button. We need to flip the state
        of all the check items and enable/disable the OK button.
        """

        select = self._btns[self.TOGGLE].text() == self.SELECT_ALL
        new_state = Qt.Checked if select else Qt.Unchecked
        self.total_selected = self.check_list.count() if select else 0

        for row in range(0, self.check_list.count()):
            if self.check_list.item(row).checkState() != new_state:
                self.check_list.item(row).setCheckState(new_state)

        self._set_ok()
        self._set_toggle(False)

    def _action_selected(self, item: QListWidgetItem):
        """Save the state of the item that has changed

        Args:
            item (QListWidgetItem): Button state changed
        """
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.total_selected += -1
        else:
            item.setCheckState(Qt.Checked)
            self.total_selected += 1
        self._btns[self.YES].setEnabled(self.total_selected > 0)
        item.setSelected(False)

        self._set_ok()
        self._set_toggle()

    def _create_title(self, heading: str = None) -> QLabel:
        """Create a qlabel and apply as the heading for dialog

        Args:
            heading (str, optional): Text for heading. Defaults to None.

        Returns:
            QLabel: _description_
        """
        self.lbl_heading = QLabel()
        self.set_heading(heading)
        return self.lbl_heading

    def _create_list(self) -> QListWidget:
        """Create a list widget and connect it to _action_selected
        Returns an object that will contain a list of names the user adds
        Actions are connected to _action_selected method

        Returns:
            QListWidget: Qt List widget
        """
        self.check_list = QListWidget()
        self.check_list.itemClicked.connect(self._action_selected)
        return self.check_list

    def _create_button_box(self) -> QDialogButtonBox:
        """ Create a button box with 'Yes', No, Select All """

        self.button_box.addButton(
            self._btns[self.YES], QDialogButtonBox.AcceptRole)
        self.button_box.addButton(
            self._btns[self.NO], QDialogButtonBox.RejectRole)
        self.button_box.addButton(
            self._btns[self.TOGGLE], QDialogButtonBox.HelpRole)

        self.button_box.accepted.connect(self._action_accepted)
        self.button_box.rejected.connect(self._action_rejected)
        self.button_box.helpRequested.connect(self._action_toggle)

        return self.button_box

    def _widget_from_datum(self, label) -> QListWidgetItem:
        """ Private: Create a widget item and label"""
        lim = QListWidgetItem()
        lim.setText(label)
        lim.setFlags(Qt.ItemIsUserCheckable |
                     Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        lim.setCheckState(Qt.Unchecked)

        return lim

    def _from_list(self, data: list):
        """Convert the list to a dictionary and set the checklist

        Args:
            data (list): _description_
        """
        self._from_dict( dict( zip( data , data ) ) )

    def _from_dict(self, dictionary: dict):
        index = self.check_list.count()
        for key, value in dictionary.items():
            self.data[index] = value
            self.check_list.addItem(self._widget_from_datum(key))
            index = index+1
        self.total_selected = 0
        self._set_toggle()
        return dictionary

    def _get_items_bystate(self, select_type: Qt.CheckState) -> dict:
        """Return a dictionary of all the items matching select_type

        Args:
            select_type (Qt.CheckState): Qt.Checked or Qt.Unchecked

        Returns:
            dict: [ display text : data ]
        """
        rtn_list = {}
        for i in range(0, self.check_list.count()):
            item = self.check_list.item(i)
            if item.checkState() == select_type:
                rtn_list[item.text()] = self.data[i]
        return rtn_list

    def set_dialog(self, *args):
        """ Set dialog layout and widget elements"""
        self._dialog_layout = QVBoxLayout()
        for element in args:
            self._dialog_layout.addWidget(element)
        self.setLayout(self._dialog_layout)

    def set_heading(self, heading: str = None) -> None:
        """ Set the heading text to string passed"""
        if heading:
            self.lbl_heading.setText(heading)

    def set_button_text(self, btn_yes: str = 'Yes', btn_no: str = 'No'):
        """ Set the button text for Yes and Now.
            Disable the 'yes' button
        """
        self._btns[self.YES].setText(btn_yes)
        self._btns[self.NO].setText(btn_no)
        self._btns[self.YES].setEnabled(False)

    def set_data(self, data: dict | list):
        """Fill in the combo box from either a dictionary or a simple list
            Data that is checked will be returned in 'data_list' as both key
            and data
            Dictionaries are { display_data : return_value }

        Args:
            data (dict | list):
                dict are { display_data : return_value }
                list: [ display, display, display... ]
        """
        if isinstance(data, dict):
            self._from_dict(data)
        else:
            self._from_list(data)

    def clear_data(self):
        """Clear and reset the checkbox dialog
        """
        self.data = {}
        self.total_selected = 0
        self.check_list.clear()

    def set_checked_list(self, value: bool):
        """Set all checked values to the value passed

        Args:
            value (bool): True or False
        """
        state = Qt.Checked if value else Qt.UnChecked
        for row in range(self.check_list.count()):
            self.check_list.item(row).setCheckState(state)
        self.total_selected = \
            self.check_list.count() if value else 0
        self._set_toggle()

    def get_data_list(self) -> dict:
        """Return a dictionary containing key->data from checklist

        Returns:
            dict: Dictionary of "Check list name" : data
        """
        data_list = {}
        for i in range(0, self.check_list.count()):
            data_list[self.check_list.item(i).text()] = self.data[i]
        return data_list

    def get_checked_list(self) -> dict:
        """Return a list of all checked items
        If 'reject' button was pressed an empty dictionary returned

        Returns:
            dict: text label : value
        """
        if self._action_was_rejected:
            return {}

        return self._get_items_bystate(Qt.Checked)

    def get_unchecked_list(self) -> dict:
        """Return a list of all unchecked values

        Returns:
            dict: text : value
        """
        if self._action_was_rejected:
            return self.get_data_list()
        return self._get_items_bystate(Qt.Unchecked)

    def get_checked_listvalues(self) -> list:
        """ This returns just the values - the full paths - of items selected"""
        return list(self._get_items_bystate(Qt.Checked).values())
