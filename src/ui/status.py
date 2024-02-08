"""
User Interface : Status

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtWidgets import (
    QPushButton, QDialog, QGridLayout, QLayout,
    QDialogButtonBox, QApplication, QLabel, QProgressBar)
from PySide6.QtCore import Qt


class UiStatus(QDialog):
    """Simple wrapper on QDialog that lets us
    create simple, standard 'status' box to display information
    Used in toolconvert, simplifies and standardises output

    Contains these main elements:
        Heading
        Information
        Progress bar
        Cancel button

    Args:
        QDialog (object): QT Dialog box
    """
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(75)
        self.setMinimumWidth(500)
        self._cancel = False
        self._dlg = None

        main_layout = QGridLayout()
        self.lbl_heading = QLabel()
        self.lbl_information = QLabel()
        self.progress = QProgressBar()
        self.buttons = QDialogButtonBox()

        self._create_widgets(main_layout)
        self._create_buttons(main_layout)

        self.setLayout(main_layout)
        self.modal = True
        self.show()

    def _create_widgets(self, layout: QLayout):
        """ Create standard widgets for the dialog box """
        self.lbl_heading.setStyleSheet(
            'font-weight: bolder;text-align: center;')
        self.lbl_heading.setTextFormat(Qt.TextFormat.PlainText)

        self.lbl_information.setStyleSheet(
            'font-weight: bolder;text-align: center;')
        self.lbl_information.setTextFormat(Qt.TextFormat.PlainText)

        self.progress.setMinimum(0)
        self.progress.set_value(0)

        layout.addWidget(self.lbl_heading)
        layout.addWidget(self.lbl_information)
        layout.addWidget(self.progress)

    def _create_buttons(self, layout: QLayout) -> None:
        self.button = QPushButton('Cancel' )
        self.buttons.addButton(self.button, QDialogButtonBox.RejectRole)
        self.buttons.clicked.connect(self._close)
        layout.addWidget(self.buttons)

    @property
    def title(self) -> str:
        """ Return the header """
        return self.lbl_heading.text()

    @title.setter
    def title(self, title: str) -> None:
        """ Set dialog heading for dialog box """
        self.lbl_heading.setText(title)
        QApplication.processEvents()

    @property
    def information(self) -> str:
        """ Return current information """
        self.lbl_information.text()

    @information.setter
    def information(self, information: str) -> None:
        """ Set the information text """
        self.lbl_information.setText(information)
        QApplication.processEvents()

    @property
    def minimum(self) -> int:
        """ Return the minimum value for the progress bar"""
        return self.progress.minimum()

    @property
    def maximum(self) -> int:
        """Return the maximum value for the progress bar

        Returns:
            int: max of progress
        """
        return self.progress.maximum

    @minimum.setter
    def minimum(self, minimum: int = 0) -> None:
        self.progress.setMinimum(minimum)
        QApplication.processEvents()

    @maximum.setter
    def maximum(self, maximum: int) -> None:
        maximum = maximum \
            if self.progress.minimum() <= maximum \
                else self.progress.minimum()
        self.progress.setMaximum(maximum)
        QApplication.processEvents()

    @property
    def button_text(self) -> str:
        """Return the button text value

        Returns:
            str: Text value - default is 'Cancel'
        """
        return self.button.text()

    @button_text.setter
    def button_text(self, text: str):
        """Override default 'Cancel' for button

        Args:
            text (str): New text to display
        """
        self.button.setText(text)

    def set_range(self, minimum: int, maximum: int) -> None:
        """Set the minimum and max for the progress bar
        This is a convienence function and simply calls
        minimum() and maximum() setters

        Args:
            minimum (int): Lowest value (zero or more)
            maximum (int): Maximum value (greater than mnimum)
        """
        self.progress.setMinimum(minimum)
        self.progress.setMaximum(maximum)

    def set_value(self, value: int) -> None:
        """Set the progress bar position

        Args:
            value (int): Should be between min and max
        """
        self.progress.set_value(value)

    def clear(self) -> None:
        """ Clear the heading, information and set progress to zero"""
        self.lbl_heading.clear()
        self.lbl_information.clear()
        self.progress.set_value(0)
        QApplication.processEvents()

    def was_canceled(self) -> bool:
        """Was the cancel button pressed?

        Returns:
            bool: True if button pressed
        """
        return self._cancel

    def _close(self, button):
        """Flag the button was pressed.
        If the button text is 'Close', close the dialog

        Args:
            button (object): Button object ignored
        """
        del button
        self._cancel = True
        if self.button.text() == 'Close':
            self.close()
