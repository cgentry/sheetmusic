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

import unittest
from ui.mixin.importinfo import MixinFilterFiles

class TestMixinFilterFiles(unittest.TestCase):
    def setUp(self):
        self.obj = MixinFilterFiles()
        self.test_files = [ 'file/a', 'file/b', 'file/c', 'file/d']

    def test_simple_split( self ):
        def db_filter( filelist:list )->list:
            return []
        def filter_dialog( filelist )->list:
            return []
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )
        self.assertListEqual( process, self.test_files  )
        self.assertEqual( len( dups ), len( ignore ))
        self.assertEqual( len( ignore), 0 )

    def test_duplicate_files_process_all( self ):
        dup_list = self.test_files[0:2]
        def db_filter( filelist:list )->list:
            return dup_list
        def filter_dialog( filelist )->list:
            return dup_list
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )
        self.assertEqual( set( process) , set( self.test_files)  )
        self.assertEqual( len( dups ), len( dup_list ))
        self.assertEqual( set( dups ) , set(  dup_list ) )

        self.assertEqual( len( ignore), 0 , ignore )

    def test_duplicate_files_process_some( self ):
        dup_list = self.test_files[0:2]
        def db_filter( filelist:list )->list:
            return dup_list
        def filter_dialog( filelist )->list:
            return self.test_files[0:1]
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        data_list = 'Process: {} Duplicates: {} Ignore: {}'.format( process, dups, ignore )
        self.assertEqual( len( process), len( self.test_files )-1, data_list  )
        self.assertEqual( set( process ), set( ['file/a', 'file/c', 'file/d'] ) , data_list )

        self.assertEqual( len( dups ), len( dup_list[0:1] ), data_list)
        self.assertEqual( set( dups ), set( dup_list[0:1] ), data_list)

        self.assertEqual( len( ignore), 1 , data_list )

    def test_no_files(self):
        def db_filter( filelist:list )->list:
            return []
        def filter_dialog( filelist )->list:
            return []
        
        process, dups, ignore = self.obj.split_selected( [], db_filter, filter_dialog )

        self.assertEqual( len( process), 0 )
        self.assertEqual( len( dups), 0 )
        self.assertEqual( len( ignore), 0 )
    
    def test_files_but_bad_filter( self ):
        def db_filter( filelist:list )->list:
            # All files have been processed
            return self.test_files
        def filter_dialog( filelist )->list:
            # But the filter returned nonsense
            return ['what/bad-01', 'what/bad-02']
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), 0 )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), len( self.test_files ) )

    def test_files_but_bad_db_filter( self ):
        def db_filter( filelist:list )->list:
            # junk returned
            return ['what/bad-01', 'what/bad-02']
        def filter_dialog( filelist )->list:
            # But the filter returned nothing
            return []
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), 0 )

    def test_files_but_bad_db_filter_bad_dialog( self ):
        def db_filter( filelist:list )->list:
            # junk returned
            return ['what/bad-01', 'what/bad-02']
        def filter_dialog( filelist )->list:
            # But the filter returned nothing
            return ['what/bad-01', 'what/bad-02']
        
        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), 0 )