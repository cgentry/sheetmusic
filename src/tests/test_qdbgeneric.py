"""
Test frame: DbGeneric

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import unittest
import logging

from qdb.dbconn     import DbConn
from qdb.setup      import Setup
from qdb.dbgeneric  import DbGenericName

class DummyData( DbGenericName ):
    def __init__(self):
        super().__init__(table='Genre')
        self.table_name = 'Genre'
        self.setup_logger()

class TestDbGeneric( unittest.TestCase ):
    def setUp(self):
        DbConn().open_db(':memory:')
        self.sys = Setup(":memory:")
        self.sys.drop_tables()
        self.sys.create_tables()
        self.sys.init_genre()
        self.dummy = DummyData()
        self.dummy.logger.setlevel( logging.CRITICAL )

    def tearDown(self):
        #self.sys.drop_tables()
        pass

    def test_getall_good_list( self ):
        rtn = self.dummy.get_all()
        self.assertEqual( len(rtn), 30)
        self.assertEqual( rtn[0], 'Alternative')
        self.assertEqual( rtn[1], 'Blues')
        self.assertEqual( rtn[2], 'Choral')
        self.assertEqual( rtn[3], 'Christmas')

    def test_hash(self):
        self.assertTrue( self.dummy.has( 'Blues') )

    def test_getid( self ):
        self.assertEqual( self.dummy.get_id( 'Blues'),  5 )
        self.assertEqual( self.dummy.get_id( 'Choral'), 7 )
