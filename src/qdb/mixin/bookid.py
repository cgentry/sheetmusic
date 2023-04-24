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
from qdb.util   import DbHelper
from qdb.keys   import BOOK

class MixinBookID:
    """ This mixin handles looking up book IDs
        lookup_book_id: find book by name or id
        lookup_books_by_column: find book(s) by any column
        lookup_book_by_column: find one book by any column
    """
    SQL_MX_LOOKUP_BY_NAME='SELECT id FROM Book where book=?'
    SQL_MX_LOOKUP_BY_COLUMN='SELECT id FROM BookView WHERE ::column = ? ORDER BY id'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_book_id = None
        self._current_book_name = None

    def lookup_book_id(self, book: str | int) -> int|None:
        """ Fetch the book ID and cache it for future access. If none found, return None"""
        self._current_book_name = None
        if book is not None:
            if isinstance(book, str):
                if self._current_book_name != book or self._current_book_id is None:
                    self._current_book_name = book
                    self._current_book_id = DbHelper.fetchone(MixinBookID.SQL_MX_LOOKUP_BY_NAME, book, default=None)
                    if self._current_book_id :
                        self._current_book_id = int( self._current_book_id )
            elif isinstance( book, dict ):
                self._current_book_id = book[ BOOK.id ]
            elif isinstance( book, int ):
                self._current_book_id = book
            else:
                raise RuntimeError( f'Invalid book parameter passed {type( book )}')
            
        return self._current_book_id
    
    def lookup_books_by_column( self, column:str, value:str )->list[int]:
        """ Find book IDs by any column. This will return a list """
        sql = MixinBookID.SQL_MX_LOOKUP_BY_COLUMN.replace( '::column', column )
        all_rows =  DbHelper.fetchrows( sql , [value], [ BOOK.id ])
        return [ row[ BOOK.id ] for row in all_rows ]
        
    def lookup_book_by_column(self, column:str, value:str )->int|None:
        """ Find a single book by a column query. If more than one exists, return None"""
        all = self.lookup_books_by_column( column, value )
        return None if all is None or len(all)>1 else int( all[0])
        