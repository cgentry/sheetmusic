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

import datetime
import os
import pickle
import typing
from collections import namedtuple


from PySide6.QtWidgets import QMessageBox
"""
RecentEntry is used for a dictionary. Each book has a name, page last read, when it was added, and the short display name
"""
RecentEntry = namedtuple('RecentEntry',['book', 'page','added','name'])

class RecentFiles():
    FILE_PATH = "~/sheetmusic"
    FILE_NAME = "sheetmusic.pkl"

    MAX_ENTRIES=10

    def __init__(self, homePath:str=None)->None:
        if homePath is None:
            homePath = self.FILE_PATH
        homePath = homePath.rstrip("/")
        self._path = os.path.expanduser(
            os.path.join(homePath, self.FILE_NAME))
        self.recentBookList = []
        self._maxentries = self.MAX_ENTRIES

    def __del__(self)->None:
        self.write()

    def setMaxEntries(self, max:int)->None:
        self._maxentries = max

    def getMaxEntries(self)->int:
        return self._maxentries

    def read(self)->None:
        try:
            if os.path.isfile(self._path):
                with open(self._path, 'rb') as configfile:
                    self.recentBookList = pickle.load( configfile)
        except:
            return QMessageBox.warning( None, 
                "Opening book",
                "Could not read recent file list",
                QMessageBox.Cancel )
        self.removeFromRecent("")

    def write(self)->None:
        try:
            with open(self._path, 'wb') as configfile:
                pickle.dump( self.recentBookList, configfile )
        except:
             QMessageBox.warning( None, 
                "Writing recent booklist",
                "Could not write recent file list.",
                QMessageBox.Cancel )

    def getRecentListBookNames(self)->list:
        return self.recentBookList

    def getBookPath( self, bookNumber:int )->str:
        if bookNumber > 0 and len( self.recentBookList ) >= bookNumber:
            bookNumber = bookNumber-1
            return self.recentBookList[ bookNumber ].book
        return None            

    def addToRecent(self, book:str, page:int=0, name:str=None)->None:
        if page > 0 and book:
            if not name:
                name = os.path.basename( book )
            newBookEntry = RecentEntry( book, page, str( datetime.datetime.now()), name )
            self.removeFromRecent( book )
            self.recentBookList.insert( 0 , newBookEntry )

    def removeFromRecent(self, book:str)->None:
        if len( self.recentBookList ) > 0 :
            for index, bookEntry in enumerate (self.recentBookList, start=0):
                if bookEntry.book == book:
                    self.recentBookList.pop( index )
                    break
            if len( self.recentBookList ) > self._maxentries :
                self.recentBookList = self.recentBookList[0:self._maxentries]

    def getTopEntry(self)->typing.Tuple[str,int]:
        if len(self.recentBookList)>0:
            return self.recentBookList[0].book, self.recentBookList[0].page
        return None,0
