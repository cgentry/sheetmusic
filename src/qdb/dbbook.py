"""
Database interface: Book, Genre, and Composer tables

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtSql import QSqlQuery

from qdb.fields.book import BookField
from qdb.base import DbBase
from qdb.dbconn import DbConn
from qdb.dbgeneric import DbGenericName
from qdb.mixin.bookid import MixinBookID
from qdb.util import DbHelper

from util.convert import to_int


class DbGenre(DbGenericName):
    """Database Genre class based on a generic-table type

    Args:
        DbGenericName (): Generic named class
    """

    def __init__(self):
        super().__init__()
        self.table_name = 'Genre'
        self.setup_logger()

    def getactive(self) -> list:
        """Get genre name using current book

        Returns:
            list: contains name of genre
        """
        sql_get_active = """SELECT name
        FROM Genre
        WHERE Genre.id
        IN (
            SELECT genre_id
            FROM Book
        )
        ORDER BY name"""
        return self.get_column(sql_get_active)


class DbComposer(DbGenericName):
    """Database interface for Composer table

    Args:
        DbGenericName (): Generic database name class
    """

    def __init__(self):
        super().__init__()
        self.table_name = 'Composer'
        self.setup_logger()

    def getactive(self) -> list:
        """Get composers that are currently used

        Returns:
            list: list of composer names
        """
        sql_get_active = '''SELECT name
        FROM Composer
        WHERE Composer.id IN
           ( SELECT composer_id FROM Book )
        ORDER BY name'''
        return self.get_column(sql_get_active)


class DbBook(MixinBookID, DbBase):
    """
        Low level access to book
    """
    SQL_DELETE = """
            DELETE FROM Book
            WHERE book=?;
        """
    SQL_DELETE_BY_COLUMN = """
        DELETE FROM Book
            WHERE ::column=?
    """
    SQL_DELETE_ALL = """DELETE FROM Book"""
    SQL_GET_BOOK_SETTINGS_BY_ID = "SELECT key, value FROM BookSetting WHERE book_id = ?"
    SQL_GET_COUNT = "SELECT count(*) FROM Book"
    SQL_IS_BOOK_FIELD = 'SELECT EXISTS ( SELECT 1 FROM Book WHERE ::key = ? ) as Bool'
    SQL_INSERT_BOOK = """INSERT INTO Book
    ( book, total_pages, location, name_default )
    VALUES (? , ? , ? , '1')"""
    SQL_SELECT_RECENT = """
        SELECT book, location, last_read
        FROM   Book
        WHERE  date_read IS NOT NULL
        ORDER  BY date_read DESC
        LIMIT  :limit
        """
    SQL_UPDATE_READ_DATE = "UPDATE Book SET date_read = datetime('now') WHERE book = ?"

    # The following have field substitutions
    SQL_SELECT_BOOKVIEW_ALL = """
        SELECT * From BookView
        ORDER BY :order
        COLLATE NOCASE ASC"""
    SQL_GET_BOOKVIEW_BY_ID = """
            SELECT *
            FROM BookView
            WHERE id = ?
            LIMIT 1"""
    SQL_GET_BOOKVIEW = """
            SELECT *
            FROM BookView
            WHERE book = ?
            LIMIT 1"""
    SQL_GET_BOOKVIEW_BY = """
            SELECT *
            FROM BookView
            WHERE ::column = ?
            LIMIT 1"""
    SQL_SELECT_BOOKVIEW_FILTER = """
        SELECT *
        FROM   BookView
        WHERE  :filter_column = ?
        ORDER BY :order
    """
    SQL_SELECT_BOOKVIEW_LIKE = """
        SELECT  *
        FROM    BookView
        WHERE   book like '%:filter%'
        ORDER BY book, genre, composer"""
    COL_SELECT_RECENT = ['book', 'location', 'last_read']
    SQL_BOOK_INCOMPLETE = """
        SELECT *
        FROM Book
        WHERE  name_default=1
            OR genre_id is NULL
            OR composer_id is NULL
            OR numbering_starts = numbering_ends"""
    SQL_IS_EXPANDED = False

    def __init__(self):
        super().__init__()
        self.setup_logger()
        self.column_book = DbConn.get_column_names('Book')
        self.column_view = DbConn.get_column_names('BookView')
        if not DbBook.SQL_IS_EXPANDED:
            DbBook.SQL_BOOK_INCOMPLETE = DbHelper.add_column_names(
                DbBook.SQL_BOOK_INCOMPLETE, self.column_book)

            DbBook.SQL_GET_BOOKVIEW = DbHelper.add_column_names(
                DbBook.SQL_GET_BOOKVIEW, self.column_view)
            DbBook.SQL_GET_BOOKVIEW_BY = DbHelper.add_column_names(
                DbBook.SQL_GET_BOOKVIEW_BY, self.column_view)
            DbBook.SQL_SELECT_BOOKVIEW_ALL = DbHelper.add_column_names(
                DbBook.SQL_SELECT_BOOKVIEW_ALL, self.column_view)
            DbBook.SQL_SELECT_BOOKVIEW_FILTER = DbHelper.add_column_names(
                DbBook.SQL_SELECT_BOOKVIEW_FILTER, self.column_view)
            DbBook.SQL_SELECT_BOOKVIEW_LIKE = DbHelper.add_column_names(
                DbBook.SQL_SELECT_BOOKVIEW_LIKE, self.column_view)
            DbBook.SQL_GET_BOOKVIEW_BY_ID = DbHelper.add_column_names(
                DbBook.SQL_GET_BOOKVIEW_BY_ID, self.column_view)

            DbBook.SQL_IS_EXPANDED = True

    def _check_column(self, colname):
        if colname not in self.column_book:
            msg = f"Invalid column name {colname}"
            raise ValueError(msg)

    def _check_column_view(self, colname: str):
        """Check to see if column name is in view

        Args:
            colname (str): name of column that must exist

        Raises:
            ValueError: string
        """
        if colname not in self.column_view:
            msg = f"Invalid column name {colname} in view"
            raise ValueError(msg)

    def _key_value_exists(self, key: str = None, value: str = None) -> bool:
        """Check to see if a key/value pair exists in database

        Args:
            key (str, optional): _description_. Defaults to None.
            value (str, optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """
        if not key or not value:
            return False

        sql = DbBook.SQL_IS_BOOK_FIELD.replace('::key', key)
        key_found = DbHelper.fetchone(sql, param=value, default=0)
        return int(key_found) > 0

    def _clean_args(self, kwargs) -> dict:
        """ cleanupArguments will strip out composer and genre
        Replace them with composer_id and genre_id
        """
        convert_entries = {}
        composer = kwargs.pop('composer', None)
        genre = kwargs.pop('genre', None)

        if composer is not None:
            convert_entries['composer_id'] = DbComposer().get_id(
                composer, create=True)
        if genre is not None:
            convert_entries['genre_id'] = DbGenre().get_id(
                genre, create=True)
        return convert_entries

    def count(self) -> int:
        """ Return a count of how many books are in the database """
        return DbHelper.count('Book')

    def is_book(self, book_name: str) -> bool:
        """Check to see if book exists

        Args:
            book_name (str): Name of book to find

        Returns:
            bool: True if found, False if not
        """
        return self._key_value_exists(BookField.BOOK, book_name)

    def is_location(self, location: str) -> bool:
        """Check to see if location exists

        Args:
            location (str): Name of location to find

        Returns:
            bool: True if found, False if not
        """
        return self._key_value_exists(BookField.LOCATION, location)

    def is_source(self, source: str) -> bool:
        """ Check if the book source is already in the library"""
        return self._key_value_exists(BookField.SOURCE, source)

    def sources_exist(self, sources: list[str]) -> list[list]:
        """
            Pass in a list of locations and determine if the books
            are referenced. Return list of sources that ARE in the database
        """
        file_list = []
        if sources is not None:
            if not isinstance(sources, list):
                sources = [sources]
            if len(sources) > 0:
                slist = ','.join('?'*len(sources))
                sql = f'SELECT source FROM Book WHERE source in ({slist})'
                query = DbHelper.bind(DbHelper.prep(sql),  sources)
                if query.exec():
                    file_list = DbHelper.all_list(query, 0)
                else:
                    print(query.lastError().text())
        return file_list

    def getbook_bycolumn(self, column: str, value: str) -> dict:
        """ Get book by column """
        self._check_column_view(column)
        sql = DbBook.SQL_GET_BOOKVIEW_BY.replace('::column', column)
        return DbHelper.fetchrow(sql,  value, self.column_view)

    def getbook_byid(self, book_id: int) -> dict:
        """Get book by ID number

        Args:
            book_id (int): book id number

        Returns:
            dict: complete book in dictionary form
        """
        return DbHelper.fetchrow(DbBook.SQL_GET_BOOKVIEW_BY_ID,  book_id, self.column_view)

    def getbook(self, book: str) -> dict:
        """Get a single book by the book name

        Args:
            book (str): Book name

        Returns:
            dict: _description_
        """
        return DbHelper.fetchrow(DbBook.SQL_GET_BOOKVIEW, book, self.column_view)

    def getbooks_filtered(self, filter_column: str, value: str, orderby: list = None):
        """Retrieve all the books, ordered by 'order' and filtered by a column.
            This allows searches for queries.
            You can ask for all entries and get a list or book dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one

        Args:
            filtername (str): _description_
            filterby (str): _description_
            o (list, optional): _description_. Defaults to ['book'].

        Returns:
            _type_: _description_
        """
        if order_by is None:
            order_by = ['book']
        self._check_column_view(filter_column)
        sql = DbBook.SQL_SELECT_BOOKVIEW_FILTER.replace(
            ':filter_column', filter_column)
        sql = sql.replace(':order', ','.join(orderby))

        return DbHelper.fetchrows(sql, value, self.column_view, endquery=self._check_error)

    def similar_titles(self, book_name: str) -> list:
        """Fetch a list of titles that match the book name

        Args:
            book_name (str): name of book.

        Returns:
            list: list of list of books
        """
        sql = DbBook.SQL_SELECT_BOOKVIEW_LIKE.replace(':filter', book_name)
        return DbHelper.fetchrows(sql, None, self.column_view, endquery=self._check_error)

    def get_all(self, order: str = 'book', fetchall=True):
        """
            Retrieve all the books, ordered by 'order'.
            You can ask for all entries and get a list or book dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one
        """
        sql = DbBook.SQL_SELECT_BOOKVIEW_ALL.replace(':order', order)
        if fetchall:
            return DbHelper.fetchrows(sql, None, self.column_view, endquery=self._check_error)
        query = DbHelper.prep(sql)
        query.exec()
        return query

    def get_all_next(self, query: QSqlQuery) -> dict:
        """
            This will return a dictionary, or none, of the next record
            started with getAll.  It is a simple wrapper to DbHelper.record
        """
        return DbHelper.record(query, self.column_view)

    def get_recent(self, limit: int = 10):
        """
            Retrieve records from the books in date order (descending)
            limit is between 5 and 20. If you pass a non-int value, it will default to 10.
        """
        limit = to_int(limit, 10)
        limit = str(min(20, max(limit, 5)))  # must be between 5 and 20
        sql = DbBook.SQL_SELECT_RECENT.replace(':limit', limit)

        return DbHelper.fetchrows(sql, None, DbBook.COL_SELECT_RECENT, endquery=self._check_error)

    def get_incomplete_books(self):
        """
        This will get a list of books that don't have pages set or genre and composer set
        You can then prompt for each book to be updated
        A list of reasons will be passed back. the field with a problem will be 'field:'
        """
        book_list = {}
        rows = DbHelper.fetchrows(
            DbBook.SQL_BOOK_INCOMPLETE, None, self.column_book, endquery=self._check_error)
        if rows is not None:
            for row in rows:
                reasons = []
                if row['name_default'] == 1:
                    reasons.append(
                        f'name: Default name used is "{row["book"]}"')
                if row['composer_id'] is None or row['composer_id'] == '':
                    reasons.append("composer: entry is empty")
                if row['genre_id'] is None or row['genre_id'] == '':
                    reasons.append("genre: entry is empty")
                if row['numbering_starts'] == row['numbering_ends']:
                    reasons.append("numbering: Page numbering isn't set")

                book_list[row['book']] = reasons
        return book_list

    def update_name(self, old_name, new_name):
        """
            This is a short way to rename a book from 'oldname'
            to 'newname'. Keys that begin with an * will cause
            a rename to occur in the 'set'
        """
        change_list = {"book": old_name, "*book": new_name.strip()}
        self.update(**change_list)

    def update_read_date(self, book_name: str) -> bool:
        """update the date a book was last read to today

        Args:
            book_name (str): Book title (not ID)

        Returns:
            bool: True if name changed, false if stays the same
        """
        query = DbHelper.prep(DbBook.SQL_UPDATE_READ_DATE)
        query.addBindValue(book_name)
        return query.exec()

    def update(self, **kwargs) -> int:
        """Update a book passing the an array of key/values

        This can accept almost any key/value dictionary pairs
        but it must contain either field of 'id' or 'name'
        Only key/value pairs will be updated. This will not
        change the book name or id

        Returns:
            int: Books 'id' field or -1 if no change occured.
        """
        new_additions = self._clean_args(kwargs)
        kwargs.update(new_additions)

        if BookField.ID in kwargs:
            book_id = kwargs.pop(BookField.ID)
        else:
            book_id = self.lookup_book_id(kwargs.pop(BookField.NAME))

        sql = self._format_update_variable('Book', BookField.ID, kwargs)

        query = DbHelper.prep(sql)
        values = list(kwargs.values())
        values.append(book_id)
        query = DbHelper.bind(query, values)
        return book_id if query.exec() else -1

    def upsert_book(self, **kwargs) -> int:
        '''
            Update or insert a book into the database.
            This requires keyword parms (book="", pages="", etc)
        '''
        book_id = self.add(**kwargs)
        if book_id < 1:
            book_id = self.update(**kwargs)
        return book_id

    def add(self, **kwargs) -> int:
        """
            Add a book to the database.
            this requires keyword parms (book='', pages='', etc.)
            If you try and add a duplicate record, you will get an
            sqlite3.IntegrityError exception.
            The return is the record ID (>0)
        """

        if BookField.COMPOSER_ID not in kwargs and BookField.COMPOSER not in kwargs:
            kwargs['composer'] = 'Unknown'
        if BookField.COMPOSER_ID not in kwargs and BookField.GENRE not in kwargs:
            kwargs['genre'] = 'Unknown'
        if BookField.SOURCE not in kwargs:
            kwargs[BookField.SOURCE] = None
        if BookField.NAME_DEFAULT not in kwargs:
            kwargs[BookField.NAME_DEFAULT] = 0

        kwargs.update(self._clean_args(kwargs))
        query = DbHelper.prep(self._format_insert_variable('Book', kwargs))
        query = DbHelper.bind(query, list(kwargs.values()))
        book_id = (query.lastInsertId() if query.exec() else -1)
        self._check_error(query)
        query.finish()
        return book_id

    def del_book(self, bookname: str) -> int:
        """
            Delete a book from the database by book
            Pass either book name or by named parameters
        """
        query = DbHelper.bind(DbHelper.prep(DbBook.SQL_DELETE), bookname)
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._check_error(query)
        query.finish()
        return rtn

    def del_by_column(self, column: str, value: str | int) -> int:
        """Delete books based on a column == value

        Args:
            column (str): Column that contains a value
            value (str | int): Value to find

        Returns:
            int: number of records deleted
        """
        self._check_column_view(column)
        sql = DbBook.SQL_DELETE_BY_COLUMN.replace('::column', column)
        query = DbHelper.bind(DbHelper.prep(sql), value)
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._check_error(query)
        query.finish()
        return rtn

    def delete_all(self) -> int:
        """Delete every book in the book table. Don't do this unless you are really sure
            as it cannot be undone

        Returns:
            int: number of books deleted
        """
        query = QSqlQuery(DbConn.db())
        rtn = (query.numRowsAffected() if query.exec(
            DbBook.SQL_DELETE_ALL) else 0)
        self._check_error(query)
        query.finish()
        del query
        return rtn

class Migrate(DbBase):
    """ Migrate will move either a composer or a genre from old to new ID
    Within the Book table are 'ID's linking to detail tables
    ( id, description )
    Migration allows you to 'move' the values from one to another

    """
    SQL_EDIT_COMPOSER = "UPDATE Book SET composer_id=? WHERE composer_id = ?"
    SQL_EDIT_GENRE = "UPDATE Book SET genre_id=? WHERE genre_id = ?"

    def _migrate( self, dbobject, sql:str, oldvalue: str = None, newvalue: str = None) -> int:
        if not oldvalue or not newvalue:
            return 0
        old_id = dbobject.get_id(oldvalue, create=False)
        if old_id is None:
            return 0
        new_id = dbobject.get_id(newvalue, create=True)

        query = DbHelper.bind(DbHelper.prep(
            sql), [new_id, old_id])
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._check_error(query)
        query.finish()
        del query
        return rtn

    def composers(self, current: str = None, new: str = None) -> int:
        """
            This acts to MIGRATE book records from one composer to another.
            It will create a new composer if needed.
        """
        return self._migrate(
                    DbComposer(),
                    Migrate.SQL_EDIT_COMPOSER,
                    current, new )

    def genres(self, current: str = None, new: str = None) -> int:
        """
            This acts to MIGRATE book records from one genre to another.
            It will create a new genre if needed.
            (If you want to rename a genre, you need to use the DbGenre class)
        """
        return self._migrate(
                    DbGenre(),
                    Migrate.SQL_EDIT_GENRE,
                    current, new )
