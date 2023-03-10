# This Python file uses the following encoding: utf-8
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

from qdb.keys import BOOK
import unittest
import tempfile
import os
from qdb.mixin.tomlbook import MixinTomlBook
from datetime import datetime, date

class TestMixinTomlBook(unittest.TestCase):

    def setUp(self):
        self.obj = MixinTomlBook()

    def test_simple_roundtrip( self ):
        data = {}
        for index , key in enumerate( MixinTomlBook.VALID_TOML_KEYS):
            data[ key ] = f"DATA{index}"
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist') 
            with open(fname, "r") as f:
                toml = f.read()
                self.assertGreater( len(toml), 0 , 'File too short' )
                for index, key in enumerate( MixinTomlBook.VALID_TOML_KEYS ):
                    self.assertTrue( toml.__contains__( key ), key )

            toml2 = self.obj.read_toml_properties( fname )
            self.assertEqual( len(data.keys()) , len(toml2.keys()))
            for key, value in toml2.items():
                self.assertTrue( key in data , f'Key {key} not found')
                self.assertEqual( toml2[ key ], data[ key ])

    def test_different_types( self ):
        data = {}
        data[ BOOK.numberStarts ] = datetime.now()
        data[ BOOK.publisher ] = date.today()
        data[ BOOK.title] = 'title'     # string
        data[ BOOK.lastRead] = 1.5      # float
        data[ BOOK.author]   = [ 'a','b','c']
        data[ BOOK.composer ] = True
                 
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist') 
            with open(fname, "r") as f:
                toml = f.read()
                self.assertGreater( len(toml), 0 , 'File too short' )
                for key in data.keys():
                    self.assertTrue( toml.__contains__( key ), key )

            toml2 = self.obj.read_toml_properties( fname )
            self.assertEqual( len(data.keys()) , len(toml2.keys()))
            for key, value in toml2.items():
                self.assertTrue( key in data , f'Key {key} not found')
                self.assertEqual( toml2[ key ], data[ key ])
            self.assertIsInstance( data[ BOOK.title ], str )

            self.assertIsInstance( toml2[ BOOK.title ], str )
            self.assertIsInstance( data[ BOOK.lastRead ], float )

            self.assertIsInstance( toml2[ BOOK.author ], list )
            self.assertIsInstance( data[ BOOK.author ], list )
            self.assertEqual( len( toml2[BOOK.author] ) , 3 )
            self.assertEqual( len( toml2[BOOK.author]  ), len( data[BOOK.author] ) )

            self.assertIsInstance( toml2[ BOOK.composer ], bool )
            self.assertIsInstance( data[ BOOK.composer ], bool )

            self.assertIsInstance( toml2[ BOOK.numberStarts ], datetime )
            self.assertIsInstance( data[ BOOK.numberStarts ], datetime )

            self.assertIsInstance( toml2[ BOOK.publisher ], date )
            self.assertIsInstance( data[ BOOK.publisher ], date )

    def test_filter( self ):
        data = {
            'alpha' : "DATA-alpha",
            'beta'  : "DATA-beta",
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = self.obj.write_toml_properties( data , tmpdirname , 'simple_output.cfg')
            self.assertTrue( os.path.isfile( fname ), f'Filename {fname} doesnt exist') 
            with open(fname, "r") as f:
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
            
        
    
        