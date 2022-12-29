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
from qdb.dbconn import DbConn
from qdb.dbbooksettings import DbBookSettings
from qdb.setup import Setup
from qdb.util  import DbHelper
from PySide6.QtSql import QSqlQuery


class TestDbBookSettings(unittest.TestCase):
    def glue( self,  row:dict ):
        for key in row:
            self.query.addBindValue(row[key] )

    def setUp(self):
        db = DbConn().openDB( ':memory:')
        s = Setup(":memory:")
        s.dropTables()
        s.createTables()
        del s

        self.query = QSqlQuery( db )

        ### BOOK
        bkData = [
                {'book': 'test1', 'location': '/loc', 'source': '/src'},
                {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        self.query.prepare("INSERT INTO Book ( book,location,source) VALUES( ?,?,?)" )
        for row in bkData:
            self.glue( row )
            if not self.query.exec():
                raise RuntimeError( self.query.lastError().text() )
        self.query.finish()

        settings = [
            {'book_id': 1, 'key': 'key1', 'value': 'value1'},
            {'book_id': 1, 'key': 'key2', 'value': 'value2'},
            {'book_id': 1, 'key': 'key3', 'value': 'value3'},
            {'book_id': 1, 'key': 'key4', 'value': 'value4'},

            {'book_id': 2, 'key': 'key1', 'value': 'value1'},
            {'book_id': 2, 'key': 'key2', 'value': 'value2'},
            {'book_id': 2, 'key': 'key3', 'value': 'value3'},
        ]
        self.query.prepare("INSERT INTO BookSetting ( book_id,key,value) VALUES( ?, ?,? )" )
        for row in settings:
            self.glue( row )
            if not self.query.exec():
                raise RuntimeError( self.query.lastError().text() )
        self.query.finish()
        self.test1_count=4
        self.test2_count=3

        system = [
            {"key": 'key4', 'value': 'value4'},
            {"key": 'key5', 'value': 'value5'},
        ]
        self.query.prepare( "INSERT INTO System ( key,value) VALUES( ?,?)" )
        for row in system:
            self.glue( row )
            if not self.query.exec():
                raise RuntimeError( self.query.lastError().text() )
        self.query.finish()
        self.settings = DbBookSettings()
    

    def tearDown(self):
        pass

    def test_getAllSettings(self):
        rows = self.settings.getAll( 'test1')
        self.assertEqual( len(rows), self.test1_count )

        rows = self.settings.getAll( 'test2')
        self.assertEqual( len(rows), self.test2_count )


    def test_getBookSetting_fallback( self ):
        value = self.settings.getValue('test2','key4')
        self.assertIsNotNone( value , "test2 fallback of key4")
        self.assertEqual( value, 'value4')

    def test_getBookSetting_notfound( self ):
        row = self.settings.getValue('test2','key9')
        self.assertIsNone( row )

    def test_getAll_nobook(self):
        self.assertRaises( ValueError, self.settings.getAll)

    def test_getBookSetting_found(self):
        for i in range(1,5):
            value = self.settings.getValue('test1','key{}'.format(i))
            self.assertIsNotNone( value )
            self.assertEqual( value, 'value{}'.format(i))

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
        self.assertTrue(  self.settings.setValue( 'test1', 'keyadd', 'valueadd') , "Insert first record")
        self.assertFalse( self.settings.setValue( 'test1', 'keyadd', 'valueadd2') , "Insert Duplicate")

        row = self.settings.getValue('test1', 'keyadd')
        self.assertEqual( row, 'valueadd')
        rtn = self.settings.setValue( 'title5', 'key5', 'value5')
        self.assertFalse( rtn )
        
    def test_setValue_nokeys(self):    
        self.assertRaises( ValueError, self.settings.setValue, None)
        self.assertFalse( self.settings.setValue( ignore=True))

    def test_setValue(self):
        self.assertTrue(self.settings.setValue( 'test1', 'keyadd', 'valueadd') )
        self.assertTrue(self.settings.upsertBookSetting(book='test1', key='keyadd', value='valueadd2'))
        
        row = self.settings.getValue('test1', 'keyadd')
        self.assertEqual( row, 'valueadd2')

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
        self.assertFalse( self.settings.deleteValue('test5', 'key1' ) )

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
        self.assertEqual(self.settings.deleteAllValues('test5') , -1)

        ok=self.settings.deleteAllValues(book=None, ignore=True)
        self.assertEqual(ok, -1 )
  
        

if __name__ == "__main__":
    unittest.main()
