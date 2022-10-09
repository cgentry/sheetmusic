# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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
import sqlite3
import unittest

from db.dbconn import DbConn
from db.setup import Setup
from db.dbsystem import DbSystem

class TestSystem( unittest.TestCase):
    def setUp(self):
        (self.conn, self.cursor) = DbConn().openDB(':memory:')
        self.setup = Setup(":memory:")
        self.setup.dropTables()
        self.setup.createTables()
        self.obj = DbSystem()
        

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
        self.assertEqual( 'myvalue', self.obj.setValue( key, 'myvalue', conflict="") )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

    def test_setValue_conflict(self):
        key = 'mykey'
        self.assertEqual( 'myvalue', self.obj.setValue( key, 'myvalue', conflict="") )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertRaises( sqlite3.IntegrityError, 
            self.obj.setValue, key, 'myvalue', None )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertRaises( sqlite3.IntegrityError, 
            self.obj.setValue, key, 'myvalue', 'FAIL' )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertRaises( sqlite3.IntegrityError, 
            self.obj.setValue, key, 'myvalue', DbSystem.SQL_SYSTEM_INSERT_FAIL )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

    def test_setValue_badparm(self):
        self.assertRaises( ValueError, 
            self.obj.setValue, 'mykey', 'myvalue', 'badparm' )

    def test_setValue_replace(self):
        key = 'mykey'
        self.assertEqual( 'myvalue', self.obj.setValue( key, 'myvalue', conflict=DbSystem.SQL_SYSTEM_INSERT_REPLACE) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertEqual( 'newvalue', self.obj.setValue( key, 'newvalue', conflict='replace') )
        self.assertEqual( 'newvalue', self.obj.getValue(key) )

    def test_setValue_ignore(self):
        key = 'mykey'
        self.assertEqual( 'myvalue', self.obj.setValue( key, 'myvalue', conflict="ignore") )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertEqual( 'myvalue', self.obj.setValue( key, 'newvalue', conflict=DbSystem.SQL_SYSTEM_INSERT_IGNORE) )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

    def test_setValue_delete(self):
        key = 'mykey'
        self.assertEqual( 'myvalue', self.obj.setValue( key, 'myvalue', conflict="ignore") )
        self.assertEqual( 'myvalue', self.obj.getValue(key) )

        self.assertEqual( None , self.obj.setValue( key ))
        self.assertEqual( None, self.obj.getValue(key) )

    def test_saveAll( self ):
        data = [
            { 'key': 'k1', 'value': 'v1'},
            { 'key': 'k2', 'value': 'v2'},
            { 'key': 'k3', 'value': 'v3'},
            { 'key': 'k4', 'value': 'v4'},
        ]
        self.obj.saveAll( data )
        rtnData = self.obj.getAll()
        self.assertEqual( len( rtnData ) , 4 )
        self.assertEqual( rtnData['k1'], 'v1')
        self.assertEqual( rtnData['k2'], 'v2')
        self.assertEqual( rtnData['k3'], 'v3')
        self.assertEqual( rtnData['k4'], 'v4')
        
if __name__ == "__main__":
    sys.path.append("../")
    unittest.main()


    
