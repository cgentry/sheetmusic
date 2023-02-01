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
#
# image files should be in a single folder and end in '.png'
# configuration for each book is located in
# config.ini - See ConfigFile in configfile.py
# 
"""
keymodifers contains definitions that can be used on any platform.
It is split off so we don't have a massive class that contains just
dictionary definitions.
"""

from PySide6.QtGui import QKeySequence

class KeyModifiers:
    """
    KeyModifers contains data dictionaries for general usage.
    The labels are shown in comboboxes with appropriate labels

    'Game' keys can be i (back), k(next), j(Prev-bookmark), l (next bookmark)
    """
    def __init__(self) -> None:
        self.native = QKeySequence.SequenceFormat.NativeText
        self.mods = {
            "page-back"        : self.pageBack(),
            "page-forward"     : self.pageForward(),
            "first-page-book"  : self.firstBookPage(),
            "first-page-shown" : self.firstPageShown(),
            "last-page-book"   : self.lastBookPage(),
            "last-page-shown"  : self.lastPageShown(),
            "previous-bookmark": self.previousBookmark(),
            "next-bookmark"    : self.nextBookmark(),
        }
        
    def pageBack(self)->dict:
        return {
             QKeySequence( QKeySequence.MoveToPreviousPage).toString() : QKeySequence( QKeySequence.MoveToPreviousPage).toString(),
            "Up-cursor key": QKeySequence(u"Up").toString(),
            "Left-cursor key": QKeySequence(u"Left").toString(),
            "i": QKeySequence(u"i")
        }
    
    def pageForward(self)->dict:
        return {
            QKeySequence( QKeySequence.MoveToNextPage).toString() : QKeySequence( QKeySequence.MoveToNextPage).toString(),
            "Down-cursor key": QKeySequence(u'Down').toString(),
            "Right-cursor key": QKeySequence(u"Right").toString(),
            "k": QKeySequence(u"k")
        }
       
    def firstPageShown(self)->dict:
        return {
            QKeySequence( QKeySequence.MoveToStartOfDocument).toString(format=self.native) : QKeySequence( QKeySequence.MoveToStartOfDocument).toString(),
            QKeySequence( QKeySequence(u'Ctrl+Left') ).toString(format=self.native): QKeySequence(u'Ctrl+Left').toString(),
        }

    def lastPageShown(self)->dict:
        return {
            QKeySequence( QKeySequence.MoveToEndOfDocument).toString(format=self.native) : QKeySequence(QKeySequence.MoveToEndOfDocument).toString(),
            QKeySequence( QKeySequence(u'Ctrl+Right') ).toString(format=self.native): QKeySequence(u'Ctrl+Right').toString()
        }

    def firstBookPage(self)->dict:
        return {
            QKeySequence( QKeySequence.Back).toString(format=self.native) : QKeySequence( QKeySequence.Back).toString(),
            QKeySequence( QKeySequence(u'Ctrl+Alt+Left') ).toString(format=self.native): QKeySequence(u'Ctrl+Alt+Left').toString() 
        }

    def lastBookPage(self)->dict:
        return {
            QKeySequence( QKeySequence.Forward).toString(format=self.native) : QKeySequence( QKeySequence.Forward).toString(),
            QKeySequence( QKeySequence(u'Ctrl+Alt+Right') ).toString(format=self.native): QKeySequence(u'Ctrl+Alt+Right').toString(),
        }

    def previousBookmark(self)->dict:
        return {
            QKeySequence( QKeySequence(u'Alt+Up') ).toString(format=self.native): QKeySequence(u'Alt+Up').toString() ,
            QKeySequence( QKeySequence(u'Alt+Left') ).toString(format=self.native): QKeySequence(u'Alt+Left').toString() ,
            "j": QKeySequence(u"j"),
        }

    def nextBookmark(self)->dict:
        return {
            QKeySequence( QKeySequence(u'Alt+Down') ).toString(format=self.native): QKeySequence(u'Alt+Down').toString() ,
            QKeySequence( QKeySequence(u'Alt+Right') ).toString(format=self.native): QKeySequence(u'Alt+Right').toString() ,
            "l": QKeySequence(u"l"),
        }

    def getMods(self) -> dict:
        return self.mods