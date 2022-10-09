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
from tkinter import W
import unittest
import sqlite3

sys.path.append("../")
from db.dbconn import DbConn
from db.dbbooksettings import DbBookSettings
from db.dbsql import SqlRowString
from db.setup import Setup


class TestDbBookSettings(unittest.TestCase):
    def setUp(self):
        (conn, cursor) = DbConn().openDB(databaseName=':memory:')
        self.setup = Setup(':memory:')
        self.setup.dropTables()
        conn.commit()
        self.setup.createTables()

        bkData = [
                {'book': 'test1', 'location': '/loc', 'source': '/src'},
                {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        for row in bkData:
            cursor.execute(
                "INSERT INTO Book ( book,location,source) VALUES( :book,:location,:source)", row)
        conn.commit()

        settings = [
            {'book_id': 1, 'key': 'key1', 'value': 'value1'},
            {'book_id': 1, 'key': 'key2', 'value': 'value2'},
            {'book_id': 1, 'key': 'key3', 'value': 'value3'},
            {'book_id': 1, 'key': 'key4', 'value': 'value4'},

            {'book_id': 2, 'key': 'key1', 'value': 'value1'},
            {'book_id': 2, 'key': 'key2', 'value': 'value2'},
            {'book_id': 2, 'key': 'key3', 'value': 'value3'},
        ]

        for row in settings:
            cursor.execute(
                "INSERT INTO BookSetting ( book_id,key,value) VALUES( :book_id,:key,:value)", row)
        conn.commit()
        self.test1_count=4
        self.test2_count=3

        system = [
            {"key": 'key4', 'value': 'value4'},
            {"key": 'key5', 'value': 'value5'},
        ]

        for row in system:
            cursor.execute(
                "INSERT INTO System ( key,value) VALUES( :key,:value)", row)
        conn.commit()
        self.settings = DbBookSettings()

    def tearDown(self):
        self.setup.dropTables()
        pass

    def test_getAllSettings(self):
        rows = self.settings.getAll( 'test1')
        self.assertEqual( len(rows), self.test1_count )

        rows = self.settings.getAll( 'test2')
        self.assertEqual( len(rows), self.test2_count )

    def test_getBookSetting_fallback( self ):
        row = self.settings.getValue('test2','key4')
        self.assertEqual( len(row), 4)
        self.assertEqual( row['book'], 'test2')
        self.assertEqual( row['value'], 'value4')
        self.assertEqual( row['key'], 'key4')

    def test_getBookSetting_notfound( self ):
        row = self.settings.getValue('test2','key9')
        self.assertIsNone( row )

    def test_getAll_nobook(self):
        self.assertRaises( ValueError, self.settings.getAll)

    def test_getBookSetting_found(self):
        for i in range(1,5):
            row = self.settings.getValue('test1','key{}'.format(i))
            self.assertIsNotNone( row )
            self.assertEqual( row['value'], 'value{}'.format(i))

    def test_getBookSetting_nokeys(self):
        self.assertRaises( ValueError, self.settings.getValue)

    def test_getInt(self):
        ok = self.settings.setValue( 'test1', 'Key42', 42)
        self.assertTrue( ok )
        self.assertEqual( 42, self.settings.getInt('test1','Key42'))

        ok = self.settings.setValue( 'test1', 'KeyNeg42', -42)
        self.assertTrue( ok )
        self.assertEqual( -42,self.settings.getInt('test1','KeyNeg42'))

        ok = self.assertEqual( 52,self.settings.getInt('test1','noKey', fallback=False,default=52))
        ok = self.assertEqual( -52,self.settings.getInt('test1','noKey', fallback=False,default=-52))

    def test_getBookSettingInt_bad(self):
        ok = self.settings.setValue( 'test1', 'keyNoWay', 'no way')
        self.assertTrue( ok )
        self.assertEqual( 0,self.settings.getInt('test1','keyNoWay'))

    def test_getBool(self):
        ok = self.settings.setValue( 'test1', 'keyTrue', True)
        self.assertTrue( ok )
        self.assertTrue( self.settings.getBool('test1','keyTrue'))

        ok = self.settings.setValue( 'test1', 'keyFalse', False)
        self.assertTrue( ok )
        self.assertFalse( self.settings.getBool('test1','keyFalse'))

        ok = self.assertFalse( self.settings.getBool('test1','noKey', fallback=False,default=False))
        ok = self.assertTrue( self.settings.getBool('test1','noKey', fallback=False,default=True))

    def test_getBookSettingBool_bad(self):
        ok = self.settings.setValue( 'test1', 'keyNoWay', 'no way')
        self.assertTrue( ok )
        self.assertFalse( self.settings.getBool('test1','keyNoWay'))

    def test_setValue(self):
        ok = self.settings.setValue( 'test1', 'keyadd', 'valueadd')
        self.assertTrue( ok )

        ok = self.settings.setValue('test1', 'keyadd', 'valueadd2', ignore=True )
        self.assertFalse( ok ,"Did not have error on duplicate key")

        self.assertRaises(sqlite3.IntegrityError, self.settings.setValue, 'test1','keyadd', 'valueadd2')

        row = self.settings.getValue('test1', 'keyadd')
        self.assertEqual( row['value'], 'valueadd')
        self.assertEqual( row['key'], 'keyadd')
        self.assertEqual( row['book'], 'test1')

        self.assertRaises( sqlite3.OperationalError, self.settings.setValue, 'title5', 'key5', 'value5')
        
    def test_setValue_nokeys(self):    
        self.assertRaises( ValueError, self.settings.setValue, None)
        self.assertFalse( self.settings.setValue( ignore=True))

    def test_setValue(self):
        ok = self.settings.setValue( 'test1', 'keyadd', 'valueadd')
        self.assertTrue( ok )

        ok = self.settings.upsertBookSetting(book='test1', key='keyadd', value='valueadd2')
        self.assertTrue( ok )
        row = self.settings.getValue('test1', 'keyadd')
        self.assertEqual( row['value'], 'valueadd2')
        self.assertEqual( row['key'], 'keyadd')
        self.assertEqual( row['book'], 'test1')

    def test_upsert_fail(self):
        self.assertRaises( ValueError, self.settings.upsertBookSetting,None, None,None)
        self.assertFalse( self.settings.upsertBookSetting(None, ignore=True))
    
    def test_delone(self):
        row = self.settings.getAll('test1')
        self.assertEqual( len(row), self.test1_count)
        ok=self.settings.deleteValue('test1','key1')
        self.assertTrue(ok)
        self.assertEqual( ok, 1 )
        row = self.settings.getAll('test1')
        self.assertEqual( len(row), self.test1_count-1)

        ok=self.settings.deleteValue(book='test1',key='keyx')
        self.assertFalse( ok )
        row = self.settings.getAll('test1')
        self.assertEqual( len(row), self.test1_count-1)

    def test_delone_badcall(self):
        self.assertRaises(ValueError, self.settings.deleteValue,None, None )
        self.assertRaises(sqlite3.OperationalError, self.settings.deleteValue,'test5', 'key1' )

        ok=self.settings.deleteValue(book=None, key='', ignore=True)
        self.assertEqual(ok, 0 )

    def test_delall(self):
        row = self.settings.getAll('test1')
        self.assertEqual( len(row), self.test1_count)

        count = self.settings.deleteAllValues('test1')
        self.assertEqual(count, self.test1_count)

        row = self.settings.getAll('test1')
        self.assertEqual( len(row), 0)  

    def test_delall_badcall(self):
        self.assertRaises(ValueError, self.settings.deleteAllValues,None)
        self.assertRaises(sqlite3.OperationalError, self.settings.deleteAllValues,'test5')

        ok=self.settings.deleteAllValues(book=None, ignore=True)
        self.assertEqual(ok, 0 )
  
        

if __name__ == "__main__":
    unittest.main()
