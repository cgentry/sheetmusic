"""
Test frame: System

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import sys
import unittest
import logging

from qdb.dbconn import DbConn
from qdb.setup import Setup
from qdb.dbsystem import DbSystem

class TestSystem( unittest.TestCase):
    def setUp(self):
        dbfile = '/tmp/test.sql'
        # dbfile = ':memory:'
        DbConn.open_db( dbfile )

        self.setup = Setup(dbfile)
        self.setup.drop_tables()
        self.setup.create_tables()
        self.obj = DbSystem()
        self.obj.show_stack(False)
        self.obj.logger.setlevel( logging.CRITICAL )


    def tearDown(self):
        self.setup.drop_tables()

    def test_get_value_no_default(self):
        self.assertIsNone( self.obj.get_value('key'))

    def test_get_value_empty_key(self):
        self.assertIsNone(self.obj.get_value(None))

    def test_get_value_with_default(self):
        self.assertEqual("DEFAULT", self.obj.get_value(None,'DEFAULT'))

    def test_set_value_nokey(self):
        self.assertRaises( ValueError,
            self.obj.set_value, None, 'hello')

    def test_set_value_set(self):
        key = 'mykey'
        self.assertTrue( self.obj.set_value( key, 'myvalue') , 'set_value')
        self.assertEqual( 'myvalue', self.obj.get_value(key), 'get_value' )

    def test_set_value_conflict(self):
        key = 'mykey'
        self.assertTrue( self.obj.set_value( key, 'myvalue') )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

        self.assertFalse( self.obj.set_value( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

        self.assertFalse( self.obj.set_value( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

        self.assertFalse( self.obj.set_value( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

    def test_set_value_replace(self):
        key = 'mykey'
        self.assertTrue( self.obj.set_value( key, 'myvalue', replace=True) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

        self.assertTrue(self.obj.set_value( key, 'newvalue', replace=True) )
        self.assertEqual( 'newvalue', self.obj.get_value(key) )

    def test_set_value_ignore(self):
        key = 'mykey'
        self.assertTrue( self.obj.set_value( key, 'myvalue', ignore=True) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

    def test_set_value_delete(self):
        key = 'mykey'
        self.assertTrue( self.obj.set_value( key, 'myvalue', ignore=True) )
        self.assertEqual( 'myvalue', self.obj.get_value(key) )

        self.assertTrue(self.obj.set_value( key ) )
        self.assertEqual( None, self.obj.get_value(key) )

    def test_save_all_list( self ):
        data = [
            { 'key': 'k1', 'value': 'v1'},
            { 'key': 'k2', 'value': 'v2'},
            { 'key': 'k3', 'value': 'v3'},
            { 'key': 'k4', 'value': 'v4'},
        ]
        self.assertEqual( 4 , self.obj.save_all( data ) )
        rtn_data = self.obj.get_all()
        self.assertEqual( len( rtn_data ) , 4 )
        self.assertEqual( rtn_data['k1'], 'v1')
        self.assertEqual( rtn_data['k2'], 'v2')
        self.assertEqual( rtn_data['k3'], 'v3')
        self.assertEqual( rtn_data['k4'], 'v4')

    def test_save_all_dictionary( self ):
        data = {
            'K1': 'sall-1',
            'K2': 'sall-2',
            'K3': 'sall-3',
            'K4': 'sall-4',
        }
        self.assertEqual( 4, self.obj.save_all( data ) )
        rtn_data = self.obj.get_all()
        self.assertEqual( len( rtn_data ) , 4 )
        self.assertEqual( rtn_data['K1'], 'sall-1')
        self.assertEqual( rtn_data['K2'], 'sall-2')
        self.assertEqual( rtn_data['K3'], 'sall-3')
        self.assertEqual( rtn_data['K4'], 'sall-4')

    def test_saveall_fail(self):
        with self.assertRaises( ValueError ) as cm:
            self.obj.save_all( 'hello')
        ex = cm.exception
        self.assertEqual( str(ex) , "saveAll: Invalid type passed '<class 'str'>'" )

if __name__ == "__main__":
    sys.path.append("../")
    unittest.main()
