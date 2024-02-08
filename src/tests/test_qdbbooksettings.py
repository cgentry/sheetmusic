"""
Test frame: BookSetting

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#disable docstring, too many public methods
#pylint: disable=C0115
#pylint: disable=C0116
#pylint: disable=R0904

import sys
import unittest
import logging

from PySide6.QtSql import QSqlQuery

from qdb.setup import Setup
from qdb.dbbooksettings import DbBookSettings
from qdb.dbconn import DbConn

sys.path.append("../")

class TestDbBookSettings(unittest.TestCase):
    BOOK1 = 'test1'
    BOOK2 = 'test2'
    def glue(self,  row: dict):
        for key in row:
            self.query.addBindValue(row[key])

    def setUp(self):
        db = DbConn().open_db(':memory:')
        s = Setup(":memory:")
        s.drop_tables()
        s.create_tables()
        del s

        self.query = QSqlQuery(db)

        # BOOK
        bk_data = [
            {'book': self.BOOK1, 'location': '/loc', 'source': '/src'},
            {'book': self.BOOK2, 'location': '/loc', 'source': '/src'},
        ]
        self.query.prepare(
            "INSERT INTO Book ( book,location,source) VALUES( ?,?,?)")
        for row in bk_data:
            self.glue(row)
            if not self.query.exec():
                raise RuntimeError(self.query.lastError().text())
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
        self.query.prepare(
            "INSERT INTO BookSetting ( book_id,key,value) VALUES( ?, ?,? )")
        for row in settings:
            self.glue(row)
            if not self.query.exec():
                raise RuntimeError(self.query.lastError().text())
        self.query.finish()
        self.test1_count = 4
        self.test2_count = 3

        system = [
            {"key": 'key4', 'value': 'value4'},
            {"key": 'key5', 'value': 'value5'},
        ]
        self.query.prepare("INSERT INTO System ( key,value) VALUES( ?,?)")
        for row in system:
            self.glue(row)
            if not self.query.exec():
                raise RuntimeError(self.query.lastError().text())
        self.query.finish()
        self.obj = DbBookSettings()
        self.obj.show_stack(False)
        self.obj.logger.setlevel(logging.CRITICAL)

    def tearDown(self):
        pass

    def test_get_all_settingss(self):
        rows = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(rows), self.test1_count)

        rows = self.obj.get_all(self.BOOK2)
        self.assertEqual(len(rows), self.test2_count)

    def test_get_booksetting_fallback(self):
        value = self.obj.get_value(self.BOOK2, 'key4')
        self.assertIsNotNone(value, "test2 fallback of key4")
        self.assertEqual(value, 'value4')

    def test_get_booksetting_notfound(self):
        row = self.obj.get_value(self.BOOK2, 'key9')
        self.assertIsNone(row)

    def test_get_all_nobook(self):
        book = None
        with self.assertRaises( ValueError ):
            self.obj.get_all(book)

    def test_get_booksetting_found(self):
        for i in range(1, 5):
            value = self.obj.get_value(self.BOOK1, f'key{i}')
            self.assertIsNotNone(value)
            self.assertEqual(value, f'value{i}')

    def test_get_booksetting_nokeys(self):
        with self.assertRaises(ValueError):
            self.obj.get_value( None , None )

    def test_get_str(self):
        self.assertTrue(
                self.obj.set_value(
                    self.BOOK1,
                    'KeyStr',
                    'yes'),
                'Set value failed for KeyStr=yes')
        self.assertEqual( 'yes',
                self.obj.get_value( self.BOOK1, 'KeyStr' ),
                'Get value failed for KeyStr and value=yes')

    def test_get_int(self):
        ok = self.obj.set_value(self.BOOK1, 'Key42', 42)
        self.assertTrue(ok)
        self.assertEqual(42, self.obj.get_int(self.BOOK1, 'Key42'))

        ok = self.obj.set_value(self.BOOK1, 'KeyNeg42', -42)
        self.assertTrue(ok)
        self.assertEqual(-42, self.obj.get_int(self.BOOK1, 'KeyNeg42'))

        ok = self.obj.get_int(self.BOOK1, 'noKey', fallback=False, default=52)
        self.assertEqual(52, ok,
                f"wrong value returned: {self.obj.get_value(self.BOOK1, 'noKey')}")

        ok = self.obj.get_int(self.BOOK1, 'noKey', fallback=False, default=-52)
        self.assertEqual(-52, ok )

    def test_get_booksetting_int_bad(self):
        self.assertTrue(self.obj.set_value(self.BOOK1, 'keyNoWay', 'no way'))
        self.assertEqual(0, self.obj.get_int(self.BOOK1, 'keyNoWay'))

    def test_get_bool(self):
        print("\nStart")
        self.assertTrue(self.obj.set_value(self.BOOK1, 'keyTrue', True))

        for item in self.obj.get_all(self.BOOK1):
            print(f'LIST: {item}')
        self.assertTrue(self.obj.get_bool(self.BOOK1, 'keyTrue'))

        ok = self.obj.set_value(self.BOOK1, 'keyFalse', False)
        self.assertTrue(ok)
        self.assertFalse(self.obj.get_bool(self.BOOK1, 'keyFalse'))

        self.assertFalse(self.obj.get_bool(
            self.BOOK1, 'noKey', fallback=False, default=False))

        self.assertTrue(self.obj.get_bool(
            self.BOOK1, 'noKey', fallback=False, default=True))

    def test_get_booksetting_bool_bad(self):
        ok = self.obj.set_value(self.BOOK1, 'keyNoWay', 'no way')
        self.assertTrue(ok)
        self.assertFalse(self.obj.get_bool(self.BOOK1, 'keyNoWay'))

    def test_set_value(self):
        self.assertTrue(self.obj.set_value(self.BOOK1, 'keyadd',
                        'valueadd'), "Insert first record")
        self.assertFalse(self.obj.set_value(
            self.BOOK1, 'keyadd', 'valueadd2'), "Insert Duplicate")

        row = self.obj.get_value(self.BOOK1, 'keyadd')
        self.assertEqual(row, 'valueadd')
        with self.assertRaises( ValueError ):
            self.obj.set_value('title5', 'key5', 'value5')

    def test_set_value_nokeys(self):
        with self.assertRaises(ValueError):
            self.obj.set_value( None , None )
        rtn = self.obj.set_value( None, None, ignore=True)
        self.assertFalse( rtn ,"Return for no book should  be false")


    def test_set_value2(self):
        self.assertTrue(self.obj.set_value(self.BOOK1, 'keyadd', 'valueadd'))
        self.assertTrue(self.obj.upsert_booksettings(
            book=self.BOOK1, key='keyadd', value='valueadd2'))

        row = self.obj.get_value(self.BOOK1, 'keyadd')
        self.assertEqual(row, 'valueadd2')

    def test_upsert_fail(self):
        with self.assertRaises( ValueError ):
            self.obj.upsert_booksettings( None, None, None)
        self.assertFalse(self.obj.upsert_booksettings(None, ignore=True))

    def test_delone(self):
        row = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(row), self.test1_count)
        ok = self.obj.delete_value(self.BOOK1, 'key1')
        self.assertTrue(ok)
        self.assertEqual(ok, 1)
        row = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(row), self.test1_count-1)

        ok = self.obj.delete_value(book=self.BOOK1, key='keyx')
        self.assertFalse(ok)
        row = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(row), self.test1_count-1)

    def test_delone_badcall(self):
        with self.assertRaises(ValueError):
            self.obj.delete_value( None, None)
        self.assertFalse(self.obj.delete_value('test5', 'key1'))

        ok = self.obj.delete_value(book=None, key='', ignore=True)
        self.assertEqual(ok, 0)

    def test_delall(self):
        row = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(row), self.test1_count)

        count = self.obj.delete_all_values(self.BOOK1)
        self.assertEqual(count, self.test1_count)

        row = self.obj.get_all(self.BOOK1)
        self.assertEqual(len(row), 0)

    def test_delall_badcall(self):
        with self.assertRaises(ValueError):
            self.obj.delete_all_values( None)
        self.assertEqual(self.obj.delete_all_values('test5'), -1)

        ok = self.obj.delete_all_values(book=None, ignore=True)
        self.assertEqual(ok, 0)


if __name__ == "__main__":
    unittest.main()
