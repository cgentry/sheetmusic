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


import unittest
import os

from db.dbconn import DbConn
from db.setup import Setup
from db.dbsystem import DbSystem
from db.dbgeneric import DbGenericName, DbTransform

class DummyData( DbGenericName ):
    def __init__(self):
        super().__init__()
        self.tableName='Genre'

class TestDbGeneric( unittest.TestCase ):
    def setUp(self):
        (self.conn, self.cursor) = DbConn().openDB(':memory:')
        self.sys = Setup(":memory:")
        self.sys.dropTables()
        self.sys.createTables()
        self.sys._initGenre()

    def tearDown(self):
        #self.sys.dropTables()
        pass

    def test_name(self):
        dh = DbConn()
        self.assertEqual( ':memory:', dh.name() )

    def test_getall_good_list( self ):
        rtn = DummyData().getall()
        self.assertEqual( len(rtn), 30)
        self.assertEqual( rtn[0], 'Alternative')
        self.assertEqual( rtn[1], 'Blues')
        self.assertEqual( rtn[2], 'Choral')
        self.assertEqual( rtn[3], 'Christmas')

    def test_init(self):
        dbname = './testgeneric.smdb'
        dh=DbConn(dbname)
        (conn, cursor )=dh.openDB()
        os.remove( dbname )

    def test_name(self):
        dh=DbConn()
        self.assertEqual( ':memory:', dh.name())
        dh.closeDB( True )
        self.assertIsNone( dh.name() )

        dh._setLocationName( ':memory:' )
        self.assertEqual( ':memory:', dh.name())

    def test_openDbBadValue(self):
        dh = DbConn()
        self.assertRaises( ValueError , dh.openDB,self )
        (conn, cursor ) = dh.closeDB( True)
        self.assertIsNone( conn )
        self.assertIsNone( cursor )
        self.assertRaises( ValueError , dh.openDB,self )

    def test_changeLocation(self):
        dh = DbConn()
        dh.closeDB( True )
        DbConn._sheet_db_location = self
        self.assertRaises( ValueError, dh.openDB, None )

    def test_openDbNoName(self):
        dh = DbConn()
        dh.closeDB( clear=True)
        (conn, cursor ) = dh.handles( )
        self.assertIsNone( conn )
        self.assertIsNone( cursor )
        self.assertRaises( ValueError , dh.openDB , None)

    def test_openDbNoName_closeConn(self):
        dh = DbConn()
        dh.closeDB( clear=True )
        conn = dh.connection( )
        self.assertIsNone( conn )
        self.assertRaises( ValueError , dh.openDB , None)