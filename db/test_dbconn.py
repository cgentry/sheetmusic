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
import unittest

sys.path.append("../")
from db.dbconn import DbConn

class TestDbConn( unittest.TestCase ):
    # def test_delete_handles( self):
    #     DbConn().openDB( close=True)

    # def test_empty_open(self):
    #     dh = DbConn()
    #     self.assertRaises( ValueError, dh.openDB, None)
    
    # def test_conn(self):
    #     dh = DbConn()
    #     conn = dh.connection(':memory:', trace=True)
    #     self.assertIsNotNone( conn,"Connection is 'none'!" )

    # def test_open_close(self):
    #     dh = DbConn()
    #     dh.openDB(close=True)
    #     self.assertRaises(ValueError, dh.openDB)

    # def test_bad_already_closed(self):
    #     dh = DbConn()
    #     dh.connection(':memory:')
    #     dh.conn.close()
    #     dh.closeDB()

    # def test_bad_close(self):
    #     dh = DbConn()
    #     dh.dbOpen(':memory:')
    #     dh.conn ='hi'
    #     dh.dbClose( close=True )

    def test_open_close_open(self):
        dh = DbConn()
        dh.closeDB( clear=True )
        self.assertRaises( ValueError , dh.openDB )

    def test_checkDbname(self):
        db = DbConn( ':memory:')
        self.assertTrue( db._checkDbName( 'dummyfile') )

    def test_openDb_different(self):
        import os
        dbname = './dummy.tdb'
        dh = DbConn()
        (conn1, curr1) = dh.dbHandle( dbname )
        self.assertEqual( dh.name() , dbname )
        (conn2, curr2) = dh.openDB(":memory:", trace=True)
        self.assertEqual( dh.name() , ':memory:')
        dh.dbHandle( close=True)

        try:
            os.remove( dbname )
        except:
            pass



        