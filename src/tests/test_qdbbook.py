
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

import logging
import unittest
#sys.path.append("../")

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.dbbook import DbBook, DbGenre, DbComposer
from qdb.setup import Setup


class TestDbBook(unittest.TestCase):
    def setUp( self ):
        DbConn().openDB( ':memory:')
        s = Setup(":memory:")
        s.dropTables()
        s.createTables()
        del s
        self.book = DbBook()
        self.book.showStack(False)
        self.book.logger.setlevel( logging.CRITICAL )
        self.query = QSqlQuery( DbConn.db() )
    
    def tearDown(self):
        self.query.exec("DELETE FROM Book")
        pass

    def test_add(self):
        from qdb.dbbooksettings import DbBookSettings
        id = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.assertEqual( id , 1 )
       
        bk = self.book.getBookById( id )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title1")
        self.assertEqual( bk['name_default'], 0 )

        bk = self.book.getBook( book="title1" )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title1")
        self.assertEqual( bk["composer"] , "bach")
        self.assertEqual( bk["genre"] , "classical")
        self.assertEqual( bk["source"] , "Source")
        self.assertEqual( bk["location"] , 'loc')
        self.assertEqual( bk['name_default'], 0 )

    def test_getBookByColumn(self):
        from qdb.dbbooksettings import DbBookSettings
        id = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.assertEqual( id , 1 )

        book = self.book.getBookByColumn('source', 'Source')
        self.assertEqual( book['book'], 'title1')
    
        book = self.book.getBookByColumn('location', 'loc')
        self.assertEqual( book['book'], 'title1')

    def test_incomplete_book_no_page(self):
        id = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.assertEqual( id , 1 )
       
        list = self.book.getIncompleteBooks()
        self.assertEqual( len(list), 1 )
        self.assertEqual( list.keys(), {'title1'})
        self.assertEqual( len( list['title1']), 1 )
        self.assertEqual( list['title1'][0],"numbering: Page numbering isn't set" )
    
    def test_incomplete_book_no_composer_genre(self):
        id = self.book.add(book="title1", source="Source",location="loc")
        self.assertEqual( id , 1 )
        list = self.book.getIncompleteBooks()
        self.assertEqual( len(list), 1 )
        self.assertEqual( list.keys(), {'title1'})
        self.assertEqual( len( list['title1']), 1 )
        self.assertEqual( list['title1'][0],"numbering: Page numbering isn't set" )
    
    def test_incomplete_book_default_composer_genre_with_page(self):
        id = self.book.add(book="title1", numbering_ends=10,source="Source",location="loc")
        self.assertEqual( id , 1 )
        list = self.book.getIncompleteBooks()
        self.assertEqual( len(list), 0 )

    def test_incomplete_book_default_name(self):
        id = self.book.add(book="title1", name_default=1, composer='Handle', genre='classical', numbering_ends=10,source="Source",location="loc")
        self.assertEqual( id , 1 )
        list = self.book.getIncompleteBooks()
        self.assertEqual( len(list), 1 )
        self.assertEqual( list.keys(), {'title1'})
        self.assertEqual( len( list['title1']), 1 )
        self.assertEqual( list['title1'][0], 'name: Default name used is "title1"' )
           
    def test_update( self ):
        id = self.book.add(book="title2",composer="Handel", genre="classical", source="Source",location="loc")
        self.assertEqual( id , 1 )
        
        bk = self.book.getBook( book='title2' )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title2")
        self.assertEqual( bk["composer"] , "Handel")

        rtn = self.book.update( book='title2', composer="Brahms")
        self.assertEqual( rtn , 1 )

        rtn = self.book.update( book='title2', composer="Brahms")
        
        bk = self.book.getBook( book='title2' )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title2")
        self.assertEqual( bk["composer"] , "Brahms")

    def test_updateBook_name( self ):
        newTitle = 'newTitle'
        id = self.book.add(book="title2",composer="Handel", genre="classical", source="Source",location="loc")
        self.assertEqual( id , 1 )
        changeList = {'book': 'title2', 'location': 'newloc', '*book': newTitle }
        self.book.update( **changeList )

        self.assertTrue( self.book.isBook( newTitle ))
        self.assertFalse( self.book.isBook( 'title2' ))

        self.book.updateName( newTitle , 'title2')
        self.assertFalse( self.book.isBook( newTitle ))
        self.assertTrue( self.book.isBook( 'title2' ))
        
    def test_delBook(self):
        rtn = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.assertTrue( rtn )
        rtn = self.book.delBook("title1")
        self.assertTrue( rtn )
        bk = self.book.getBook( book="title1"  )
        self.assertIsNone( bk )

    def test_delAllBooks(self):
        rtn = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.assertTrue( rtn )
        self.assertEqual( self.book.count(), 1 )
        rtn = self.book.add(book="title2",composer="minogue", genre="pop", source="Source",location="loc")
        self.assertEqual( self.book.count(), 2 )
        self.assertTrue( rtn )

        self.assertTrue( self.book.delAllBooks() )
        self.assertEqual( self.book.count(), 0)
        self.assertIsNone( self.book.getBook( book="title1"  ) )
        self.assertIsNone( self.book.getBook( book="title2"  ) )

    def test_getComposerGenre(self):
        rtn = self.book.add(book="title1",composer="mozart", genre="classical", source="Source",location="loc")
        self.assertTrue( rtn )
        rtn = self.book.add(book="title1b",composer="mozart", genre="opera", source="Source",location="loc")
        self.assertTrue( rtn )
        rtn = self.book.add(book="title2",composer="minogue", genre="pop", source="Source",location="loc")
        self.assertTrue( rtn )
        rtn = self.book.add(book="title3",composer="bell", genre="jazz", source="Source",location="loc")
        self.assertTrue( rtn )
        self.assertEqual( self.book.count(), 4 )

        rtn =  DbComposer().getall() 
        self.assertEqual( len( rtn), 3)
        self.assertEqual( rtn[0], 'bell')
        self.assertEqual( rtn[1], 'minogue')
        self.assertEqual( rtn[2], 'mozart')

        rtn = DbComposer().getall(sequence='DESC') 
        self.assertEqual( rtn[2], 'bell')
        self.assertEqual( rtn[1], 'minogue')
        self.assertEqual( rtn[0], 'mozart')

        rtn = DbGenre().getall() 
        self.assertEqual( len(rtn), 4)
        self.assertEqual( rtn[0], 'classical')
        self.assertEqual( rtn[1], 'jazz')
        self.assertEqual( rtn[2], 'opera')
        self.assertEqual( rtn[3], 'pop')

    def test_getAll(self):
        rtn = self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc1")
        self.assertTrue( rtn )
        self.assertEqual( self.book.count(), 1 )
        rtn = self.book.add(book="title2",composer="bach", genre="classical", source="Source",location="loc2")
        self.assertEqual( self.book.count(), 2 )

        bk = self.book.getAll()
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0]['book'], 'title1')
        self.assertEqual( bk[1]['book'], 'title2')

        rtn = self.book.getAll( fetchall=False)
        self.assertTrue( rtn.next() )
        self.assertEqual( rtn.value( 'book'), 'title1')
        self.assertTrue( rtn.next() )
        self.assertEqual( rtn.value( 'book'), 'title2')
        rtn.finish()
        del rtn

        rows = self.book.getAll( )
        self.assertEqual( len(rows), 2 )
        self.assertEqual( rows[0]['location'] , 'loc1')
        self.assertEqual( rows[1]['location'] , 'loc2')



    def test_edit_composer(self):
        newValue = 'Bach, J.S.'
        self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.book.add(book="title2",composer="bach", genre="ensemble", source="Source",location="loc")
        self.book.add(book="title3",composer="Handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 3 )

        rtn = self.book.editAllComposers('bach', newValue)
        self.assertEqual( rtn , 2 ,'How many composer records changed')

        rtn = DbComposer().getall() #ordered by name
        self.assertEqual( rtn[0], "bach" )
        self.assertEqual( rtn[2], 'Handel' )
        self.assertEqual( rtn[1], newValue ) #Bach, J.S.

        rtn = self.book.editAllComposers('bach', None )
        self.assertEqual( rtn , 0 )

    def test_edit_genre(self):
        newValue = 'pop'
        self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.book.add(book="title2",composer="bach", genre="ensemble", source="Source",location="loc")
        self.book.add(book="title3",composer="handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 3 )

        rtn = self.book.editAllGenres('classical', newValue)
        self.assertEqual( rtn , 2 ,'how many genre records changed')

        rtn = DbGenre().getall()                # Ordered by name
        self.assertEqual( len( rtn ), 3)
        self.assertEqual( rtn[1], 'ensemble' )
        self.assertEqual( rtn[2], newValue ) #pop

    def test_duplicate_insert(self):
        self.assertEqual( self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc") , 1 )
        self.assertEqual(self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc"), -1 )
        self.assertTrue( self.book.isError() )
        self.assertEqual( self.book.count(), 1 )

    def test_upsert_exists(self):
        self.book.add(book="title1",composer="bach", genre="classical", source="Source",location="loc")
        self.book.upsertBook(book="title1",composer="handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 1 )
        bk = self.book.getBook(book='title1')
        self.assertEqual( bk['composer'], 'handel')

    def test_upsert_not_exists(self):
        self.book.upsertBook(book="title1",composer="handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 1 )

    def test_is_book(self):
        self.book.upsertBook(book="title1",composer="handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 1 )
        self.assertTrue( self.book.isBook('title1'))
        self.assertFalse( self.book.isBook('title2'))
        self.assertFalse( self.book.isBook( None))

    def test_is_location( self ):
        self.book.add(book="title1",composer="Handel", genre="classical", source="Source",location="loc")
        self.assertEqual( self.book.count(), 1 )
        self.assertTrue(  self.book.isLocation('loc'))
        self.assertFalse( self.book.isLocation('noloc'))
        self.assertFalse( self.book.isLocation( None))
        self.assertFalse( self.book.isLocation( ''))

    

if __name__ == "__main__":
    unittest.main()
