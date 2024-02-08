"""
Test frame: DbNotes

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import unittest
import logging

from PySide6.QtSql import QSqlQuery
from PySide6.QtCore import QSize

from qdb.dbconn import DbConn
from qdb.dbnote import DbNote
from qdb.setup import Setup
from qdb.fields.note import NoteField
from qdb.util   import DbHelper


NOTE_TEST_DB = ':memory:'


class TestNote(unittest.TestCase):
    def glue(self, query: QSqlQuery, bulkdata: dict):
        for row in bulkdata:
            for key in row:
                query.addBindValue(row[key])
            if not query.exec():
                print("Query failed for",  query.lastError())

    def setUp(self):
        db = DbConn.open_db(NOTE_TEST_DB)
        self.setup = Setup(NOTE_TEST_DB)
        self.setup.drop_tables()
        self.setup.create_tables()
        query = QSqlQuery(db)

        bk_data = [
            {'book': 'test1', 'location': '/loc', 'source': '/src'},
            {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        bk_notedata = [
            {'book_id': 1, 'note': 'note.1.0.0', 'page': 0, 'sequence': 0},
            {'book_id': 1, 'note': 'note.1.1.0', 'page': 1, 'sequence': 0},
            {'book_id': 2, 'note': 'note.2.2.0', 'page': 2, 'sequence': 0},
            {'book_id': 2, 'note': 'note.2.2.1', 'page': 2, 'sequence': 1},
            {'book_id': 2, 'note': 'note.2.3.0', 'page': 3, 'sequence': 0},
        ]
        query.prepare(
            "INSERT INTO Book ( book,location,source) VALUES( ? ,? ,?)")
        self.glue(query, bk_data)

        query.prepare(
            "INSERT INTO Note ( book_id,note,page,sequence) VALUES( ?,?,?,?)")
        self.glue(query, bk_notedata)

        self.obj = DbNote()
        self.obj.show_stack(False)
        self.obj.logger.setlevel(logging.CRITICAL)

    def tearDown(self):
        # (_, cursor) = DbConn().open_db()
        # cursor.execute('DROP TABLE IF EXISTS Bookmark')
        # = DbConn().open_db(close=True)
        # ßDbConn.close_db()
        pass

    def test_get_note_t1(self):
        note = self.obj.get_note(1, 0, 0)
        self.assertIsNotNone(note, 'Database returned no data')
        self.assertEqual(note[NoteField.NOTE], 'note.1.0.0')

    def test_get_note_for_book(self):
        note = self.obj.get_note_for_book(1)
        self.assertIsNotNone(note, 'Database returned no data')
        self.assertEqual(note[NoteField.NOTE], 'note.1.0.0')

    # def test_get_note_t2(self):
    #     note = self.obj.get_note(2, 2, 1)
    #     self.assertEqual(note[NoteField.NOTE], 'note.2.2.1')

    def test_get_note_all(self):
        notes = self.obj.get_all(2)
        self.assertEqual(len(notes), 3, "Number of notes for book 2")
        self.assertEqual(self.obj.count(2, 2), 2)

    def test_delete_page(self):
        self.assertTrue(self.obj.delete_page(1, 0, 0))
        note = self.obj.get_note(1, 0, 0)
        self.assertTrue(NoteField.ID not in note)
        self.assertFalse(self.obj.delete_page(1, 0, 0))

    def test_delete_all_page_notes(self):
        self.assertTrue(self.obj.delete_all_page_notes(2, 2))
        notes = self.obj.get_notes_for_page(2, 2)
        self.assertEqual(len(notes), 0)

    def test_update(self):
        note = self.obj.get_note_for_book(1)
        note[NoteField.NOTE] = 'updated'
        note[NoteField.LOCATION] = "location"
        note[NoteField.SIZE] = 'new size'

        self.obj.update(note)
        note = self.obj.get_note_for_book(1)
        self.assertEqual('updated', note[NoteField.NOTE])
        self.assertEqual('location', note[NoteField.LOCATION])
        self.assertEqual('new size', note[NoteField.SIZE])

    def test_coding(self):
        rtn_value = DbHelper.decode(DbHelper.encode("Silly value"))
        self.assertEqual(rtn_value, 'Silly value')
        q = QSize(10, 20)
        self.assertIsInstance(q, QSize)
        self.assertEqual(q.height(), 20)
        self.assertEqual(q.width(), 10)

        qtest = DbHelper.decode(DbHelper.encode(q))
        self.assertIsInstance(qtest, QSize)
        self.assertEqual(qtest.height(), 20)
        self.assertEqual(qtest.width(), 10)

        self.assertEqual(DbHelper.encode(None), None)
        self.assertIsNone(DbHelper.decode(None))


    def test_add(self):

        dbnote = NoteField.new(
            { NoteField.NOTE: "add",
                 NoteField.BOOK_ID: 3,
                 NoteField.PAGE: 4,
                 NoteField.SEQ: 5,
                 NoteField.LOCATION:'location',
                 NoteField.SIZE: 'size' } )
        recno = self.obj.add(dbnote)
        self.assertGreater(recno, 3,
            f"Recno returned was {recno} not 3")

        dbnote = self.obj.get_note(book=3, page=4, seq=5)
        self.assertEqual(dbnote[NoteField.NOTE], 'add',
            "Note contents not 'add'")
        self.assertEqual(DbHelper.decode(
            dbnote[NoteField.LOCATION]), 'location')
        self.assertEqual(DbHelper.decode(dbnote[NoteField.SIZE]), 'size')
        self.assertEqual(dbnote[NoteField.PAGE], 4)
        self.assertEqual(dbnote[NoteField.SEQ], 5)

    def test_add_page(self):
        self.assertEqual(self.obj.count(2, 2), 2)

        note = NoteField.new( {
                NoteField.NOTE: "add-note3",
                 NoteField.BOOK_ID: 2,
                 NoteField.PAGE: 2,
                 NoteField.LOCATION:'location',
                 NoteField.SIZE: 'size' } )
        self.obj.add( note)

        self.assertGreater(self.obj.add_page(note),3)
        self.assertEqual(self.obj.count(2, 2), 3)

        dbnote = self.obj.get_note(book=2, page=2, seq=2)
        self.assertIsNotNone(dbnote)
        self.assertGreaterEqual(len(dbnote), 5)
        self.assertEqual(dbnote[NoteField.NOTE], 'add-note3')
        self.assertEqual(DbHelper.decode(
            dbnote[NoteField.LOCATION]), 'location')
        self.assertEqual(DbHelper.decode(dbnote[NoteField.SIZE]), 'size')
        self.assertEqual(dbnote[NoteField.PAGE], 2)
        self.assertEqual(dbnote[NoteField.SEQ], 2)

    def test_add_page_error_no_book_id(self):
        note = NoteField.new( {
                NoteField.NOTE: "add-note3",
                 NoteField.BOOK_ID: 2,
                 NoteField.PAGE: 2,
                 NoteField.LOCATION:'location',
                 NoteField.SIZE: 'size' } )

        note[NoteField.BOOK_ID] = 0
        with self.assertRaises(ValueError):
            self.obj.add_page(note)

        note[NoteField.BOOK_ID] = 1
        note[NoteField.PAGE] = None
        with self.assertRaises(ValueError):
            self.obj.add_page(note)

    def test_page_count(self):
        rc = self.obj.note_page_list(2)
        self.assertEqual(len(rc), 2, "Book 2")

        rc = self.obj.note_page_list(1)
        self.assertEqual(len(rc), 2, "Book 1")

        rc = self.obj.note_page_list(3)
        self.assertEqual(len(rc), 0, "Book 3")


if __name__ == "__main__":
    unittest.main()
