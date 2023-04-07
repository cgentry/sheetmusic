# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file is part of Sheetmusic. 

# Sheetmusic is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        DbConn.openDB( dbfile )
        
        self.setup = Setup(dbfile)
        self.setup.dropTables()
        self.setup.createTables()
        self.obj = DbSystem()
        self.obj.showStack(False)
        self.obj.logger.setlevel( logging.CRITICAL )
        

    def tearDown(self):
        self.setup.dropTables()

    def test_getValue_noDefault(self):
        self.assertIsNone( self.obj.getValue('key'))
    
    def test_getValue_emptyKey(self):
        self.assertIsNone(self.obj.getValue(None))

    def test_getValue_with_default(self):
        self.assertEqual("DEFAULT", self.obj.getValue(None,'DEFAULT'))

    def test_setValue_nokey(self):
        self.assertRaises( ValueError,
            self.obj.setValue, None, 'hello')

    def test_setValue_set(self):
        key = 'mykey'
        self.assertTrue( self.obj.setValue( key, 'myvalue') , 'setValue')
        self.assertEqual( 'myvalue', self.obj.getValue(key), 'getValue' )

    def test_setValue_conflict(self):
        key = 'mykey'
        self.assertTrue( self.obj.setValue( key, 'myvalue') )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertFalse( self.obj.setValue( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertFalse( self.obj.setValue( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertFalse( self.obj.setValue( key, 'myvalue' ) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

    def test_setValue_replace(self):
        key = 'mykey'
        self.assertTrue( self.obj.setValue( key, 'myvalue', replace=True) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertTrue('newvalue', self.obj.setValue( key, 'newvalue', replace=True) )
        self.assertEqual( 'newvalue', self.obj.getValue(key) )

    def test_setValue_ignore(self):
        key = 'mykey'
        self.assertTrue( self.obj.setValue( key, 'myvalue', ignore=True) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

    def test_setValue_delete(self):
        key = 'mykey'
        self.assertTrue( self.obj.setValue( key, 'myvalue', ignore=True) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertTrue(self.obj.setValue( key ) )
        self.assertEqual( None, self.obj.getValue(key) )

    def test_saveAll_list( self ):
        data = [
            { 'key': 'k1', 'value': 'v1'},
            { 'key': 'k2', 'value': 'v2'},
            { 'key': 'k3', 'value': 'v3'},
            { 'key': 'k4', 'value': 'v4'},
        ]
        self.assertEqual( 4 , self.obj.saveAll( data ) )
        rtnData = self.obj.getAll()
        self.assertEqual( len( rtnData ) , 4 )
        self.assertEqual( rtnData['k1'], 'v1')
        self.assertEqual( rtnData['k2'], 'v2')
        self.assertEqual( rtnData['k3'], 'v3')
        self.assertEqual( rtnData['k4'], 'v4')

    def test_saveAll_dictionary( self ):
        data = {
            'K1': 'sall-1',
            'K2': 'sall-2',
            'K3': 'sall-3',
            'K4': 'sall-4',
        }
        self.assertEqual( 4, self.obj.saveAll( data ) )
        rtnData = self.obj.getAll()
        self.assertEqual( len( rtnData ) , 4 )
        self.assertEqual( rtnData['K1'], 'sall-1')
        self.assertEqual( rtnData['K2'], 'sall-2')
        self.assertEqual( rtnData['K3'], 'sall-3')
        self.assertEqual( rtnData['K4'], 'sall-4')

    def test_saveall_fail(self):
        with self.assertRaises( ValueError ) as cm:
            self.obj.saveAll( 'hello') 
        ex = cm.exception
        self.assertEqual( str(ex) , "saveAll: Invalid type passed '<class 'str'>'" )

if __name__ == "__main__":
    sys.path.append("../")
    unittest.main()


    
