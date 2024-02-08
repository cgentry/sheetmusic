"""
Test frame: DbBookmark

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
#disable no docstrings, too many public methods
#pylint: disable=C0115
#pylint: disable=C0116
#pylint: disable=R0904

import unittest
import logging

#sys.path.append("../")
from PySide6.QtSql  import QSqlQuery
from qdb.dbconn     import DbConn
from qdb.dbbookmark import DbBookmark
from qdb.setup      import Setup
from qdb.fields.bookmark import BookmarkField


class TestDbBookmark(unittest.TestCase):
    """ TestDbBookmark"""
    def glue( self, query:QSqlQuery , bulkdata:dict ):
        for row in bulkdata:
            for key in row:
                query.bindValue( ":"+key , row[key])
            query.exec()


    def setUp(self):
        db = DbConn.open_db(':memory:')
        self.setup = Setup(':memory:')
        self.setup.drop_tables()
        self.setup.create_tables()
        query = QSqlQuery( db )

        bk_data = [
                {'book': 'test1', 'location': '/loc', 'source': '/src'},
                {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        bkmark_data = [
                {'book_id': 1, 'bookmark': 'bk01', 'page': 5},
                {'book_id': 1, 'bookmark': 'bk02', 'page': 10},
                {'book_id': 1, 'bookmark': 'bk03', 'page': 15},
                {'book_id': 1, 'bookmark': 'bk04', 'page': 20},
                {'book_id': 2, 'bookmark': 'bkz2', 'page': 5},
                {'book_id': 2, 'bookmark': 'bkz1', 'page': 10},

        ]
        query.prepare("INSERT INTO Book ( book,location,source) VALUES( :book,:location,:source)" )
        self.glue( query , bk_data )

        query.prepare( """INSERT INTO Bookmark
                      ( book_id,bookmark,page) VALUES( :book_id,:bookmark,:page)""" )
        self.glue( query, bkmark_data )

        self.obj = DbBookmark()
        self.obj.show_stack(False)
        self.obj.logger.setlevel( logging.CRITICAL )

    def tearDown(self):
        # (_, cursor) = DbConn().open_db()
        # cursor.execute('DROP TABLE IF EXISTS Bookmark')
        # = DbConn().open_db(close=True)
        pass

    def test_get_bookmark_for_page(self):
        bk = self.obj.get_bookmark_for_page(book='test1', page=12)
        self.assertIsNotNone(bk)
        self.assertEqual( len(bk) , 5 )
        self.assertEqual(bk[ BookmarkField.BOOK ], 'test1')
        self.assertEqual(bk[ BookmarkField.NAME ], 'bk02')
        self.assertEqual(bk[ BookmarkField.PAGE ], 10)

    def test_last( self ):
        """ check last bookmark """
        bk = self.obj.get_last( book='test1')
        self.assertIsNotNone(bk)
        self.assertEqual( len(bk) , 5, 'Should be five fields' )
        self.assertEqual(bk[ BookmarkField.BOOK ] , 'test1')
        self.assertEqual(bk[ BookmarkField.NAME ] , 'bk04')

    def test_last_nothere( self ):
        """ Test if book doesn't exist"""
        bk = self.obj.get_last( book='nothere')
        self.assertIsNone(bk)

    def test_empty_database(self):
        self.setup.drop_tables()
        self.setup.create_tables()
        bk = self.obj.get_bookmark_for_page(book='test1', page=12)
        self.assertIsNone( bk )

    def test_get_first_bookmark_for_page(self):
        bk = self.obj.get_first(book='test1')
        self.assertIsNotNone(bk)
        self.assertEqual(bk[ BookmarkField.BOOK ], 'test1')
        self.assertEqual(bk[ BookmarkField.NAME ], 'bk01')
        self.assertEqual(bk[ BookmarkField.PAGE], 5)

    def test_get_previous_bookmark_for_page(self):
        bk = self.obj.get_bookmark_for_page( 'test1' , 12 )
        self.assertIsNotNone(bk)
        self.assertEqual(bk[ BookmarkField.NAME ], 'bk02',
                         'Confirm we have the correct ID for this page')
        bk = self.obj.get_previous_bookmark_for_page(book='test1', page=12)
        self.assertIsNotNone(bk)
        self.assertEqual(bk[ BookmarkField.BOOK ], 'test1')
        self.assertEqual(bk[ BookmarkField.NAME ], 'bk01', 'Went from bk02 to bk01')
        self.assertEqual(bk[ BookmarkField.PAGE], 5)

    def test_get_previous_bookmark_for_page_at_start(self):
        bk = self.obj.get_previous_bookmark_for_page(book='test1', page=5)
        self.assertIsNone(bk)

    def test_get_next_bookmark_for_page(self):
        bk = self.obj.get_next_bookmark_for_page(book='test1', page=12)
        self.assertEqual( len(bk) , 5 )
        self.assertIsNotNone(bk)
        self.assertEqual( bk[ BookmarkField.BOOK ], 'test1')
        self.assertEqual( bk[ BookmarkField.NAME ], 'bk03')
        self.assertEqual( bk[ BookmarkField.PAGE ], 15)

    def test_get_next_bookmark_for_page_at_end(self):
        bk = self.obj.get_next_bookmark_for_page(book='test1', page=20)
        self.assertIsNone(bk)

    def test_count( self ):
        count = self.obj.get_count(book='test1')
        self.assertEqual( count, 4, 'Count of test1 should be 4')
        count = self.obj.get_count(book='test2')
        self.assertEqual( count, 2, 'Count of test2 should be 2')
        count = self.obj.get_count(book='test3')
        self.assertEqual( count, 0 , 'Count of test3 should be zero')

    def test_get_all_bookmarks( self ):
        bk = self.obj.get_all( 'test1' )
        self.assertEqual( len(bk), 4 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 5)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[2][ BookmarkField.VALUE ] , 15)
        self.assertEqual( bk[3][ BookmarkField.VALUE ] , 20)

        bk = self.obj.get_all('test2')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 5)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 10)

        ## bookmark names will reverse the page order
        bk = self.obj.get_all('test2', order="bookmark")
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 5)

    def test_del_bookmark( self):
        rtn = self.obj.delete( book='test1', bookmark='bk01')
        self.assertTrue(rtn )
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 3 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 15)
        self.assertEqual( bk[2][ BookmarkField.VALUE ] , 20)

        rtn = self.obj.delete( book='test1', bookmark='bk03')
        self.assertTrue( rtn )
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 20)

        rtn = self.obj.delete( book='test1', bookmark='bk03')
        self.assertFalse( rtn )

    def test_delbookmark_bypage( self):
        rtn=self.obj.delete_by_page( book='test1', page=5)
        self.assertTrue( rtn )
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 3 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 15)
        self.assertEqual( bk[2][ BookmarkField.VALUE ] , 20)

        self.obj.delete_by_page( book='test1', page=15)
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 20)

    def test_delallbookmark(self):
        self.obj.delete_all( 'test1')
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 0 )
        self.obj.delete_all( 'test1')
        rtn=self.obj.delete_by_page( book='test1', page=5)
        self.assertFalse( rtn )

        rtn=self.obj.delete_all( None)
        self.assertFalse( rtn )

    def test_addbookmark(self):
        self.obj.add('test1','new01',25)
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 5 )
        self.assertEqual( bk[0][ BookmarkField.VALUE ] ,  5)
        self.assertEqual( bk[1][ BookmarkField.VALUE ] , 10)
        self.assertEqual( bk[2][ BookmarkField.VALUE ] , 15)
        self.assertEqual( bk[3][ BookmarkField.VALUE ] , 20)
        self.assertEqual( bk[4][ BookmarkField.VALUE ] , 25)
        self.assertEqual( bk[4][ BookmarkField.NAME  ] , 'new01')

    def test_get_all_bookmarks_empty(self):
        self.obj.delete_all('test1')
        bk = self.obj.get_all('test1')
        self.assertEqual( len(bk), 0 )
        bk = self.obj.get_all(None)
        self.assertEqual( len(bk), 0 )

    def test_last_page(self):
        val = self.obj.last_page( 'test1',5)
        self.assertIsNotNone( val )
        self.assertEqual( val, 9)
        val = self.obj.last_page( 'test1',10)
        self.assertIsNotNone( val )
        self.assertEqual( val, 14 )

        val = self.obj.last_page( 'test1',17)
        self.assertIsNotNone( val )
        self.assertEqual( val, 19)

        val = self.obj.last_page( 'test1',21)
        self.assertIsNone( val ,"Last bookmark at 20")

    def test_delbookmark_no_book( self):
        self.obj.delete( book='junk', bookmark='test01')

if __name__ == "__main__":
    unittest.main()
