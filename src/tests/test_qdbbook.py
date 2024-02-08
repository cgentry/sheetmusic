"""
Test frame

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import logging
import unittest
#sys.path.append("../")

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.dbbook import ( DbBook, DbGenre, DbComposer, Migrate )
from qdb.setup import Setup

#pylint: disable=C0116
class TestMigrate(unittest.TestCase ):
    """Standard test frame for qdb.DbBook
    """
    def setUp( self ):
        DbConn().open_db( ':memory:')
        s = Setup(":memory:")
        s.drop_tables()
        s.create_tables()
        del s
        self.dbbook = DbBook()
        self.dbbook.show_stack(False)
        self.dbbook.logger.setlevel( logging.CRITICAL )
        self.query = QSqlQuery( DbConn.db() )
        self.migrate = Migrate()

    def tearDown(self):
        self.query.exec("DELETE FROM Book")

    def test_edit_composer(self):
        new_value = 'Bach, J.S.'
        self.dbbook.add(book="title1",
                        composer="bach",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.dbbook.add(book="title2",
                        composer="bach",
                        genre="ensemble",
                        source="Source",
                        location="loc")
        self.dbbook.add(book="title3",
                        composer="Handel",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.assertEqual( self.dbbook.count(), 3 )

        rtn = self.migrate.composers('bach', new_value)
        self.assertEqual( rtn , 2 ,'How many composer records changed')

        rtn = DbComposer().get_all() #ordered by name
        self.assertEqual( rtn[0], "bach" )
        self.assertEqual( rtn[2], 'Handel' )
        self.assertEqual( rtn[1], new_value ) #Bach, J.S.

        rtn = self.migrate.composers('bach', None )
        self.assertEqual( rtn , 0 )

    def test_edit_genre(self):
        new_value = 'pop'
        self.dbbook.add(book="title1",
                        composer="bach",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.dbbook.add(book="title2",
                        composer="bach",
                        genre="ensemble",
                        source="Source",
                        location="loc")
        self.dbbook.add(book="title3",
                        composer="handel",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.assertEqual( self.dbbook.count(), 3 )

        rtn = self.migrate.genres('classical', new_value)
        self.assertEqual( rtn , 2 ,'how many genre records changed')

        rtn = DbGenre().get_all()                # Ordered by name
        self.assertEqual( len( rtn ), 3)
        self.assertEqual( rtn[1], 'ensemble' )
        self.assertEqual( rtn[2], new_value ) #pop

class TestDbBook(unittest.TestCase):
    """Standard test frame for qdb.DbBook
    """
    def setUp( self ):
        DbConn().open_db( ':memory:')
        s = Setup(":memory:")
        s.drop_tables()
        s.create_tables()
        del s
        self.dbbook = DbBook()
        self.dbbook.show_stack(False)
        self.dbbook.logger.setlevel( logging.CRITICAL )
        self.query = QSqlQuery( DbConn.db() )

    def tearDown(self):
        self.query.exec("DELETE FROM Book")

    def test_add(self):
        book_id = self.dbbook.add(book="title1",
                                  composer="bach",
                                  genre="classical",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )

        bk = self.dbbook.getbook_byid( book_id )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title1")
        self.assertEqual( bk['name_default'], 0 )

        bk = self.dbbook.getbook( book="title1" )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title1")
        self.assertEqual( bk["composer"] , "bach")
        self.assertEqual( bk["genre"] , "classical")
        self.assertEqual( bk["source"] , "Source")
        self.assertEqual( bk["location"] , 'loc')
        self.assertEqual( bk['name_default'], 0 )

    def test_getbook_bycolumn(self):
        book_id = self.dbbook.add(book="title1",
                                  composer="bach",
                                  genre="classical",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )

        book = self.dbbook.getbook_bycolumn('source', 'Source')
        self.assertEqual( book['book'], 'title1')

        book = self.dbbook.getbook_bycolumn('location', 'loc')
        self.assertEqual( book['book'], 'title1')

    def test_incomplete_book_no_page(self):
        book_id = self.dbbook.add(book="title1",
                                  composer="bach",
                                  genre="classical",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )

        booklist = self.dbbook.get_incomplete_books()
        self.assertEqual( len(booklist), 1 )
        self.assertEqual( booklist.keys(), {'title1'})
        self.assertEqual( len( booklist['title1']), 1 )
        self.assertEqual( booklist['title1'][0],"numbering: Page numbering isn't set" )

    def test_incomplete_book_no_composer_genre(self):
        book_id = self.dbbook.add(book="title1",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )
        booklist = self.dbbook.get_incomplete_books()
        self.assertEqual( len(booklist), 1 )
        self.assertEqual( booklist.keys(), {'title1'})
        self.assertEqual( len( booklist['title1']), 1 )
        self.assertEqual( booklist['title1'][0],"numbering: Page numbering isn't set" )

    def test_incomplete_book_default_composer_genre_with_page(self):
        book_id = self.dbbook.add(book="title1",
                                  numbering_ends=10,
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )
        booklist = self.dbbook.get_incomplete_books()
        self.assertEqual( len(booklist), 0 )

    def test_incomplete_book_default_name(self):
        book_id = self.dbbook.add(book="title1",
                                  name_default=1,
                                  composer='Handle',
                                  genre='classical',
                                  numbering_ends=10,
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )
        booklist = self.dbbook.get_incomplete_books()
        self.assertEqual( len(booklist), 1 )
        self.assertEqual( booklist.keys(), {'title1'})
        self.assertEqual( len( booklist['title1']), 1 )
        self.assertEqual( booklist['title1'][0], 'name: Default name used is "title1"' )

    def test_update( self ):
        book_id = self.dbbook.add(book="title2",
                                  composer="Handel",
                                  genre="classical",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )

        bk = self.dbbook.getbook( book='title2' )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title2")
        self.assertEqual( bk["composer"] , "Handel")

        rtn = self.dbbook.update( book='title2', composer="Brahms")
        self.assertEqual( rtn , 1 )

        rtn = self.dbbook.update( book='title2', composer="Brahms")

        bk = self.dbbook.getbook( book='title2' )
        self.assertIsNotNone( bk )
        self.assertEqual( bk["book"] , "title2")
        self.assertEqual( bk["composer"] , "Brahms")

    def test_update_book_name( self ):
        new_title = 'new_title'
        book_id = self.dbbook.add(book="title2",
                                  composer="Handel",
                                  genre="classical",
                                  source="Source",
                                  location="loc")
        self.assertEqual( book_id , 1 )
        change_list = {'book': 'title2', 'location': 'newloc', '*book': new_title }
        self.dbbook.update( **change_list )

        self.assertTrue( self.dbbook.is_book( new_title ))
        self.assertFalse( self.dbbook.is_book( 'title2' ))

        self.dbbook.update_name( new_title , 'title2')
        self.assertFalse( self.dbbook.is_book( new_title ))
        self.assertTrue( self.dbbook.is_book( 'title2' ))

    def test_del_book(self):
        rtn = self.dbbook.add(book="title1",
                              composer="bach",
                              genre="classical",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        rtn = self.dbbook.del_book("title1")
        self.assertTrue( rtn )
        bk = self.dbbook.getbook( book="title1"  )
        self.assertIsNone( bk )

    def test_delete_all(self):
        rtn = self.dbbook.add(book="title1",
                              composer="bach",
                              genre="classical",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        self.assertEqual( self.dbbook.count(), 1 )
        rtn = self.dbbook.add(book="title2",
                              composer="minogue",
                              genre="pop",
                              source="Source",
                              location="loc")
        self.assertEqual( self.dbbook.count(), 2 )
        self.assertTrue( rtn )

        self.assertTrue( self.dbbook.delete_all() )
        self.assertEqual( self.dbbook.count(), 0)
        self.assertIsNone( self.dbbook.getbook( book="title1"  ) )
        self.assertIsNone( self.dbbook.getbook( book="title2"  ) )

    def test_get_composer_genre(self):
        rtn = self.dbbook.add(book="title1",
                              composer="mozart",
                              genre="classical",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        rtn = self.dbbook.add(book="title1b",
                              composer="mozart",
                              genre="opera",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        rtn = self.dbbook.add(book="title2",
                              composer="minogue",
                              genre="pop",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        rtn = self.dbbook.add(book="title3",
                              composer="bell",
                              genre="jazz",
                              source="Source",
                              location="loc")
        self.assertTrue( rtn )
        self.assertEqual( self.dbbook.count(), 4 )

        rtn =  DbComposer().get_all()
        self.assertEqual( len( rtn), 3)
        self.assertEqual( rtn[0], 'bell')
        self.assertEqual( rtn[1], 'minogue')
        self.assertEqual( rtn[2], 'mozart')

        rtn = DbComposer().get_all(sequence='DESC')
        self.assertEqual( rtn[2], 'bell')
        self.assertEqual( rtn[1], 'minogue')
        self.assertEqual( rtn[0], 'mozart')

        rtn = DbGenre().get_all()
        self.assertEqual( len(rtn), 4)
        self.assertEqual( rtn[0], 'classical')
        self.assertEqual( rtn[1], 'jazz')
        self.assertEqual( rtn[2], 'opera')
        self.assertEqual( rtn[3], 'pop')

    def test_get_all(self):
        rtn = self.dbbook.add(book="title1",
                              composer="bach",
                              genre="classical",
                              source="Source",
                              location="loc1")
        self.assertTrue( rtn )
        self.assertEqual( self.dbbook.count(), 1 )
        rtn = self.dbbook.add(book="title2",
                              composer="bach",
                              genre="classical",
                              source="Source",
                              location="loc2")
        self.assertEqual( self.dbbook.count(), 2 )

        bk = self.dbbook.get_all()
        self.assertEqual( len(bk), 2 )
        self.assertEqual( bk[0]['book'], 'title1')
        self.assertEqual( bk[1]['book'], 'title2')

        rtn = self.dbbook.get_all( fetchall=False)
        self.assertTrue( rtn.next() )
        self.assertEqual( rtn.value( 'book'), 'title1')
        self.assertTrue( rtn.next() )
        self.assertEqual( rtn.value( 'book'), 'title2')
        rtn.finish()
        del rtn

        rows = self.dbbook.get_all( )
        self.assertEqual( len(rows), 2 )
        self.assertEqual( rows[0]['location'] , 'loc1')
        self.assertEqual( rows[1]['location'] , 'loc2')

    def test_duplicate_insert(self):
        self.assertEqual( self.dbbook.add(book="title1",
                                          composer="bach",
                                          genre="classical",
                                          source="Source",
                                          location="loc") , 1 )
        self.assertEqual(self.dbbook.add(book="title1",
                                         composer="bach",
                                         genre="classical",
                                         source="Source",
                                         location="loc"), -1 )
        self.assertTrue( self.dbbook.is_error() )
        self.assertEqual( self.dbbook.count(), 1 )

    def test_upsert_exists(self):
        self.dbbook.add(book="title1",
                        composer="bach",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.dbbook.upsert_book(book="title1",
                                composer="handel",
                                genre="classical",
                                source="Source",
                                location="loc")
        self.assertEqual( self.dbbook.count(), 1 )
        bk = self.dbbook.getbook(book='title1')
        self.assertEqual( bk['composer'], 'handel')

    def test_upsert_not_exists(self):
        self.dbbook.upsert_book(book="title1",
                                composer="handel",
                                genre="classical",
                                source="Source",
                                location="loc")
        self.assertEqual( self.dbbook.count(), 1 )

    def test_is_book(self):
        self.dbbook.upsert_book(book="title1",
                                composer="handel",
                                genre="classical",
                                source="Source",
                                location="loc")
        self.assertEqual( self.dbbook.count(), 1 )
        self.assertTrue( self.dbbook.is_book('title1'))
        self.assertFalse( self.dbbook.is_book('title2'))
        self.assertFalse( self.dbbook.is_book( None))

    def test_is_location( self ):
        self.dbbook.add(book="title1",
                        composer="Handel",
                        genre="classical",
                        source="Source",
                        location="loc")
        self.assertEqual( self.dbbook.count(), 1 )
        self.assertTrue(  self.dbbook.is_location('loc'))
        self.assertFalse( self.dbbook.is_location('noloc'))
        self.assertFalse( self.dbbook.is_location( None))
        self.assertFalse( self.dbbook.is_location( ''))



if __name__ == "__main__":
    unittest.main()
