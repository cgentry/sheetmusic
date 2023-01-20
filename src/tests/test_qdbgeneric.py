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
import logging

from qdb.dbconn     import DbConn
from qdb.setup      import Setup
from qdb.dbsystem   import DbSystem
from qdb.dbgeneric  import DbGenericName

class DummyData( DbGenericName ):
    def __init__(self):
        super().__init__(table='Genre')
        self.tableName = 'Genre'
        self.setupLogger()

class TestDbGeneric( unittest.TestCase ):
    def setUp(self):
        DbConn().openDB(':memory:')
        self.sys = Setup(":memory:")
        self.sys.dropTables()
        self.sys.createTables()
        self.sys.initGenre()
        self.dummy = DummyData()
        self.dummy.logger.setLevel( logging.CRITICAL )

    def tearDown(self):
        #self.sys.dropTables()
        pass

    def test_getall_good_list( self ):
        rtn = self.dummy.getall()
        self.assertEqual( len(rtn), 30)
        self.assertEqual( rtn[0], 'Alternative')
        self.assertEqual( rtn[1], 'Blues')
        self.assertEqual( rtn[2], 'Choral')
        self.assertEqual( rtn[3], 'Christmas')

    def test_hash(self):
        self.assertTrue( self.dummy.has( 'Blues') )

    def test_getid( self ):
        self.assertEqual( self.dummy.getID( 'Blues'),  5 )
        self.assertEqual( self.dummy.getID( 'Choral'), 7 )
