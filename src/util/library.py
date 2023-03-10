# This Python file uses the following encoding: utf-8
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

import os
import fnmatch
from qdb.dbbook import DbBook
from qdb.keys import BOOK, DbKeys
from qdil.preferences import DilPreferences


class Library():

    @staticmethod
    def books() -> list:
        """ Get all books from the library """
        library = DilPreferences().getDirectoryDB()
        dbbook = DbBook()
        return dbbook.getAll(order=BOOK.location)

    @staticmethod
    def books_not_in_library() -> list:
        """ Get all books where the the location is not in the sheetmusic folder """
        return (Library.books_locations()[1])

    @staticmethod
    def books_in_library() -> list:
        """ Get all the books where the location is in the sheetmusic folder"""
        return (Library.books_locations[0])

    @staticmethod
    def books_locations():
        all_books = Library.books()
        library = DilPreferences().getDirectoryDB()
        in_lib = []
        not_in_lib = []
        for book in all_books:
            if book[BOOK.location].startswith(library):
                in_lib.append(book)
            else:
                not_in_lib.append(book)
        return (in_lib, not_in_lib)

    @staticmethod
    def folders() -> list:
        """ Generate a list of folders that contain PNG files """
        library = DilPreferences().getDirectoryDB()
        liblist = []
        page_suffix = Library.page_suffix()
        with os.scandir(library) as libdir:
            for entry in libdir:
                if (not entry.name.startswith('.') and
                        Library.is_valid_book_directory(entry.path, page_suffix)):
                    liblist.append(entry.path)
        return liblist

    @staticmethod
    def is_valid_book_directory(bookDir: str, page_suffix: str = None) -> bool:
        """
            Check if a directory exists for a book, check for pages that exist in directory
        """
        if page_suffix is None:
            page_suffix = Library.page_suffix()
        return (os.path.isdir(bookDir) and len(fnmatch.filter(os.listdir(bookDir), '*.' + page_suffix)) > 0)

    @staticmethod
    def page_suffix() -> str:
        return DilPreferences().getValue(
            DbKeys.SETTING_FILE_TYPE, default=DbKeys.VALUE_FILE_TYPE)
