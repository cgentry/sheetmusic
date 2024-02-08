"""
Testing program: This is just to test some modules.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import sys
from PySide6.QtWidgets  import QApplication
from ui.selectitems     import SelectItems


if __name__ == "__main__":
    lst = { "Entry one": "value1", "Entry two": "value2"}
    app = QApplication()
    sim = SelectItems("Books already processed","Select books you want to re-process")
    sim.set_data( lst )
    sim.set_button_text("OK","Ignore")
    sim.exec()
    print( "Checked:"   ,sim.get_checked_list() )
    print( "Unchecked:", sim.get_unchecked_list() )

    print("\nTest two")
    sim.set_data( ['List1', 'List2', 'List3'])
    sim.set_button_text("OK","Ignore")
    sim.exec()
    print( "Checked:"   ,sim.get_checked_list() )
    print( "Unchecked:", sim.get_unchecked_list() )

    print("\nTest three")
    sim.clear_data()
    sim.set_data( ['List1', 'List2', 'List3'])
    sim.set_button_text("OK","Ignore")
    sim.exec()
    print( "Checked:"   ,sim.get_checked_list() )
    print( "Unchecked:", sim.get_unchecked_list() )

    app.quit()
    sys.exit(0)
