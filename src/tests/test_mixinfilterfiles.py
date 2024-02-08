"""
Test frame: MixinFilterFiles

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import unittest
from ui.mixin.importinfo import MixinFilterFiles

class TestMixinFilterFiles(unittest.TestCase):
    def setUp(self):
        self.obj = MixinFilterFiles()
        self.test_files = [ 'file/a', 'file/b', 'file/c', 'file/d']

    def test_simple_split( self ):
        def db_filter( _:list )->list:
            return []
        def filter_dialog( _ )->list:
            return []

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )
        self.assertListEqual( process, self.test_files  )
        self.assertEqual( len( dups ), len( ignore ))
        self.assertEqual( len( ignore), 0 )

    def test_duplicate_files_process_all( self ):
        dup_list = self.test_files[0:2]
        def db_filter( _:list )->list:
            return dup_list
        def filter_dialog( _ )->list:
            return dup_list

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )
        self.assertEqual( set( process) , set( self.test_files)  )
        self.assertEqual( len( dups ), len( dup_list ))
        self.assertEqual( set( dups ) , set(  dup_list ) )

        self.assertEqual( len( ignore), 0 , ignore )

    def test_duplicate_files_process_some( self ):
        dup_list = self.test_files[0:2]
        def db_filter( _:list )->list:
            return dup_list
        def filter_dialog( _ )->list:
            return self.test_files[0:1]

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        data_list = f'Process: {process} Duplicates: {dups} Ignore: {ignore}'
        self.assertEqual( len( process), len( self.test_files )-1, data_list  )
        self.assertEqual( set( process ), set( ['file/a', 'file/c', 'file/d'] ) , data_list )

        self.assertEqual( len( dups ), len( dup_list[0:1] ), data_list)
        self.assertEqual( set( dups ), set( dup_list[0:1] ), data_list)

        self.assertEqual( len( ignore), 1 , data_list )

    def test_no_files(self):
        def db_filter( _:list )->list:
            return []
        def filter_dialog( _ )->list:
            return []

        process, dups, ignore = self.obj.split_selected( [], db_filter, filter_dialog )

        self.assertEqual( len( process), 0 )
        self.assertEqual( len( dups), 0 )
        self.assertEqual( len( ignore), 0 )

    def test_files_but_bad_filter( self ):
        def db_filter( _:list )->list:
            # All files have been processed
            return self.test_files
        def filter_dialog( _ )->list:
            # But the filter returned nonsense
            return ['what/bad-01', 'what/bad-02']

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), 0 )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), len( self.test_files ) )

    def test_files_but_bad_db_filter( self ):
        def db_filter( _:list )->list:
            # junk returned
            return ['what/bad-01', 'what/bad-02']
        def filter_dialog( _ )->list:
            # But the filter returned nothing
            return []

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), 0 )

    def test_files_but_bad_db_filter_bad_dialog( self ):
        def db_filter( _:list )->list:
            # junk returned
            return ['what/bad-01', 'what/bad-02']
        def filter_dialog( _ )->list:
            # But the filter returned nothing
            return ['what/bad-01', 'what/bad-02']

        process, dups, ignore = self.obj.split_selected( self.test_files, db_filter, filter_dialog )
        self.assertEqual( len( process), len( self.test_files ) )

        self.assertEqual( len( dups ), 0 )

        self.assertEqual( len( ignore), 0 )
