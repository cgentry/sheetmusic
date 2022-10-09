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

from .dbconn import DbConn
from .setup import Setup
from .dbsystem import DbSystem
from db.keys   import DbKeys

class TestSetup( unittest.TestCase):
    sql_get_tablenames="""
            SELECT name
            FROM sqlite_schema
            WHERE type ='table' 
            AND name NOT LIKE 'sqlite_%';"""
    sql_get_viewnames="""
            SELECT name
            FROM sqlite_schema
            WHERE type ='view' 
            AND name NOT LIKE 'sqlite_%';"""

    sql_get_genre="""
            SELECT id, name
            FROM Genre
            ORDER BY id
            """
    sql_get_composer="""
            SELECT id, name
            FROM Composer
            ORDER BY id
            """
    sql_get_system="""
            SELECT *
            FROM System
        """

    def setUp(self):
        (self.conn, self.cursor) = DbConn().openDB(':memory:')
        self.setup = Setup(":memory:")
        self.setup.dropTables()

    def test_createTables(self):
        result=self.cursor.execute(self.sql_get_tablenames)
        rows=result.fetchall()
        self.assertEqual( 0, len(rows ))
        result=self.cursor.execute(self.sql_get_viewnames)
        rows=result.fetchall()
        self.assertEqual( 0, len(rows ))

        self.setup.createTables()
        result=self.cursor.execute(self.sql_get_tablenames)
        rows=result.fetchall()
        self.assertEqual( 6, len(rows ))
        result=self.cursor.execute(self.sql_get_viewnames)
        rows=result.fetchall()
        self.assertEqual( 3, len(rows ))

    def test_dropTables(self):
        self.setup.createTables()
        self.setup.dropTables()

        result=self.cursor.execute(self.sql_get_tablenames)
        rows=result.fetchall()
        self.assertEqual( 0, len(rows ))
        result=self.cursor.execute(self.sql_get_viewnames)
        rows=result.fetchall()
        self.assertEqual( 0, len(rows ))

    def test_initGenre(self):
        self.setup.createTables()
        self.assertTrue( self.setup._initGenre() )
        result=self.cursor.execute( self.sql_get_genre )
        rows = result.fetchall()
        self.assertEqual( rows[0]['id'], 1 )
        self.assertEqual( rows[1]['id'], 2 )
        self.assertEqual( rows[2]['id'], 3 )

        self.assertEqual( rows[0]['name'], 'Unknown' )
        self.assertEqual( rows[1]['name'], 'Various' )
        self.assertEqual( rows[2]['name'], 'Teaching' )

        self.assertEqual( len(rows), 30 )
        self.assertFalse( self.setup._initGenre() )

    def test_initComposers(self):
        self.setup.createTables()
        self.assertTrue( self.setup._initComposers() )
        result=self.cursor.execute( self.sql_get_composer )
        rows = result.fetchall()
        self.assertEqual( len(rows), 40 )

        self.assertEqual( rows[0]['id'], 1 )
        self.assertEqual( rows[1]['id'], 2 )
        self.assertEqual( rows[2]['id'], 3 )

        self.assertEqual( rows[0]['name'], 'Unknown' )
        self.assertEqual( rows[1]['name'], 'Various' )
        self.assertEqual( rows[2]['name'], 'Teaching' )

        self.assertFalse( self.setup._initComposers() )

    def test_initData(self):
        self.setup.createTables()
        self.setup.initData()

        result=self.cursor.execute( self.sql_get_system )
        rows = result.fetchall()

        self.assertEqual( len(rows), 12 )

        sysdata = { row['key']: row['value'] for row in rows }

        self.assertEqual( sysdata[DbKeys.SETTING_DEFAULT_GSDEVICE]   , DbKeys.VALUE_GSDEVICE )
        self.assertEqual( sysdata[DbKeys.SETTING_PAGE_LAYOUT]     , DbKeys.VALUE_PAGES_SINGLE )
        self.assertTrue(  sysdata[DbKeys.SETTING_LAST_BOOK_REOPEN] )# , DbKeys.VALUE_REOPEN_LAST )
        self.assertEqual( sysdata[DbKeys.SETTING_FILE_TYPE]       , DbKeys.VALUE_FILE_TYPE )
        self.assertEqual( sysdata[DbKeys.SETTING_DEFAULT_SCRIPT]     , DbKeys.VALUE_SCRIPT_CMD )
        self.assertEqual( sysdata[DbKeys.SETTING_DEFAULT_SCRIPT_VAR] , DbKeys.VALUE_SCRIPT_VAR )
        
        sysPath = os.path.expanduser(DbKeys.VALUE_DEFAULT_DIR)
        self.assertEqual( sysdata[DbKeys.SETTING_DEFAULT_PATH_MUSIC] , sysPath )


