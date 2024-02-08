"""
Testing program: This is just to test some items.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
####
#### TEST BED APPLICATION - doesn't really do anything
####
import sys

from PySide6.QtWidgets import QApplication
from qdb.setup import Setup
from qdb.dbconn import DbConn

from ui.file import Openfile
from qdil.preferences import SystemPreferences

if __name__ == "__main__":
    location = SystemPreferences().dbpath              # Fetch the system settings
    DbConn().open_db( location )                             # Open up the link to the database
    s = Setup(location)                                     # Make sure the database is initialised
    s.create_tables()
    s.init_data()

    app = QApplication()
    window = Openfile()
    window.exec()
    print("\nshow")
    print( window.bookSelected )
    app.quit()
    sys.exit(app.exec())
