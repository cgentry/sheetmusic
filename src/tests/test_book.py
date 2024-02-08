"""
Test frame: book

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116
import logging
import unittest
import os
import tempfile

# sys.path.append("../")

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.setup import Setup
from qdil.book import DilBook

#pylint: disable=C0115
#pylint: disable=C0116
class TestBook(unittest.TestCase):

    def setUp(self):
        db = ':memory:'
        #db = '/tmp/test.sql'
        DbConn().open_db( db )
        s = Setup(db)
        s.drop_tables()
        s.create_tables()
        del s
        self.dlbook = DilBook()
        self.dlbook.show_stack(False)
        self.dlbook.logger.setlevel(logging.CRITICAL)
        self.query = QSqlQuery(DbConn.db())

    def tearDown(self):
        # self.query.exec("DELETE FROM Book")
        pass

    # def test_toml(self):
    #     end_path = os.path.join(
    #         '/tmp', DilBook.CONFIG_TOML_FILE)
    #     id = self.dlbook.add(book="title",
    #               composer="bach", genre="classical",
    #               source="Source", location="/tmp/",
    #               author='Author', publisher='Pub')
    #     self.assertEqual(id, 1)
    #     self.dlbook._load_book_setting('title')

    #     self.assertEqual(self.dlbook._toml_path(),end_path )

    #     # test writing toml out
    #     self.dlbook.save_toml_properties()
    #     self.assertTrue( os.path.isfile( end_path ), 'Confirm file was written')

    #     data_return = self.dlbook.read_toml_properties('/tmp')
    #     self.assertIsInstance(data_return, dict)

    #     self.assertEqual(data_return[BookField.BOOK], 'title')
    #     self.assertEqual(data_return[BookField.COMPOSER], 'bach')
    #     self.assertEqual(data_return[BookField.GENRE], 'classical')
    #     self.assertEqual(data_return[BookField.SOURCE], 'Source')
    #     self.assertEqual(data_return[BookField.AUTHOR], 'Author')
    #     self.assertEqual(data_return[BookField.PUBLISHER], 'Pub')

    #     self.assertTrue( self.dlbook.delete_toml_properties() )
    #     self.assertFalse( os.path.isfile( end_path ), 'Confirm file was deleted')
    #     self.assertFalse( self.dlbook.delete_toml_properties() )



    def test_add_book_dir_empty( self ):
        (status, rec, message ) = self.dlbook.import_directory( None )
        self.assertFalse( status )
        self.assertEqual( len( rec), 0 )
        self.assertEqual( message,"Location is empty" )

    def test_add_book_directory( self ):
        with tempfile.TemporaryDirectory('dbbook') as tdir:
            (status, rec, message ) = self.dlbook.import_directory( tdir )
            self.assertTrue( status, 'Directory exists but error occured' )
            self.assertEqual( len( rec), 0 )
            self.assertEqual( message,"No new records found" )

    def test_add_book_directory2( self ):
        image_path = ""
        with tempfile.TemporaryDirectory('dbbook') as tdir:
            for index in range(1,11):
                image_dir = f'book{index:03d}'
                image_path = os.path.join( tdir , image_dir )
                os.mkdir( image_path )
                for index_image in range(1,11):
                    image_file = f'page{index_image:03d}.png'
                    image_path = os.path.join( tdir, image_dir , image_file )
                    with open(  image_path , "w", encoding="utf-8" ) as fp:
                        fp.flush()

            (status, rec, message) = self.dlbook.import_directory( tdir )
            self.assertTrue( status)
            self.assertEqual( len( rec ), 10 , message )
            self.assertTrue( message.startswith( 'Records added'), message)

            (status, rec, message) = self.dlbook.import_directory( tdir )
            self.assertEqual( len( rec) , 0 , message)
            self.assertTrue( message.startswith( 'Book already in library'), message )


        for index in range(1,11):
            book_name = f'book{index:03d}'
            self.assertTrue(
                self.dlbook.is_book( book_name ) ,
                f'***** BOOK NOT FOUND: {book_name}')
