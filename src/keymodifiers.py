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
            "page-back": self.page_back(),
            "page-forward": self.page_forward(),
            "first-page-book": self.first_book_page(),
            "first-page-shown": self.first_page_shown(),
            "last-page-book": self.last_book_page(),
            "last-page-shown": self.last_page_shown(),
            "previous-bookmark": self.previous_bookmark(),
            "next-bookmark": self.next_bookmark(),
        }

    def page_back(self) -> dict:
        """ Page back key sequence """
        return {
            QKeySequence(QKeySequence.MoveToPreviousPage).toString():
                QKeySequence(QKeySequence.MoveToPreviousPage).toString(),
            "Up-cursor key": QKeySequence("Up").toString(),
            "Left-cursor key": QKeySequence("Left").toString(),
            "i": QKeySequence("i")
        }

    def page_forward(self) -> dict:
        """ Page forward sequence """
        return {
            QKeySequence(QKeySequence.MoveToNextPage).toString():
                QKeySequence(QKeySequence.MoveToNextPage).toString(),
            "Down-cursor key": QKeySequence('Down').toString(),
            "Right-cursor key": QKeySequence("Right").toString(),
            "k": QKeySequence("k")
        }

    def first_page_shown(self) -> dict:
        """ Key sequence for first page """
        return {
            QKeySequence(QKeySequence.MoveToStartOfDocument).toString(
                format=self.native):
                    QKeySequence(QKeySequence.MoveToStartOfDocument).toString(),
            QKeySequence(QKeySequence('Ctrl+Left')).toString(
                format=self.native):
                    QKeySequence('Ctrl+Left').toString(),
        }

    def last_page_shown(self) -> dict:
        """ Keys sequence for last page """
        return {
            QKeySequence(QKeySequence.MoveToEndOfDocument).toString(
                format=self.native):
                    QKeySequence(QKeySequence.MoveToEndOfDocument).toString(),
            QKeySequence(QKeySequence('Ctrl+Right')).toString(
                format=self.native):
                    QKeySequence('Ctrl+Right').toString()
        }

    def first_book_page(self) -> dict:
        """ Key sequence for first book page"""
        return {
            QKeySequence(QKeySequence.Back).toString(
                format=self.native):
                    QKeySequence(QKeySequence.Back).toString(),
            QKeySequence(QKeySequence('Ctrl+Alt+Left')).toString(
                format=self.native):
                    QKeySequence('Ctrl+Alt+Left').toString()
        }

    def last_book_page(self) -> dict:
        """ Last page of book """
        return {
            QKeySequence(QKeySequence.Forward).toString(
                format=self.native):
                    QKeySequence(QKeySequence.Forward).toString(),
            QKeySequence(QKeySequence('Ctrl+Alt+Right')).toString(
                format=self.native):
                    QKeySequence('Ctrl+Alt+Right').toString(),
        }

    def previous_bookmark(self) -> dict:
        """ Back one bookmark """
        return {
            QKeySequence(QKeySequence('Alt+Up')).toString(
                format=self.native):
                    QKeySequence('Alt+Up').toString(),
            QKeySequence(QKeySequence('Alt+Left')).toString(
                format=self.native):
                    QKeySequence('Alt+Left').toString(),
            "j": QKeySequence("j"),
        }

    def next_bookmark(self) -> dict:
        """Forward one bookmark

        Returns:
            dict: Next bookmark shortcuts
        """
        return {
            QKeySequence(QKeySequence('Alt+Down')).toString(
                format=self.native): QKeySequence('Alt+Down').toString(),
            QKeySequence(QKeySequence('Alt+Right')).toString(
                format=self.native): QKeySequence('Alt+Right').toString(),
            "l": QKeySequence("l"),
        }

    def get_mods(self) -> dict:
        """ Get all keyboard modifications in a dictionary """
        return self.mods
