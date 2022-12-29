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
import site
import os
import unittest

sys.path.append("../")
from qdb.dbconn         import DbConn
from PySide6.QtSql      import QSqlDatabase, QSqlQuery
from qdb.keys           import DbKeys

class TestDbConn( unittest.TestCase ):

    @classmethod
    def setUpClass(cls):
        pass

    # def test_delete_handles( self):
    #     DbConn().openDB( close=True)
    
    def test_open_close(self):
        DbConn.openDB(':memory:')
        DbConn.closeDB()
        db = DbConn.openDB()
        self.assertIsNotNone( db )
        self.assertTrue( DbConn.isOpen() )
        self.assertEqual( DbKeys.VALUE_DEFAULT_DB_FILENAME, DbConn.name() )

    def test_bad_close(self):
        DbConn.openDB(':memory:')
        self.assertTrue( DbConn.isOpen() )
        DbConn._qdb_conn = None
        DbConn.closeDB()
        DbConn.closeDB()
        db = DbConn.openDB()
        self.assertIsNotNone( db )
        self.assertTrue( DbConn.isOpen() )
        self.assertEqual( DbKeys.VALUE_DEFAULT_DB_FILENAME, DbConn.name() )

    def test_open_close_open(self): 

        sql = DbConn.openDB(':memory:')
        self.assertIsInstance( sql , QSqlDatabase )
        self.assertTrue( DbConn.isOpen() )

        query = QSqlQuery( DbConn.db() )
        self.assertIsInstance( query, QSqlQuery, type(query))
        query.clear()
        query.finish()
        

    def test_checkDbname(self):
        DbConn.openDB(':memory:')
        self.assertEqual( DbConn.name()   , DbKeys.VALUE_DEFAULT_DB_FILENAME)
        self.assertEqual( DbConn.dbname() , ':memory:')
        DbConn.destroyConnection()
        self.assertIsNone( DbConn.name() )

    def test_connecection(self):
        DbConn.closeDB()
        self.assertEqual( None, DbConn.getConnection() )
        DbConn.destroyConnection()

    def test_open_close_reopen(self):
        DbConn.openDB(':memory:')
        self.assertTrue( DbConn.isOpen() )
        DbConn.closeDB()
        self.assertFalse( DbConn.isOpen())
        DbConn.reopenDB()
        self.assertTrue( DbConn.isOpen())
        DbConn.destroyConnection()

    def test_double_close(self):
        DbConn.openDB(':memory:')
        self.assertTrue( DbConn.isOpen() )
        DbConn.closeDB()
        self.assertFalse( DbConn.isOpen())
        DbConn.closeDB()
        self.assertFalse( DbConn.isOpen())
        DbConn.closeDB()

    def test_destroy(self):
        DbConn.openDB(':memory:')
        self.assertTrue( DbConn.isOpen() )
        DbConn.closeDB()
        self.assertFalse( DbConn.isOpen())
        self.assertEqual( DbConn.dbname() , ':memory:')
        DbConn.destroyConnection()

    def test_cursor(self):
        DbConn.openDB(':memory:')

        self.assertTrue( DbConn.isOpen() )
        self.assertTrue( DbConn.isValid( open=True) )
        query = QSqlQuery( DbConn.db() )
        self.assertIsInstance( query , QSqlQuery )
        query.prepare( 'SELECT 1 AS number;')
        self.assertTrue ( query.exec() )
        self.assertTrue( query.next() )

        self.assertEqual( 1 , query.value(0))
        query.finish()
        query.clear()
        del query


 

        