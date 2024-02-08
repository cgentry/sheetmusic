"""
Test frame: MixinField

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

import unittest
from qdb.mixin.fieldcleanup import MixinFieldCleanup

class TestMixinFieldCleanup(unittest.TestCase):

    def setUp(self):
        self.obj = MixinFieldCleanup()

    def test_bad_start( self ):
        value = "..\tHello World"
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')

    def test_extra_spaces( self ):
        value = "Hello    \t    World"
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')

    def test_extra_spaces_end( self ):
        value = "Hello World     \t"
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')

    def test_extra_spaces_start(self):
        value = '             Hello World'
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')

    def test_special_chars(self):
        value = r'Hello**World?<>\\'
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')

    def test_replace_tab_with_blank(self):
        value = r'Hello World'
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')
        value = "Hello\tWorld"
        self.assertEqual( self.obj.clean_field_value( value ) , 'Hello World')
