from qdb.util   import DbHelper
from qdb.keys   import BOOK

class MixinBookID:
    """ This handles simple lookups to for Book ID. """
    SQL_MX_LOOKUP_BY_NAME='SELECT id FROM Book where book=?'
    SQL_MX_LOOKUP_BY_COLUMN='SELECT id FROM BookView WHERE ::column = ? ORDER BY id'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_book_id = None
        self._current_book_name = None

    def lookup_book_id(self, book: str | int) -> int|None:
        """ Fetch the book ID and cache it for future access. If none found, return None"""
        if book is None:
            return None
        if isinstance(book, str):
            if self._current_book_name != book or self._current_book_id is None:
                self._current_book_name = book
                self._current_book_id = DbHelper.fetchone(MixinBookID.SQL_MX_LOOKUP_BY_NAME, book, default=None)
                if self._current_book_id :
                    self._current_book_id = int( self._current_book_id )
        else:
            self._current_book_id = book
            self._current_book_name = None

        return self._current_book_id
    
    def lookup_books_by_column( self, column:str, value:str )->list:
        """ Find book IDs by any column. This will return a list """
        sql = MixinBookID.SQL_MX_LOOKUP_BY_COLUMN.replace( '::column', column )
        all =  DbHelper.fetchrows( sql , [value], [ BOOK.id ])
        return [ id for id in all.values() ]
        
    def lookup_book_by_column(self, column:str, value:str )->int|None:
        """ Find a single book by a column query. If more than one exists, return None"""
        all = self.lookup_books_by_column( column, value )
        return None if all is None or len(all)>1 else int( all[0])
        