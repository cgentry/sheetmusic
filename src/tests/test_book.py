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
        DbConn().openDB(':memory:')
        s = Setup(":memory:")
        s.dropTables()
        s.createTables()
        del s
        self.book = DilBook()
        self.book.showStack(False)
        self.book.logger.setLevel(logging.CRITICAL)
        self.query = QSqlQuery(DbConn.db())

    def tearDown(self):
        self.query.exec("DELETE FROM Book")
        pass

    def test_toml(self):
        id = self.book.addBook(book="title", composer="bach", genre="classical",
                               source="Source", location="/tmp/", author='Author', publisher='Pub')
        self.assertEqual(id, 1)
        self.book._load_book_setting('title')

        self.assertEqual(self.book._toml_path(), os.path.join(
            '/tmp', DilBook.CONFIG_TOML_FILE))
        # test writing toml out
        self.book.save_toml_config()

        data_return = self.book.read_toml_properties('/tmp')
        self.assertIsInstance(data_return, dict)

        self.assertEqual(data_return[BOOK.book], 'title')
        self.assertEqual(data_return[BOOK.composer], 'bach')
        self.assertEqual(data_return[BOOK.genre], 'classical')
        self.assertEqual(data_return[BOOK.source], 'Source')
        self.assertEqual(data_return[BOOK.author], 'Author')
        self.assertEqual(data_return[BOOK.publisher], 'Pub')

    # def test_add_book_directory( self ):
    #     import tempfile
    #     import os
    #     (rec, message ) = self.book.import_book_directory( None )
    #     self.assertFalse( rec )
    #     self.assertEqual( message,"Location is empty" )
    #     imagePath = ""
    #     with tempfile.TemporaryDirectory('dbbook') as tdir:
    #         (rec, message ) = self.book.addBookDirectory( tdir )
    #         self.assertFalse( rec )
    #         self.assertEqual( message,"No new records found" )
    #         for index in range(1,11):
    #             imageDir = 'book{:03d}'.format( index )
    #             imagePath = os.path.join( tdir , imageDir )
    #             os.mkdir( imagePath )
    #             for indexImage in range(1,11):
    #                 imageFile = 'page{:03d}.png'.format( indexImage )
    #                 imagePath = os.path.join( tdir, imageDir , imageFile )
    #                 fp = open(  imagePath , "w")
    #                 fp.close()

    #         (rec, message) = self.book.addBookDirectory( tdir )
    #         self.assertEqual( True , rec , message)
    #         self.assertTrue( message.startswith( 'Records added'))

    #         (rec, message) = self.book.addBookDirectory( tdir )
    #         self.assertFalse( rec , message)
    #         self.assertTrue( message.startswith( 'No new records'))

    #         ( rec, message ) = self.book.addBookDirectory( imagePath )
    #         self.assertFalse( rec , message)
    #         self.assertTrue( message.startswith( "Location '"))

    #     for index in range(1,11):
    #             imageDir = 'book{:03d}'.format( index )
    #             self.book.isBook( imageDir )
    #     (rec, message ) = self.book.addBookDirectory( tdir )
