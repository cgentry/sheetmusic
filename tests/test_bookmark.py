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

from bookmark import Bookmark
import unittest

class TestBookmark( unittest.TestCase): 
    def test_empty_bookmark(self):
        pstring = "[]: Name: '' Index: -1 Page: 0 End: 0, Found: False"
        b = Bookmark()
        self.assertEqual( b.section, "")
        self.assertEqual( b.name, "" )
        self.assertEqual( b.index, -1 )
        self.assertEqual( b.page, 0 )
        self.assertEqual( b.pagestr, "0")
        self.assertEqual( b.endpage, 0 )
        self.assertFalse( b.isFound())
        self.assertFalse( b.found )
        self.assertEqual( b.__str__(), pstring)

    def test_all_set_bookmark(self):
        pstring = "[section]: Name: 'name' Index: 123 Page: 456 End: 789, Found: True"
        b = Bookmark("section","name", 123, 456, 789, True)
        self.assertEqual( b.section, "section")
        self.assertEqual( b.name, "name")
        self.assertEqual( b.index, 123 )
        self.assertEqual( b.page, 456 )
        self.assertEqual( b.pagestr, "456")
        self.assertEqual( b.endpage, 789 )
        self.assertTrue( b.isFound())
        self.assertTrue( b.found )
        self.assertEqual( b.__str__(), pstring)

    def test_none_value_bookmark(self):
        b = Bookmark( None, None, None, None, None )
        self.assertIsNone( b.section )
        self.assertIsNone( b.name)
        self.assertEqual( b.index, 0 )
        self.assertEqual( b.page, 0 )
        self.assertEqual( b.pagestr, "0")
        self.assertEqual( b.endpage, 0 )
        self.assertFalse( b.isFound())
        self.assertFalse( b.found )