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
#
import unittest
import os.path

from qdb.dbconn     import DbConn
from qdb.setup      import Setup
from qdb.dbsystem   import DbSystem
from qdb.keys       import DbKeys
from PySide6.QtSql  import QSqlQuery

class TestSetup( unittest.TestCase):
    sql_get_tablenames="""
            SELECT count(*)
            FROM sqlite_schema
            WHERE type ='table' 
            AND name NOT LIKE 'sqlite_%';"""
    sql_get_viewnames="""
            SELECT count(*)
            FROM sqlite_schema
            WHERE type ='view' 
            AND name NOT LIKE 'sqlite_%';"""

    sql_get_genre="""
            SELECT id, name
            FROM Genre
            ORDER BY id ASC
            """
    sql_get_composer="""
            SELECT id, name
            FROM Composer
            ORDER BY id ASC
            """
    sql_count_composer="""SELECT COUNT(*) FROM Composer"""

    sql_get_system="""
            SELECT key, value
            FROM System
            ORDER BY key
        """

    def setUp(self):
        db = DbConn().openDB(':memory:')
        self.setup = Setup(":memory:")
        self.setup.dropTables()
        self.query = QSqlQuery( db )

    def test_createTables(self):
        self.assertTrue( self.query.exec(self.sql_get_tablenames) )
        self.assertTrue( self.query.next() )
        self.assertEqual( 0, self.query.value(0))
        self.query.finish()

        self.assertTrue( self.query.exec(self.sql_get_viewnames) )
        self.query.next()
        self.assertEqual( 0, self.query.value(0))
        self.query.finish()

        self.setup.createTables()

        self.assertTrue( self.query.exec(self.sql_get_viewnames) )
        self.query.next()
        self.assertEqual( 3, self.query.value(0),"Number of views")
        self.query.finish()

        self.assertTrue( self.query.exec(self.sql_get_tablenames) )
        self.query.next()
        self.assertEqual( 7, self.query.value(0))
        self.query.finish()

    def test_dropTables(self):
        self.setup.createTables()
        self.setup.dropTables()

        self.assertTrue( self.query.exec(self.sql_get_tablenames) )
        self.assertTrue( self.query.next() )
        self.assertEqual( 0, self.query.value(0))
        self.query.finish()

        self.assertTrue( self.query.exec(self.sql_get_viewnames) )
        self.query.next()
        self.assertEqual( 0, self.query.value(0))
        self.query.finish()

    def test_initGenre(self):
        self.setup.createTables()
        self.assertTrue( self.setup.initGenre() )
        self.assertTrue( self.query.exec( self.sql_get_genre ) )

        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 1 )
        self.assertEqual( self.query.value(1) , 'Unknown')

        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 2 )
        self.assertEqual( self.query.value(1) , 'Various')

        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 3 )
        self.assertEqual( self.query.value(1) , 'Teaching')
    
        self.query.finish()

        self.assertFalse( self.setup.initGenre() )

    def test_initComposers(self):
        self.setup.createTables()
        self.assertTrue( self.setup.initComposer() )

        self.assertTrue( self.query.exec(self.sql_count_composer) )
        self.assertTrue( self.query.next() )
        self.assertGreaterEqual( 40, self.query.value(0))
        self.query.finish()

        self.assertTrue( self.query.exec( self.sql_get_composer ) )
        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 1 )
        self.assertEqual( self.query.value(1) , 'Unknown')

        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 2 )
        self.assertEqual( self.query.value(1) , 'Various')

        self.assertTrue( self.query.next() )
        self.assertEqual( self.query.value(0) , 3 )
        self.assertEqual( self.query.value(1) , 'Teaching')
    
        self.query.finish()

        self.assertFalse( self.setup.initComposer() )

    def test_initData(self):
        self.setup.createTables()
        self.setup.initData()

        self.assertTrue( self.query.exec( self.sql_get_system ) )
        rows = {}
        while self.query.next() :
            rows[ self.query.value(0)] = self.query.value(1)

        self.assertGreaterEqual( len(rows), 14 ,"System should have at least 14 entries")

        self.assertEqual( rows[DbKeys.SETTING_DEFAULT_GSDEVICE]   , DbKeys.VALUE_GSDEVICE )
        self.assertEqual( rows[DbKeys.SETTING_PAGE_LAYOUT]     , DbKeys.VALUE_PAGES_SINGLE )
        self.assertTrue(  rows[DbKeys.SETTING_LAST_BOOK_REOPEN] )# , DbKeys.VALUE_REOPEN_LAST )
        self.assertEqual( rows[DbKeys.SETTING_FILE_TYPE]       , DbKeys.VALUE_FILE_TYPE )
        self.assertEqual( rows[DbKeys.SETTING_DEFAULT_SCRIPT]     , DbKeys.VALUE_SCRIPT_CMD )
        self.assertEqual( rows[DbKeys.SETTING_DEFAULT_SCRIPT_VAR] , DbKeys.VALUE_SCRIPT_VAR )
        


