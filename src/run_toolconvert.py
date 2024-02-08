"""
Testing program: This just tests ToolConvert.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import sys
from PySide6.QtWidgets import QApplication
from qdil.book import DilBook
from qdil.preferences import SystemPreferences

from qdb.dbconn import DbConn
if __name__ == "__main__":
    syspref = SystemPreferences()
    dbLocation = syspref.dbpath
    mainDirectory = syspref.dbdirectory
    DbConn.open_db(dbLocation)

    app = QApplication()
    converter = DilBook()
    converter.import_book()
    app.quit()
    sys.exit(0)
