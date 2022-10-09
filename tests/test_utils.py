# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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
import sys
sys.path.append("../")
from util.convert import toInt, toBool

class TestUtils( unittest.TestCase):

    def test_toint_with_numeric_characters( self ):
        self.assertEqual( toInt(""), 0 )
        for i in range( -10,10,1):
            intString = str( i )
            self.assertEqual( toInt( intString ), i)
        self.assertEqual( toInt("10"), 10)
        self.assertEqual( toInt("-10"), -10 )

        x = float(.5)
        self.assertEqual( toInt(x,default=10), 0 )

    def test_toint_with_alphabetic_characters( self ):

        self.assertEqual( toInt("abc"), 0 )
        self.assertEqual( toInt("$10"), 0)
        flag=False
        try:
            self.assertEqual( toInt('abc', ignore=False))
        except:
            flag=True
        self.assertTrue( flag )
        flag=False
        try:
            self.assertEqual( toInt('$10', ignore=False))
        except:
            flag=True
        self.assertTrue( flag )

    def test_toint_bool(self):
        flag=False
        value = 0
        try:
            value=toInt(True, ignore=False)
        except Exception as err:
            flag=True
        self.assertFalse( flag )
        self.assertEqual(value, 1)

    
    def test_toint_with_none(self):
        self.assertEqual( toInt(None), 0 )

    def test_toint_with_integers(self):
        for i in range(-10,10,1 ):
            self.assertEqual( toInt(i), i )

    def test_toint_with_floats(self):
        self.assertEqual( toInt(10.5), 10 )

    def test_toBool(self):
        self.assertTrue( toBool(1))
        self.assertTrue( toBool( 'yes'))
        self.assertTrue( toBool( 'true'))
        self.assertTrue( toBool( 't'))
        self.assertTrue( toBool( 'ok'))
        self.assertTrue( toBool( True))

        self.assertFalse( toBool('no'))
        self.assertFalse( toBool( False))
        self.assertFalse( toBool( 0 ))
        self.assertFalse( toBool(None))

if __name__ == "__main__":
    unittest.main()
