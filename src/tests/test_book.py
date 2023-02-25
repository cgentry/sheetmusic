import logging
import unittest
import os

# sys.path.append("../")

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdil.book import DilBook
from qdb.setup import Setup
from qdb.keys import BOOK


class TestBook(unittest.TestCase):
    def setUp(self):
        db = ':memory:'
        #db = '/tmp/test.sql'
        DbConn().openDB( db )
        s = Setup(db)
        s.dropTables()
        s.createTables()
        del s
        self.book = DilBook()
        self.book.showStack(False)
        self.book.logger.setLevel(logging.CRITICAL)
        self.query = QSqlQuery(DbConn.db())

    def tearDown(self):
        # self.query.exec("DELETE FROM Book")
        pass

    # def test_toml(self):
    #     end_path = os.path.join(
    #         '/tmp', DilBook.CONFIG_TOML_FILE)
    #     id = self.book.add(book="title", composer="bach", genre="classical",
    #                            source="Source", location="/tmp/", author='Author', publisher='Pub')
    #     self.assertEqual(id, 1)
    #     self.book._load_book_setting('title')

    #     self.assertEqual(self.book._toml_path(),end_path )

    #     # test writing toml out
    #     self.book.save_toml_config()
    #     self.assertTrue( os.path.isfile( end_path ), 'Confirm file was written')

    #     data_return = self.book.read_toml_properties('/tmp')
    #     self.assertIsInstance(data_return, dict)

    #     self.assertEqual(data_return[BOOK.book], 'title')
    #     self.assertEqual(data_return[BOOK.composer], 'bach')
    #     self.assertEqual(data_return[BOOK.genre], 'classical')
    #     self.assertEqual(data_return[BOOK.source], 'Source')
    #     self.assertEqual(data_return[BOOK.author], 'Author')
    #     self.assertEqual(data_return[BOOK.publisher], 'Pub')

    #     self.assertTrue( self.book.delete_toml_config() )
    #     self.assertFalse( os.path.isfile( end_path ), 'Confirm file was deleted')
    #     self.assertFalse( self.book.delete_toml_config() )



    def test_add_book_dir_empty( self ):
        (status, rec, message ) = self.book.import_directory( None )
        self.assertFalse( status )
        self.assertEqual( len( rec), 0 )
        self.assertEqual( message,"Location is empty" )

    def test_add_book_directory( self ):
        import tempfile
        import os
        
        imagePath = ""
        with tempfile.TemporaryDirectory('dbbook') as tdir:
            (status, rec, message ) = self.book.import_directory( tdir )
            self.assertFalse( status )
            self.assertEqual( len( rec), 0 )
            self.assertEqual( message,"No new records found" )

    def test_add_book_directory( self ):
        import tempfile
        import os
        
        imagePath = ""
        with tempfile.TemporaryDirectory('dbbook') as tdir:
            for index in range(1,11):
                imageDir = 'book{:03d}'.format( index )
                imagePath = os.path.join( tdir , imageDir )
                os.mkdir( imagePath )
                for indexImage in range(1,11):
                    imageFile = 'page{:03d}.png'.format( indexImage )
                    imagePath = os.path.join( tdir, imageDir , imageFile )
                    fp = open(  imagePath , "w")
                    fp.close()

            (status, rec, message) = self.book.import_directory( tdir )
            self.assertTrue( status)
            self.assertEqual( len( rec ), 10 , message )
            self.assertTrue( message.startswith( 'Records added'), message)

            (status, rec, message) = self.book.import_directory( tdir )
            self.assertEqual( len( rec) , 0 , message)
            self.assertTrue( message.startswith( 'Book already in library'), message )


        for index in range(1,11):
                book_name = 'book{:03d}'.format( index )
                self.assertTrue( self.book.isBook( book_name ) , '***** BOOK NOT FOUND: {}'.format( book_name))
        
