"""
 User interface : PageNumber Widget

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import sys

from PySide6.QtWidgets import (
    QAbstractButton, QApplication, QCheckBox,
    QDialog, QDialogButtonBox,
    QGridLayout,
    QLabel, QLineEdit,
    QVBoxLayout, QWidget )

from util.convert import to_int
class PageNumber(QDialog):
    """
        PageNumber will display a 'go to page' window, prompting the
        user to enter a page number (absolute or relative)
    """
    def __init__(self, page=None, relative=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go To Page")

        layout = QVBoxLayout()
        layout.addWidget( self._create_grid(page,relative) )
        layout.addWidget( self.create_buttons() )
        self.setLayout( layout )

        self.page = page
        self.relative = relative


    def _create_grid( self, page:int, relative:bool) -> QGridLayout:
        widg = QWidget()
        grid = QGridLayout()

        lbl = QLabel()
        lbl.setText("Page number")
        grid.addWidget(lbl, 0, 0)

        self.page_number = QLineEdit()
        if page is not None:
            self.page_number.setText( str(page))
        grid.addWidget(self.page_number, 0,1)

        self.page_marker = QLabel()
        grid.addWidget(self.page_marker, 0, 2 )

        self.page_relative = QCheckBox()
        self.page_relative.setText("Use page numbering shown in book")
        self.page_relative.setChecked(relative)
        grid.addWidget( self.page_relative , 1,1)

        self.errorlabel = QLabel()
        grid.addWidget( self.errorlabel, 2,1)

        widg.setLayout( grid )

        return widg

    def verify( self ):
        """Check the page number field that has been entered
        """
        self.errorlabel.clear()
        self.page_marker.clear()
        self.page_number.setText( self.page_number.text().strip() )
        if self.page_number.text() == "" :
            self.errorlabel.setText("<b>Page number cannot be blank</b>")
        elif self.page_number.text().isnumeric() :
            self.accept()
            self.page = to_int( self.page_number.text(), self.page )
            self.relative = self.page_relative.isChecked()
        else:
            self.errorlabel.setText("<b>Page number must be numeric</b>")

    def action_button_clicked(self, button:QAbstractButton ):
        """ A button has been clicked.
            If it isn't cancel,  verify the field """
        if button.text() =='Cancel':
            self.reject()
        self.verify()

    def create_buttons(self) -> QDialogButtonBox:
        """Create a buttonbox containing OK and Cancel

        Returns:
            QDialogButtonBox: QT Standard button box
        """
        self.buttons = QDialogButtonBox()
        self.buttons.addButton( QDialogButtonBox.Cancel )
        self.buttons.addButton( QDialogButtonBox.Ok )
        #self.buttons.addButton( "Go", QDialogButtonBox.OkRole)
        self.buttons.clicked.connect(self.action_button_clicked)

        return self.buttons

if __name__ == "__main__":
    app = QApplication()
    window = PageNumber( )
    rtn = window.exec()

    sys.exit(app.exec())
