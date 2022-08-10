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
from musicsettings import MSet

class TestMset( unittest.TestCase):

    def test_by(self):
        self.assertEqual( MSet.byWindow("value1"), "mainWindow/value1")
        self.assertEqual( MSet.byDefault("value2"), "setting/value2")
        self.assertEqual( MSet.byFile("value3"), "lastfile/value3")
    
    def testDefaults( self ):
        prefs = MSet.defaultSettings()
        self.assertEqual( prefs['lastfile/pageNumber'], '')
        self.assertEqual( prefs['lastfile/directoryPath'], '')
        self.assertEqual( prefs['setting/directoryPath'], MSet.VALUE_DEFAULT_DIR)
        self.assertEqual( prefs['setting/fileType'], MSet.VALUE_FILETYPE)
        self.assertEqual( prefs['setting/layout'], MSet.VALUE_PAGES_SINGLE)
        self.assertEqual( prefs['setting/reopen'], MSet.VALUE_DEFAULT_REOPEN)

    def testVarSplit(self):
        prefs = MSet.defaultSettings()
        varIn = " -c;  -d  "

        parms = MSet.scriptVarSplit( ' -c' )
        self.assertEqual( 1, len( parms ))
        self.assertEqual( parms[0], '-c')

        parms = MSet.scriptVarSplit( varIn )
        self.assertEqual( 2, len( parms ))
        self.assertEqual( parms[0], '-c')
        self.assertEqual( parms[1], '-d')

        parms = MSet.scriptVarSplit( varIn , 'one' )
        self.assertEqual( 3 , len( parms ) )
        self.assertEqual( parms[0], '-c')
        self.assertEqual( parms[1], '-d')
        self.assertEqual( parms[2], 'one')
        
        parms = MSet.scriptVarSplit( varIn , 'one', 'two')
        self.assertEqual( 4 , len( parms ))
        self.assertEqual( parms[0], '-c')
        self.assertEqual( parms[1], '-d')
        self.assertEqual( parms[2], 'one')
        self.assertEqual( parms[3], 'two')

        



