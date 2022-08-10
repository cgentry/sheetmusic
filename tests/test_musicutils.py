# This Python file uses the following encoding: utf-8
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
from musicutils import toInt, toBool

class TestToInt( unittest.TestCase): 
    def test_convertStrings(self):
        self.assertEqual(10,toInt( "10"))
        self.assertEqual(-10, toInt("-0010"))
        self.assertEqual(0 , toInt(""))
    
    def test_convertStringWthDefaults(self):
        self.assertEqual( 1 , toInt("hi", 1))
        self.assertRaises( ValueError, toInt, "hi", 1, ignore=False)

    def test_convertInt(self):
        self.assertEqual( 1 , toInt(1))
        self.assertEqual( 2, toInt(2, 10, False))

class TestToBool( unittest.TestCase ):
    def test_true_string(self):
        self.assertTrue( toBool( "t"))
        self.assertTrue( toBool( "true"))
        self.assertTrue( toBool( "yes"))
        self.assertTrue( toBool( "1"))

    def test_false_string(self):
        self.assertFalse( toBool( "f"))
        self.assertFalse( toBool( "false"))
        self.assertFalse( toBool( "no"))
        self.assertFalse( toBool( "0"))
        self.assertFalse( toBool( ""))

    def test_true_int(self):
        self.assertTrue( toBool(1))
        self.assertTrue( toBool(-1))

    def test_false_int(self):
        self.assertFalse( toBool(0))

    def test_false_none(self):
        self.assertFalse( toBool( None ))

    def test_bool(self):
        self.assertTrue( toBool( True ))
        self.assertFalse( toBool(False))