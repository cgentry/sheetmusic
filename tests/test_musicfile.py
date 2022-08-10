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
import tempfile
import os
from musicfile import MusicFile
from musicsettings import MSet
from PySide6.QtWidgets import QMessageBox


class TestMusicfile(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.dir = tempfile.TemporaryDirectory(prefix="sheetmusic")
        self.path = os.path.join(self.dir.name, "testmusic")
        os.mkdir(self.path)
        self.createFiles(self)
        self.writeConfig(self)

    def test_prettyname(self):
        mf = MusicFile()
        pname = mf._formatPrettyName("nametest-010")
        self.assertEqual(pname, "Nametest, page 10")

    def test_set_filtype(self):
        mf = MusicFile()
        mf.setFileType('txt')
        self.assertEqual('txt', mf.getFileType())

    def test_book_paths(self):
        mf = MusicFile()
        mf.setPaths("/tmp//sheetmusic/book")
        self.assertTrue("book-{0:03d}.png" in mf.bookPathFormat)
        self.assertEqual(mf.dirPath, "/tmp/sheetmusic/book")
        self.assertEqual(mf.dirName, "/tmp/sheetmusic")
        self.assertEqual(mf.fileBaseName, "book")
        self.assertEqual(mf.bookPageName, "book-{0:03d}")

        self.assertEqual(mf.getBookPath(), "/tmp/sheetmusic/book")
        self.assertEqual(mf.getBookPagePath(
            10), "/tmp/sheetmusic/book/book-010.png")

        mf.clearSettings()
        self.assertEqual("", mf.bookPathFormat)
        self.assertEqual(mf.dirPath, "")
        self.assertEqual(mf.dirName, "")
        self.assertEqual(mf.fileBaseName, "")
        self.assertEqual(mf.bookPageName, "")

    def test_configs(self):
        mf = MusicFile()
        mf.setConfig('test', 10)
        self.assertEqual(mf.getConfig('test'), '10')
        self.assertIsNone(mf.getConfig('nobody home'))

    def test_openbook(self):
        mf = MusicFile()
        self.assertTrue(mf.getBookTitle(), "")
        self.assertEqual(mf.getContentStartingPage(), 0)
        self.assertEqual(mf.getRelativePageOffset(), 1)
        self.assertEqual(mf.getBookPageNumber(), 0)
        self.assertEqual(mf.setPageNumber(7), 0)
        self.assertEqual(mf.getBookPageNumberRelative(), 0)
        self.assertFalse(mf.isRelativePageSet())
        self.assertFalse(mf.isThisPageRelative())

        self.assertTrue(mf.setRelativePageOffset(20))
        self.assertFalse(mf.setRelativePageOffset(20))
        self.assertEqual(20, mf.getRelativePageOffset())
        self.assertTrue(mf.setContentStartingPage(19))
        self.assertFalse(mf.setContentStartingPage(19))
        self.assertEqual(19, mf.getContentStartingPage())

        self.assertTrue(mf.setBookTitle("test"))
        self.assertFalse(mf.setBookTitle("test"))
        self.assertTrue(mf.getBookTitle(), 'test')

        self.assertEqual(mf.openBook(self.path, onError=QMessageBox.Cancel), QMessageBox.Ok)

        self.assertEqual(mf.getContentStartingPage(), 4)
        self.assertEqual(mf.getRelativePageOffset(), 7)
        self.assertTrue(mf.isThisPageRelative())
        self.assertEqual(mf.getBookPageNumber(), 10)
        self.assertEqual(mf.setPageNumber(7), 7)
        self.assertEqual(mf.getBookPageNumberRelative(), 1)
        self.assertTrue(mf.isRelativePageSet())
        self.assertTrue(mf.isThisPageRelative())
        self.assertTrue(mf.getBookTitle(), self.testTitle)
        self.assertEqual(mf.getBookPagesTotal(), 19)

        self.assertTrue("/testmusic" in mf.getBookPath())

    def test_openbook_withpage(self):
        mf = MusicFile()
        self.assertEqual( mf.openBook(self.path, 2,onError=QMessageBox.Cancel), QMessageBox.Ok )
        self.assertEqual(mf.getRelativePageOffset(), 7)
        self.assertEqual(mf.getBookPageNumber(), 2)
        self.assertTrue(mf.isRelativePageSet())
        self.assertFalse(mf.isThisPageRelative())

    def test_openbook_nofile(self):
        mf = MusicFile()
        self.assertEqual(mf.openBook("name isn't valid", onError=QMessageBox.Cancel), QMessageBox.Cancel)

    def test_openbook_emptydir(self):
        mf = MusicFile()
        self.deleteFiles()
        self.assertEqual(mf.openBook(self.path,onError=QMessageBox.Cancel), QMessageBox.Cancel)
        self.createFiles()

    def test_openbook_noconfig(self):
        mf = MusicFile()
        self.deleteConfig()

        self.assertEqual(mf.openBook(self.path, onError=QMessageBox.Cancel), QMessageBox.Ok)
        self.assertEqual(mf.getContentStartingPage(), 1)
        self.assertEqual(mf.getBookPageNumber(), 1)
        self.assertEqual(mf.getRelativePageOffset(), 1)
        self.assertFalse(mf.isRelativePageSet())
        self.assertFalse(mf.isThisPageRelative())

        self.assertEqual(mf.setPageNumber(7), 7)
        self.assertEqual(mf.getBookPageNumberRelative(), 7)
        self.assertFalse(mf.isRelativePageSet())
        self.assertFalse(mf.isThisPageRelative())
        self.assertTrue(mf.getBookTitle(), "testmusic")

        self.writeConfig()

    def test_open_closebook(self):
        mf = MusicFile()
        mf.openBook(self.path)
        mf.setPageNumber(9)
        self.assertEqual(mf.getBookPageNumber(), 9)
        mf.closeBook()
        self.assertEqual(mf.getBookPageNumber(), 0)
        mf.openBook(self.path)
        self.assertEqual(mf.getBookPageNumber(), 9)
        self.writeConfig()

    def test_save_bookmark_nolayout(self):
        mf = MusicFile()
        mf.openBook(self.path)
        mf.setPageNumber(11)
        mf.saveBookmark('dummy')
        self.assertTrue(mf.config.has_section('testmusic-011'))
        self.assertEqual(mf.config.getConfig(
            "name", "testmusic-011", "NOT FOUND"), "dummy")
        self.assertEqual(mf.config.getConfig(
            "content_start", "testmusic-011", "NOT FOUND"), '11')

        self.writeConfig()

    def test_save_bookmark_without_layout_name(self):
        mf = MusicFile()
        mf.openBook(self.path)
        mf.setPageNumber(12)
        mf.saveBookmark()
        self.assertTrue(mf.config.has_section('testmusic-012'))
        self.assertEqual(mf.config.getConfig(
            "name", "testmusic-012", "12 NOT FOUND"), "testmusic-012")
        self.assertEqual(mf.config.getConfig(
            "content_start", "testmusic-012", " 12 NOT FOUND"), '12')
        """" No name, no section, this will fallback to value passed"""
        self.assertEqual(mf.config.getConfig(
            "MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)", section="testmusic-012", fallback=False), 
            None)
        self.assertEqual(mf.config.getConfig(
            "MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)", section="testmusic-012", value="what",fallback=False), 
            "what")

        self.writeConfig()

    def test_save_bookmark_with_layout(self):
        mf = MusicFile()
        mf.openBook(self.path)
        mf.setPageNumber(13)
        mf.saveBookmark('dummy13', "1page")
        self.assertTrue(mf.config.has_section('testmusic-013'))
        self.assertEqual(mf.config.getConfig(
            "name", "testmusic-013", "NOT FOUND"), "dummy13")
        self.assertEqual(mf.config.getConfig(
            "content_start", "testmusic-013", "NOT FOUND"), '13')
        self.assertEqual(mf.config.get(
            'testmusic-013', MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT)), "1page")
        self.assertEqual(mf.config.getConfig(
            MSet.byDefault(MSet.SETTING_DEFAULT_LAYOUT), "testmusic-013"), "1page")

        self.writeConfig()

    def test_go_first_last_bookmark(self):
        mf = MusicFile()
        mf.openBook(self.path)
        self.assertEqual(mf.getNumberBookmarks(), 3)
        self.assertEqual(mf.getBookPageNumber(), 10)

        mf.goPreviousBookmark()
        self.assertEqual(mf.getBookPageNumber(), 8)

        mf.goPreviousBookmark()
        self.assertEqual(mf.getBookPageNumber(), 8)

        mf.goNextBookmark()
        self.assertEqual(mf.getBookPageNumber(), 10)

        mf.goNextBookmark()
        self.assertEqual(mf.getBookPageNumber(), 15)

        mf.goNextBookmark()
        self.assertEqual(mf.getBookPageNumber(), 15)

    def test_inc_page(self):
        mf = MusicFile()
        mf.openBook(self.path)
        self.assertEqual(10, mf.getBookPageNumber())
        for i in range(1, 9):
            mf.incPageNumber(1)
            self.assertEqual(10+i, mf.getBookPageNumber())
        for i in range(1, 9):
            mf.incPageNumber(1)
            self.assertEqual(19, mf.getBookPageNumber())

        for i in range(1, 18):
            mf.incPageNumber(-1)
            self.assertEqual(19-i, mf.getBookPageNumber())
        for i in range(1, 9):
            mf.incPageNumber(-1)
            self.assertEqual(1, mf.getBookPageNumber())

    def test_getBookmarkName(self):
        mf = MusicFile()
        mf.openBook(self.path)
        name = mf.getBookmarkName('testmusic-007')
        self.assertEqual(name, "Starting")

        name = mf.getBookmarkName('testmusic-015')
        self.assertEqual(name, 'testmusic-015')

    def test_getBookmarkList(self):
        mf = MusicFile()
        mf.openBook(self.path)
        list = mf.getBookmarkList()
        self.assertEqual(len(list), 3)
        self.assertEqual(list[0], 'Starting')
        self.assertEqual(list[1], 'Second')
        self.assertEqual(list[2], 'testmusic-015')

    def test_getProperties(self):
        mf = MusicFile()
        mf.openBook(self.path)
        list = mf.getProperties()
        self.assertGreater(len(list), 3)
        self.assertEqual(list['Title'], self.testTitle)
        self.assertEqual(list['Total Pages'], 19)
        self.assertEqual(list['Total Bookmarks'], 3)
        self.assertEqual(list['Page numbering starts at'], 7)
        self.assertEqual(list['Page for first content'], 4)
        self.assertEqual(list['Location'], self.path)
        self.assertEqual(list['List of Bookmarks'],
                         '"Starting", "Second", "testmusic-015"')

    def test_properties(self):
        """
        Update a mutable property. If a change occures it should return true
        """
        mf = MusicFile()
        mf.openBook(self.path)
        self.assertTrue( mf.setMutableProperties( 'title','10','20'))

        self.assertEqual( mf.getBookTitle(), 'title')
        self.assertEqual( mf.getContentStartingPage(), 10 )
        self.assertEqual( mf.getRelativePageOffset(), 20)

        self.assertFalse( mf.setMutableProperties( 'title','10','20'))

    @classmethod
    def tearDownClass(self):
        self.deleteConfig(self)
        self.deleteFiles(self)
        os.rmdir(self.path)
        self.dir.cleanup()

    def createFiles(self):
        for index in range(1, 20):
            fname = os.path.join(
                self.path, "testmusic-{0:03d}.png".format(index))
            f = open(fname, "w")
            f.close()

    def deleteFiles(self):
        for index in range(1, 20):
            fname = os.path.join(
                self.path, "testmusic-{0:03d}.png".format(index))
            if os.path.isfile(fname):
                os.remove(fname)

    def writeConfig(self):
        self.testTitle = "test music volume 1"
        fname = os.path.join(self.path, "config.ini")
        f = open(fname, "w")
        f.write(configTest)
        f.close()

    def deleteConfig(self):
        fname = os.path.join(self.path, "config.ini")
        os.remove(fname)


configTest = """#
[DEFAULT]
filetype = png
setting/layout = 2side
content_start = 4
last_read = 10
numbering_starts = 7
numbering_ends = 20
total_pages = 0
version = 1.0
title = test music volume 1
page = 1

[testmusic-007]
content_start = 8
name = Starting

[testmusic-010]
content_start = 10
name = Second

[testmusic-015]
content_start = 15
"""
