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
