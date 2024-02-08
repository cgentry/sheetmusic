"""
User Interface : Simple routines to display/control

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget


def center_on_screen( widget:QWidget):
    """Move the widget to the center of the screen

    Args:
        widget (QWidget): Widget to be centered.
    """
    center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    fg = widget.frameGeometry()
    fg.moveCenter(center)
    widget.move(fg.topLeft())
    ##
    widget.show()
