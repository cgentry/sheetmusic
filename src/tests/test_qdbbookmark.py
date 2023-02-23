# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
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
import logging

sys.path.append("../")
from qdb.dbconn     import DbConn
from qdb.dbbookmark import DbBookmark
from qdb.setup      import Setup
from qdb.keys       import BOOKMARK
from PySide6.QtSql  import QSqlQuery

class TestDbBookmark(unittest.TestCase):
    def glue( self, query:QSqlQuery , bulkdata:dict ):
        for row in bulkdata:
            for key in row:
                query.bindValue( ":"+key , row[key])
            query.exec()
            

    def setUp(self):
        db = DbConn.openDB(':memory:')
        self.setup = Setup(':memory:')
        self.setup.dropTables()
        self.setup.createTables()
        query = QSqlQuery( db )
    
        bkData = [
                {'book': 'test1', 'location': '/loc', 'source': '/src'},
                {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        bkmarkData = [
                {'book_id': 1, 'bookmark': 'bk01', 'page': 5},
                {'book_id': 1, 'bookmark': 'bk02', 'page': 10},
                {'book_id': 1, 'bookmark': 'bk03', 'page': 15},
                {'book_id': 1, 'bookmark': 'bk04', 'page': 20},
                {'book_id': 2, 'bookmark': 'bkz2', 'page': 5},
                {'book_id': 2, 'bookmark': 'bkz1', 'page': 10},

        ]
        query.prepare("INSERT INTO Book ( book,location,source) VALUES( :book,:location,:source)" )
        self.glue( query , bkData )

        query.prepare( "INSERT INTO Bookmark ( book_id,bookmark,page) VALUES( :book_id,:bookmark,:page)" )
        self.glue( query, bkmarkData )

        self.obj = DbBookmark()
        self.obj.showStack(False)
        self.obj.logger.setLevel( logging.CRITICAL )

    def tearDown(self):
        # (_, cursor) = DbConn().openDB()
        # cursor.execute('DROP TABLE IF EXISTS Bookmark')
        # = DbConn().openDB(close=True)
        pass

    def test_getBookmarkForPage(self):
        bk = self.obj.getBookmarkForPage(book='test1', page=12)
        self.assertIsNotNone(bk)
        self.assertEqual( len(bk) , 6 )
        self.assertEqual(bk[ BOOKMARK.book ], 'test1')
        self.assertEqual(bk[ BOOKMARK.name ], 'bk02')
        self.assertEqual(bk[BOOKMARK.page], 10)

    def test_last( self ):
        bk = self.obj.last( book='test1')
        self.assertIsNotNone(bk)
        self.assertEqual( len(bk) , 6 )
        self.assertEqual(bk[ BOOKMARK.book ] , 'test1')
        self.assertEqual(bk[ BOOKMARK.name ] , 'bk04')
    
    def test_last( self ):
        bk = self.obj.last( book='nothere')
        self.assertIsNone(bk)

    def test_emptyDatabase(self):
        self.setup.dropTables()
        self.setup.createTables()
        bk = self.obj.getBookmarkForPage(book='test1', page=12)
        self.assertIsNone( bk )
        
    def test_getFirstBookmarkFor(self):
        bk = self.obj.first(book='test1')
        self.assertIsNotNone(bk)
        self.assertEqual(bk[ BOOKMARK.book ], 'test1')
        self.assertEqual(bk[ BOOKMARK.name ], 'bk01')
        self.assertEqual(bk[ BOOKMARK.page], 5)
    
    def test_getPreviousBookmarkForPage(self):
        bk = self.obj.getPreviousBookmarkForPage(book='test1', page=12)
        self.assertIsNotNone(bk)
        self.assertEqual(bk[ BOOKMARK.book ], 'test1')
        self.assertEqual(bk[ BOOKMARK.name ], 'bk01')
        self.assertEqual(bk[ BOOKMARK.page], 5)

    def test_getPreviousBookmarkForPage_AtStart(self):
        bk = self.obj.getPreviousBookmarkForPage(book='test1', page=5)
        self.assertIsNone(bk)

    def test_getNextBookmarkForPage(self):
        bk = self.obj.getNextBookmarkForPage(book='test1', page=12)
        self.assertEqual( len(bk) , 6 )
        self.assertIsNotNone(bk)
        self.assertEqual( bk[ BOOKMARK.book ], 'test1')
        self.assertEqual( bk[ BOOKMARK.name ], 'bk03')
        self.assertEqual( bk[ BOOKMARK.page ], 15)

    def test_getNextBookmarkForPage_AtEnd(self):
        bk = self.obj.getNextBookmarkForPage(book='test1', page=20)
        self.assertIsNone(bk)

    def test_count( self ):
        count = self.obj.count(book='test1')
        self.assertEqual( count, 4)
        count = self.obj.count(book='test2')
        self.assertEqual( count, 2)
        count = self.obj.count(book='test3')
        self.assertEqual( count, 0 )

    def test_getallbookmarks( self ):
        bk = self.obj.getAll( 'test1' )
        self.assertEqual( len(bk), 4 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 5)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[2][ BOOKMARK.value ] , 15)
        self.assertEqual( bk[3][ BOOKMARK.value ] , 20)

        bk = self.obj.getAll('test2')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 5)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 10)

        ## bookmark names will reverse the page order
        bk = self.obj.getAll('test2', order="bookmark")
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 5)

    def test_delbookmark( self):
        rtn = self.obj.delete( book='test1', bookmark='bk01')
        self.assertTrue(rtn )
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 3 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 15)
        self.assertEqual( bk[2][ BOOKMARK.value ] , 20)

        rtn = self.obj.delete( book='test1', bookmark='bk03')
        self.assertTrue( rtn )
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 20)

        rtn = self.obj.delete( book='test1', bookmark='bk03')
        self.assertFalse( rtn )

    def test_delbookmark_bypage( self):
        rtn=self.obj.delete_by_page( book='test1', page=5)
        self.assertTrue( rtn )
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 3 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 15)
        self.assertEqual( bk[2][ BOOKMARK.value ] , 20)

        self.obj.delete_by_page( book='test1', page=15)
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 20)

    def test_delallbookmark(self):
        self.obj.delete_all( 'test1')
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 0 )
        self.obj.delete_all( 'test1')
        rtn=self.obj.delete_by_page( book='test1', page=5)
        self.assertFalse( rtn )
        
        rtn=self.obj.delete_all( None)
        self.assertFalse( rtn )

    def test_addbookmark(self):
        self.obj.add('test1','new01',25)
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 5 )
        self.assertEqual( bk[0][ BOOKMARK.value ] ,  5)
        self.assertEqual( bk[1][ BOOKMARK.value ] , 10)
        self.assertEqual( bk[2][ BOOKMARK.value ] , 15)
        self.assertEqual( bk[3][ BOOKMARK.value ] , 20)
        self.assertEqual( bk[4][ BOOKMARK.value ] , 25)
        self.assertEqual( bk[4][ BOOKMARK.name  ] , 'new01')

    def test_getAllBookmarks_empty(self):
        self.obj.delete_all('test1')
        bk = self.obj.getAll('test1')
        self.assertEqual( len(bk), 0 )
        bk = self.obj.getAll(None)
        self.assertEqual( len(bk), 0 )

    def test_lastpage(self):
        val = self.obj.lastpage( 'test1',5)
        self.assertIsNotNone( val )
        self.assertEqual( val, 9)
        val = self.obj.lastpage( 'test1',10)
        self.assertIsNotNone( val )
        self.assertEqual( val, 14 )

        val = self.obj.lastpage( 'test1',17)
        self.assertIsNotNone( val )
        self.assertEqual( val, 19)

        val = self.obj.lastpage( 'test1',21)
        self.assertIsNone( val ,"Last bookmark at 20")

    def test_delbookmark_no_book( self):
        self.obj.delete( book='junk', bookmark='test01')

if __name__ == "__main__":
    unittest.main()
