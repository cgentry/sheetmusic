# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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
from musicutils import toInt

class TestUtils( unittest.TestCase):

    def test_toint_with_numeric_characters( self ):
        self.assertEqual( toInt(""), 0 )
        for i in range( -10,10,1):
            intString = str( i )
            self.assertEqual( toInt( intString ), i)
        self.assertEqual( toInt("10"), 10)
        self.assertEqual( toInt("-10"), -10 )

    def test_toint_with_alphabetic_characters( self ):
        self.assertEqual( toInt("abc"), 0 )
        self.assertEqual( toInt("$10"), 0)
    
    def test_toint_with_none(self):
        self.assertEqual( toInt(None), 0 )

    def test_toint_with_integers(self):
        for i in range(-10,10,1 ):
            self.assertEqual( toInt(i), i )

    def test_toint_with_floats(self):
        self.assertEqual( toInt(10.5), 10 )