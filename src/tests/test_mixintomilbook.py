"""
Test frame: MixinTomlBook

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import unittest
import tempfile
import os
from datetime import datetime, date

from qdb.mixin.tomlbook import MixinTomlBook
from qdb.dbconn    import DbConn
from qdb.fields.book import BookField
from qdb.setup import Setup


class TestMixinTomlBook(unittest.TestCase):

    def setUp(self):
        DbConn().open_db( ':memory:')
        s = Setup(":memory:")
        s.drop_tables()
        s.create_tables()
        del s
        self.obj = MixinTomlBook()

    def test_simple_roundtrip( self ):
        data = {}
        for index , key in enumerate( MixinTomlBook.VALID_TOML_KEYS):
            data[ key ] = f"DATA{index}"

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist')

            with open(fname, "r", encoding="utf-8" ) as f:
                toml = f.read()
                # check all the keys are there
                self.assertGreater( len(toml), 0 , 'File too short' )
                for index, key in enumerate( MixinTomlBook.VALID_TOML_KEYS ):
                    self.assertTrue( key in toml, key )

            toml2 = self.obj.read_toml_properties( fname )
            # check all values are there
            for key, value in data.items():
                self.assertTrue( key in toml2 , f'Key "{key}" not in toml')
                self.assertEqual( data[ key ], value, f'Value "{value}" is not in toml' )

    def test_different_types( self ):
        data = {}
        data[ BookField.NUMBER_STARTS ] = datetime.now()
        data[ BookField.PUBLISHER ] = date.today()
        data[ BookField.TITLE] = 'title'     # string
        data[ BookField.LAST_READ] = 1.5      # float
        data[ BookField.AUTHOR]   = [ 'a','b','c']
        data[ BookField.COMPOSER ] = True

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist')
            with open(fname, "r", encoding="utf-8" ) as f:
                toml = f.read()
                self.assertGreater( len(toml), 0 , 'File too short' )
                for key in data:
                    self.assertTrue( key in toml, key )

            toml2 = self.obj.read_toml_properties( fname )
            self.assertEqual( len(data.keys()) , len(toml2.keys()))
            for key, value in toml2.items():
                self.assertTrue( key in data , f'Key {key} not found')
                self.assertEqual( value , data[ key ])
            self.assertIsInstance( data[ BookField.TITLE ], str )

            self.assertIsInstance( toml2[ BookField.TITLE ], str )
            self.assertIsInstance( data[ BookField.LAST_READ ], float )

            self.assertIsInstance( toml2[ BookField.AUTHOR ], list )
            self.assertIsInstance( data[ BookField.AUTHOR ], list )
            self.assertEqual( len( toml2[BookField.AUTHOR] ) , 3 )
            self.assertEqual( len( toml2[BookField.AUTHOR]  ), len( data[BookField.AUTHOR] ) )

            self.assertIsInstance( toml2[ BookField.COMPOSER ], bool )
            self.assertIsInstance( data[ BookField.COMPOSER ], bool )

            self.assertIsInstance( toml2[ BookField.NUMBER_STARTS ], datetime )
            self.assertIsInstance( data[ BookField.NUMBER_STARTS ], datetime )

            self.assertIsInstance( toml2[ BookField.PUBLISHER ], date )
            self.assertIsInstance( data[ BookField.PUBLISHER ], date )

    def test_filter( self ):
        data = {
            'alpha' : "DATA-alpha",
            'beta'  : "DATA-beta",
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist')
            with open(fname, "r", encoding="utf-8" ) as f:
                toml = f.read()
                self.assertGreater( len(toml), 0 , 'File too short' )

            toml2 = self.obj.read_toml_properties( fname )
            self.assertEqual( len( toml2 ),0)

    def test_delete( self ):
        data = {}
        data[ 'alpha' ] = "DATA-alpha"

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist')
            self.assertTrue( self.obj.delete_toml_properties( fname ))
            self.assertFalse(os.path.isfile( fname ), f'Filename {fname} exists')
