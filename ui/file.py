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
#


from musicfile import MusicFile
from functools import lru_cache
from PySide6.QtWidgets import (QMessageBox)
from PySide6.QtGui import QPixmap

class UiFile (MusicFile):
    '''
    Class will handle the file functions and configuration.
    '''
    CACHE_SIZE = 5

    def __init__(self):
        super().__init__()

    def clearSettings(self):
        """ Clear the pixel map and all settings for a music config"""
        self.getPixmap.cache_clear()
        return super().clearSettings()


# we need to save layout in appropriate section
    def setOrientaton(self, layout: str):
        """ Set the orientation. This should be defined in MusicFile"""
        self.layout = str

    def deleteBookmark(self, 
            section,
            bookName=None,
            bookmark=None,
            pageShown=None,
            bookPage=None
            ):
        """ Delete the bookmark indicated from the config.ini file """
        try:
            self.config.remove_section(section)
        except Exception as err:
            expandedFormat="{}:    {}\n"
            expandedInfo=""
            if bookName:
                expandedInfo=expandedFormat.format("Book", bookName)
            if bookmark:
                expandedInfo = expandedInfo + expandedFormat.format("Bookmark",bookmark)
            if pageShown:
                expandedInfo = expandedInfo + expandedFormat.format("Page Shown",pageShown)
            if bookPage:
                expandedInfo = expandedInfo + expandedFormat.format("Book Page",bookPage)
            
            dlg = QMessageBox()
            dlg.setIcon(QMessageBox.Warning)
            dlg.setWindowTitle("SheetMusic")
            dlg.setCheckBox(None)
            dlg.setStandardButton(QMessageBox.Ok)

            dlg.setText("Could not delete bookmark.")
            if hasattr(err, "message"):
                dlg.setInformativeText(err.message)
            else:
                dlg.setInfomativeText(bookmark)
            if expandedInfo:
                dlg.setDetailedText( expandedInfo )
            dlg.exec()
        finally:
            self.writeBookConfig()


    def getAllBookmarks(self):
        """ fetch a list of all bookmarks in the config.ini """
        bookmarkList = []
        for section in self.config.sectionsSorted():
            name = self.config.getConfig(self.config.KEY_NAME, section , '?' )
            pname = name
            if name == '?':
                name = section
                pname = self._formatPrettyName(name)
            configPage = self.config[section][self.config.KEY_PAGE_CONTENT]
            relativePage = str(self.getBookPageNumberRelative(configPage))
            bookmarkList.append({
                self.config.KEY_NAME:          name,
                self.config.KEY_PAGE_CONTENT:  configPage,
                self.config.KEY_PNAME:         pname,
                self.config.KEY_PAGES_START:   relativePage})
        return bookmarkList

 
    @lru_cache(5)
    def getPixmap(self, pageNum):
        """ read the file and conver it into a pixal map.
        
            This will cache entries to help speedup pixmap conversion
        """
        imagePath = self.getBookPagePath(pageNum)
        return QPixmap(imagePath)
        

    def writeBookConfig(self):
        """ Save the books config.ini """
        try:
            super().writeBookConfig()        
        except Exception as err:
            dlg = QMessageBox()
            dlg.setWindowTitle("Error " + self.fileBaseName +
                                   "configuration file")
            if hasattr(err, "message"):
                dlg.setText(err.message)
            else:
                dlg.setText(
                    "Could not write configuration file " + self.fileBaseName)
                dlg.setStandardButtons(QMessageBox.Cancel)
                dlg.setDefaultButton(QMessageBox.Cancel)
                dlg.setIcon(QMessageBox.Warning)
                dlg.exec()
                return False
        return True