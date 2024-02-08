"""
Test frame: DilPreferences

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116
import unittest

from qdb.dbconn import DbConn
from qdb.setup import Setup
from qdb.keys import DbKeys
from qdil.preferences import DilPreferences

class TestSystem( unittest.TestCase):
    def setUp(self):
        DbConn.open_db(':memory:')
        self.setup = Setup(":memory:")
        self.setup.drop_tables()
        self.setup.create_tables()
        self.setup.init_data()
        self.obj = DilPreferences()

    def tearDown(self):
        self.setup.drop_tables()

    def test_get_value( self ):
        val = self.obj.get_value( DbKeys.SETTING_DEFAULT_SCRIPT)
        self.assertIsNotNone( val )
