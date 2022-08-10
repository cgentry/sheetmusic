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
from configfile import ConfigFile
from bookmark import Bookmark
from test_config import dummyPref
from musicsettings import MSet

class TestConfigFile( unittest.TestCase): 
    sampleData = """#
[DEFAULT]
content_start =  4
filetype = png
numbering_starts = 7  
numbering_ends   = 101
last_read = 20
setting/layout = 2side
name = volume1
title = Stranger Volume 1
version = 1.1
total_pages = 300

[volume1-023]
content_start =  23
name = Some Trilling Exercises

[volume1-020]
name = Starting Lessons
content_start =  20

[volume1-050]
content_start =  50

[volume1-017]
name = test bookmark after delete
content_start =  17
version = 1.0"""

    sampleSections = ["volume1-017","volume1-020","volume1-023","volume1-050"]

    emptyData="""[DEFAULT]
content_start =  4
filetype = png
numbering_starts = 7  
numbering_ends   = 101
last_read = 20
layout = 2side
name = volume1
title = Stranger Volume 1
version = 1.1
total_pages = 300"""

    def createTest(self, data ):
        self.pref = dummyPref()
        cfg = ConfigFile(self.pref)
        cfg.read_string( data )
        return cfg
        
    def test_formatBook_find_first_bookmark(self):
        cfg = self.createTest(self.sampleData )
        mark = cfg._formatBookmark( 'volume1-017')
        self.assertEqual( mark.name, "test bookmark after delete")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 0)
        self.assertEqual( mark.page, 17)
        self.assertEqual( mark.pagestr, '17')
        self.assertEqual( mark.endpage, 19, "volume1-017. Next bookmark is 20" )
        del cfg

    def test_formatBook_find_middle_bookmark(self):
        cfg = self.createTest(self.sampleData )
        mark = cfg._formatBookmark( 'volume1-023')
        self.assertEqual( mark.name, "Some Trilling Exercises")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 2)
        self.assertEqual( mark.page, 23)
        self.assertEqual( mark.pagestr, '23')
        self.assertEqual( mark.endpage, 49, "volume1-023. Next bookmark is 50" )
        del cfg

    def test_formatBookmark_valid_bookmark(self):
        cfg = self.createTest(self.sampleData )
        mark = cfg._formatBookmark( 'volume1-050')
        self.assertEqual( mark.name, "volume1")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 3)
        self.assertEqual( mark.page, 50)
        self.assertEqual( mark.pagestr, '50')
        self.assertEqual( mark.endpage, 300)
        del cfg

    def test_formatBookmark_invalid_name(self):
        cfg = self.createTest(self.sampleData )
        mark = cfg._formatBookmark( 'novolume')
        self.assertEqual( mark.name, "")
        self.assertEqual( mark.found, False)
        self.assertEqual( mark.index, -1)
        self.assertEqual( mark.page, 0)
        self.assertEqual( mark.pagestr, '0')
        self.assertEqual( mark.endpage, 0)
        del cfg

    def test_bookmarkFromIndex_0(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg._bookmarkFromIndex( self.sampleSections, 0 )
        self.assertEqual( mark.name, "test bookmark after delete")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 0)
        self.assertEqual( mark.page, 17)
        self.assertEqual( mark.pagestr, '17')
        self.assertEqual( mark.endpage, 19, "volume1-017. Next bookmark is 20" )
        del cfg

    def test_bookmarkFromIndex_1(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg._bookmarkFromIndex( self.sampleSections , 1 )
        self.assertEqual( mark.name, "Starting Lessons")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 1)
        self.assertEqual( mark.page, 20)
        self.assertEqual( mark.pagestr, '20')
        self.assertEqual( mark.endpage, 22, "volume1-020. Next bookmark is 23" )
        del cfg

    def test_sortedsections(self):
        cfg = self.createTest(self.sampleData)
        ss = cfg.sectionsSorted()
        self.assertEqual( len( ss), len(self.sampleSections))
        for index in range( len(ss) ):
            self.assertEqual( ss[index], self.sampleSections[index])

    def test_getBookmarkClassForPage_beforebook(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getBookmarkClassForPage( 1 )
        self.assertEqual( mark.page, 1 )
        self.assertEqual( mark.section, "" )
        self.assertEqual( mark.found, False )
        self.assertEqual( mark.endpage, 300 )
        self.assertEqual( mark.index, -1 )

    def test_getBookmarkClassForPage_afterbook(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getBookmarkClassForPage( 300 )
        self.assertEqual( mark.name, "volume1")
        self.assertEqual( mark.found, True)
        self.assertEqual( mark.index, 3)
        self.assertEqual( mark.page, 50)
        self.assertEqual( mark.pagestr, '50')
        self.assertEqual( mark.endpage, 300)


    def test_getBookmarkClassForPage_FirstChaper_017(self):
        cfg = self.createTest(self.sampleData)
        for page in range( 17,19):
            mark = cfg.getBookmarkClassForPage( page )
            self.assertEqual( mark.name, "test bookmark after delete")
            self.assertEqual( mark.found, True)
            self.assertEqual( mark.index, 0)
            self.assertEqual( mark.page, 17)
            self.assertEqual( mark.endpage, 19)

    def test_getBookmarkClassForPage_FirstChaper_050(self):
        cfg = self.createTest(self.sampleData)
        for page in range( 50,300):
            mark = cfg.getBookmarkClassForPage( page )
            self.assertEqual( mark.name, "volume1")
            self.assertEqual( mark.found, True)
            self.assertEqual( mark.index, 3)
            self.assertEqual( mark.page, 50)
            self.assertEqual( mark.endpage, 300)

    def test_getBookmarkClassForPage_EmptyData(self):
        cfg = self.createTest(self.emptyData)
        mark = cfg.getBookmarkClassForPage( 50 )
        self.assertEqual( mark.name, "volume1")
        self.assertEqual( mark.found, False)
        self.assertEqual( mark.index, -1)
        self.assertEqual( mark.page, 1)
        self.assertEqual( mark.endpage, 300)

    def test_getConfig(self):
        cfg = self.createTest(self.sampleData)
        tlayout = MSet.byDefault( MSet.SETTING_DEFAULT_LAYOUT)
        self.assertEqual( '2side', cfg.getConfig( tlayout ,'volume1-023'))

    def test_totalPages(self):
        cfg = self.createTest(self.sampleData)
        self.assertEqual(300, cfg.getTotalPages() )
        cfg.setTotalPages(40)
        self.assertEqual(40, cfg.getTotalPages() )

    def test_numberpagesdisplay(self):
        cfg = self.createTest(self.sampleData)
        self.assertEqual(2, cfg.getNumberPagesToDisplay() )

    def test_getBookmarkForPage(self):
        cfg = self.createTest(self.sampleData)
        self.assertEqual( "" , cfg.getBookmarkForPage(10) )

        for i in range(0,3):
            self.assertEqual( 'volume1-020', cfg.getBookmarkForPage( 20+i))

        self.assertNotEqual( 'volume1-020', cfg.getBookmarkForPage( 23))
        self.assertEqual( 'volume1-023', cfg.getBookmarkForPage( 23))

    def test_getBookmarkForPageField( self ):
        cfg = self.createTest(self.sampleData)
        self.assertEqual( cfg.getBookmarkForPageField( 20 , "name" ), "Starting Lessons" )
        self.assertEqual( cfg.getBookmarkForPageField( 22 , "content_start" ), "20" )

        self.assertEqual( cfg.getBookmarkForPageField( 2 , "content_start" ), None )

    def test_setCurrentBookmark_with_mark(self):
        cfg = self.createTest(self.sampleData)
        self.assertFalse( cfg.isCurrentBookmarkSet() )
        mark = cfg.getBookmarkClassForPage( 20 )
        self.assertIsInstance( mark , Bookmark )
        self.assertEqual( mark.section , "volume1-020" )
        self.assertEqual( mark.index , 1 )
        self.assertFalse( cfg.isCurrentBookmarkSet() )
        cfg.setCurrentBookmark( mark )
        self.assertTrue( cfg.isCurrentBookmarkSet() )

        mark = cfg.getCurrentBookmark()
        self.assertIsInstance( mark , Bookmark )
        self.assertEqual( mark.section , "volume1-020" )
        self.assertEqual( mark.index , 1 )

        cfg.clearCurrentBookmark()
        self.assertFalse( cfg.isCurrentBookmarkSet() )

    def test_setCurrentBookmark_with_page(self):
        cfg = self.createTest(self.sampleData)
        self.assertFalse( cfg.isCurrentBookmarkSet() )
        cfg.setCurrentBookmark(21)
        mark = cfg.getCurrentBookmark()
        self.assertIsInstance( mark , Bookmark )
        self.assertEqual( mark.section , "volume1-020" )
        self.assertEqual( mark.index , 1 )
        self.assertTrue( cfg.isCurrentBookmarkSet() )

        cfg.clearCurrentBookmark()
        self.assertFalse( cfg.isCurrentBookmarkSet() )

    def test_getBookmar_Offsets( self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getBookmarkClassForPage( 20 )
    
        cfg.setCurrentBookmark( mark )
        markLast=cfg.getPreviousBookmark()
        self.assertEqual( markLast.section, "volume1-017")

        markNext=cfg.getNextBookmark()
        self.assertEqual( markNext.section, "volume1-023")
    
    def test_getBookmark_WithOffset( self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getBookmarkClassForPage( 20 )
        cfg.setCurrentBookmark( mark )
        msg = "** CURRENT = "+ mark.section + " **"

        mark2 = cfg.getBookmarkWithOffset(1)
        self.assertEqual( mark2.section , "volume1-023", msg)
        mark2 = cfg.getBookmarkWithOffset(2)
        self.assertEqual( mark2.section, "volume1-050", msg)

        mark2 = cfg.getBookmarkWithOffset(3)
        self.assertEqual( mark2.section, "volume1-050", msg)

        mark2 = cfg.getBookmarkWithOffset(4)
        self.assertEqual( mark2.section, "volume1-050")

        mark2 = cfg.getBookmarkWithOffset(-1)
        self.assertEqual( mark2.section, "volume1-017", msg)

        mark2 = cfg.getBookmarkWithOffset(-2)
        self.assertEqual( mark2.section, "volume1-017", msg)

        mark2 = cfg.getBookmarkWithOffset(-3)
        self.assertEqual( mark2.section, "volume1-017", msg)

    def test_first_bookmark(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getFirstBookmark()
        self.assertEqual( mark.section, "volume1-017")
        self.assertEqual( cfg.getFirstBookmarkPage(), 17 )

        cfg = ConfigFile()
        self.assertEqual( cfg.getFirstBookmarkPage(), None )

    def test_Last_bookmark(self):
        cfg = self.createTest(self.sampleData)
        mark = cfg.getLastBookmark()
        self.assertEqual( mark.section, "volume1-050")
