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

import sys
import sqlite3
import unittest

from qdb.dbconn import DbConn
from qdb.setup import Setup
from qdb.keys import DbKeys
from qdil.preferences import DilPreferences

class TestSystem( unittest.TestCase):
    def setUp(self):
        DbConn.openDB(':memory:')
        self.setup = Setup(":memory:")
        self.setup.dropTables()
        self.setup.createTables()
        self.setup.initData()
        self.obj = DilPreferences()
        

    def tearDown(self):
        self.setup.dropTables()

    def test_getValue( self ):
        val = self.obj.getValue( DbKeys.SETTING_DEFAULT_SCRIPT)
        self.assertIsNotNone( val )