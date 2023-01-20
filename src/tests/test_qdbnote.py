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
import logging

sys.path.append("../")
from qdb.dbconn     import DbConn
from qdb.dbnote import DbNote
from qdb.setup      import Setup
from qdb.keys       import NOTE
from PySide6.QtSql  import QSqlQuery
from PySide6.QtCore import QSize, QByteArray

NOTE_TEST_DB = ':memory:'
class TestDbBookmark(unittest.TestCase):
    def glue( self, query:QSqlQuery , bulkdata:dict ):
        for row in bulkdata:
            for key in row:
                query.addBindValue( row[key])
            if not query.exec():
                print("Query failed for",  query.lastError())
            

    def setUp(self):
        db = DbConn.openDB(NOTE_TEST_DB)
        self.setup = Setup(NOTE_TEST_DB)
        self.setup.dropTables()
        self.setup.createTables()
        query = QSqlQuery( db )
    
        bkData = [
                {'book': 'test1', 'location': '/loc', 'source': '/src'},
                {'book': 'test2', 'location': '/loc', 'source': '/src'},
        ]
        bkNoteData = [
                {'book_id': 1, 'note': 'note.1.0.0', 'page': 0 , 'sequence': 0},
                {'book_id': 1, 'note': 'note.1.1.0', 'page': 1 , 'sequence': 0},
                {'book_id': 2, 'note': 'note.2.2.0', 'page': 2 , 'sequence': 0},
                {'book_id': 2, 'note': 'note.2.2.1', 'page': 2 , 'sequence': 1},
                {'book_id': 2, 'note': 'note.2.3.0', 'page': 3 , 'sequence': 0},
        ]
        query.prepare("INSERT INTO Book ( book,location,source) VALUES( ? ,? ,?)" )
        self.glue( query , bkData )

        query.prepare( "INSERT INTO Note ( book_id,note,page,sequence) VALUES( ?,?,?,?)" )
        self.glue( query, bkNoteData )

        self.obj = DbNote()
        self.obj.showStack(False)
        self.obj.logger.setLevel( logging.CRITICAL )

    def tearDown(self):
        # (_, cursor) = DbConn().openDB()
        # cursor.execute('DROP TABLE IF EXISTS Bookmark')
        # = DbConn().openDB(close=True)
        pass

    def test_getNote_t1(self):
        note = self.obj.getNote( 1 ,0,0 )
        self.assertIsNotNone( note , 'Database returned no data')
        self.assertEqual( note[NOTE.note] , 'note.1.0.0')

    def test_getNoteForBook(self ):
        note = self.obj.getNoteForBook( 1 )
        self.assertIsNotNone( note , 'Database returned no data')
        self.assertEqual( note[NOTE.note] , 'note.1.0.0')

    def test_getNote_t2(self):
        note = self.obj.getNote( 2, 2, 1 )
        self.assertEqual( note[NOTE.note] , 'note.2.2.1')

    def test_getNoteAll(self):
        notes = self.obj.getAll( 2,2)
        self.assertEqual( len(notes), 2 )
        self.assertEqual( self.obj.count( 2, 2) , 2)

    def test_deletePage( self ):
        self.assertTrue( self.obj.deletePage( 1 , 0, 0 ) )
        note = self.obj.getNote( 1 ,0,0 )
        self.assertTrue( NOTE.id not in note )
        self.assertFalse( self.obj.deletePage( 1 , 0, 0 ) )

    def test_DeleteAllPageNotes( self ):
        self.assertTrue( self.obj.deleteAllPageNotes( 2, 2 ))
        notes = self.obj.getAll( 2,2)
        self.assertEqual( len(notes), 0 )

    def test_Update(self):
        note = self.obj.getNoteForBook( 1 )
        note[NOTE.note] = 'updated'
        note[NOTE.location] = "location"
        note[NOTE.size] = 'new size'

        self.obj.update(note)
        note = self.obj.getNoteForBook(1)
        self.assertEqual( 'updated' , note[NOTE.note])
        self.assertEqual( 'location' , note[NOTE.location])
        self.assertEqual( 'new size' , note[NOTE.size])
    
    def test_coding( self ):
        rtnValue = self.obj.decode( self.obj.encode( "Silly value"))
        self.assertEqual( rtnValue , 'Silly value')
        q = QSize(10,20)
        self.assertIsInstance( q , QSize )
        self.assertEqual( q.height() , 20)
        self.assertEqual( q.width() , 10 )

        qtest = self.obj.decode( self.obj.encode( q ) )
        self.assertIsInstance( qtest , QSize )
        self.assertEqual( qtest.height() , 20)
        self.assertEqual( qtest.width() , 10 )

        self.assertEqual( self.obj.encode( None ), None)
        self.assertEqual( self.obj.encode( '') , None)
        self.assertIsNone( self.obj.decode( None ))
        self.assertIsNone( self.obj.decode( '' ))

    def test_new(self):
        note = self.obj.new( "add", 3, 4 , 5 , 'location', 'size')
        self.assertEqual( note[NOTE.book_id ], 3 )
        self.assertEqual( note[NOTE.page ], 4 )
        self.assertEqual( note[NOTE.seq ], 5 )
        self.assertEqual( note[NOTE.location ], self.obj.encode( 'location'))
        self.assertEqual( note[NOTE.size ], self.obj.encode('size'))
    
    def test_add(self):
        note = self.obj.new( "add", book_id=4, loc='location' , size='size' )
        self.assertGreater( self.obj.add( note ) , 3 )
        dbnote = self.obj.getNote( 4 )
        self.assertEqual( dbnote[NOTE.note] , 'add')
        self.assertEqual( self.obj.decode( dbnote[ NOTE.location ]), 'location')
        self.assertEqual( self.obj.decode( dbnote[ NOTE.size ]), 'size')
        self.assertEqual( dbnote[NOTE.page] , 0)
        self.assertEqual( dbnote[NOTE.seq] , 0)

    def test_addPage(self):
        self.assertEqual( self.obj.count( 2, 2) , 2)

        note = self.obj.new( "add-note3", book_id=2, page=2, loc='location' , size='size' )
        self.assertGreater( self.obj.addPage( note ) , 3 )
        self.assertEqual( self.obj.count( 2,2), 3 )

        dbnote = self.obj.getNote( book=2,page=2, seq=2 )
        self.assertIsNotNone( dbnote )
        self.assertGreaterEqual( len( dbnote ), 5)
        self.assertEqual( dbnote[NOTE.note] , 'add-note3')
        self.assertEqual( self.obj.decode( dbnote[ NOTE.location ]), 'location')
        self.assertEqual( self.obj.decode( dbnote[ NOTE.size ])    , 'size')
        self.assertEqual( dbnote[NOTE.page] , 2)
        self.assertEqual( dbnote[NOTE.seq]  , 2)

    def test_addPageError_no_book_id(self):
        note = self.obj.new( "add-note3", book_id=None, page=2, loc='location' , size='size' )
        with self.assertRaises( ValueError) : 
            self.obj.addPage( note )
        note[ NOTE.book_id ] = 0
        with self.assertRaises( ValueError):
            self.obj.addPage( note )
        
        note[ NOTE.book_id ] = 1
        note[ NOTE.page ] = None
        with self.assertRaises( ValueError):
            self.obj.addPage( note )

    def test_page_count(self):
        rc = self.obj.notePageList( 2 )
        self.assertEqual( len(rc), 2, "Book 2")

        rc = self.obj.notePageList( 1 )
        self.assertEqual( len(rc), 2,"Book 1")

        rc = self.obj.notePageList( 3 )
        self.assertEqual( len(rc), 0,"Book 3")
        

if __name__ == "__main__":
    unittest.main()
