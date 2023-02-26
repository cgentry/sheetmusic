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

from qdb.dbbook import DbBook
from qdb.keys   import BOOK
from qdil.preferences import DilPreferences

class LibraryConsolidate( ):
    @staticmethod
    def books_not_in_library()->list:
        library = DilPreferences().getDirectoryDB()
        dbbook = DbBook()
        all_books = dbbook.getAll()
        not_in_lib = []
        for book in all_books:
            if not book[ BOOK.location ].startswith( library ):
                not_in_lib.append( book )
        return not_in_lib