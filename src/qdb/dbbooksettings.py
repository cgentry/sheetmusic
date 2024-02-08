"""
Database Interface : Book Setting table

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from typing import Any
from PySide6.QtSql import QSqlQuery
from qdb.base import DbBase
from qdb.dbconn import DbConn
from qdb.fields.booksetting import BookSettingField
from qdb.keys import DbKeys
from qdb.util import DbHelper
from qdb.mixin.bookid import MixinBookID
from util.convert import to_bool, to_int

class DbBookSettings(MixinBookID, DbBase):
    """ Handle database calls to BookSetting and BookSettingView
    """
    SQL_BOOKSETTING_ALL = """SELECT * FROM BookSettingView WHERE book_id=? ORDER BY :order ASC"""
    SQL_BOOKSETTING_GET = """SELECT * FROM BookSettingView WHERE book_id=? AND key=?"""

    SQL_GET_VALUE = """
            SELECT value AS setting,
                   'setting' AS source
            FROM Booksetting
            WHERE book_id = ?
              AND key=?
        UNION ALL
            SELECT value AS setting,
                   'sytem' AS source
            FROM System
            WHERE key=?"""
    SQL_BOOKSETTING_FALLBACK = """
        SELECT   book, id AS book_id, System.key as key, System.value as value
            FROM Book, System
            WHERE Book.id=? AND System.key=?
        """
    SQL_BOOKSETTING_ADD = """
        INSERT {}INTO BookSetting (book_id, key, value )
        VALUES ( ? , ? , ?)
    """
    SQL_BOOKSETTING_UPSERT = """
        INSERT OR REPLACE INTO BookSetting (book_id, key, value )
        VALUES ( ?, ?, ?)
    """
    SQL_BOOKSETTING_DELETE = """DELETE FROM BookSetting WHERE book_id=:id AND key=?"""
    SQL_BOOKSETTING_DELETE_ALL = """DELETE FROM BookSetting WHERE book_id=?"""

    SQL_IS_EXPANDED = False

    encoded_keys = [BookSettingField.KEY_DIMENSIONS]
    encoded_bool = [DbKeys.SETTING_RENDER_PDF]

    def __init__(self, book: str = None):
        """
            Initialise the class. If you pass a book, it will be used
            as default
        """
        super().__init__()
        self.setup_logger()
        self.column_names = DbConn.get_column_names('BookSetting')
        self.column_view = DbConn.get_column_names('BookSettingView')
        if book is not None:
            self.lookup_book_id(book)
        if not DbBookSettings.SQL_IS_EXPANDED:
            DbBookSettings.SQL_BOOKSETTING_ALL = \
                DbHelper.add_column_names(
                    DbBookSettings.SQL_BOOKSETTING_ALL, self.column_view)
            DbBookSettings.SQL_BOOKSETTING_GET = \
                DbHelper.add_column_names(
                    DbBookSettings.SQL_BOOKSETTING_GET, self.column_view)
            DbBookSettings.SQL_IS_EXPANDED = True

    def _encode(self, key, value):
        if key in DbBookSettings.encoded_keys:
            return DbHelper.encode(value)
        if key in DbBookSettings.encoded_bool:
            if value is None:
                return None
            return 1 if value is True or value == 1 else 0
        return value

    def _decode(self, key, value, raw: bool = False):
        """ Call this to decode the value from the database
            If you pass it raw==True, it will just return the value
        """
        if not raw:
            if value is not None and key in DbBookSettings.encoded_keys:
                return DbHelper.decode(value)
            if key in DbBookSettings.encoded_bool:
                if value is None:
                    return None
                return value is True or value == 1 or value == '1'
        return value

    def _critical_log(self, label: str, book, book_id, key, err) -> None:
        msg = f"{label} Book: '{book}', BookID: '{book_id}' Key: '{key}' [{str(err)}]"
        self.logger.critical(msg, trace=True)

    def upsert_booksettings(self,
                            book: str | int = None,
                            key: str = None,
                            value: str = None,
                            ignore=False) -> bool:
        """ Update or insert a book setting. If the value is None, the value will be deleted """
        sqlid = None
        try:
            if book is None or key is None:
                raise ValueError(
                    f'No book or key passed BOOK: {book} KEY: {key} VALUE: {value}')
            sqlid = (book
                     if book is not None and isinstance(book, int)
                     else self.lookup_book_id(book))
        except Exception as err:
            self._critical_log(
                "upsert_booksettings (no book)",
                book,
                sqlid,
                key,
                err)
            if ignore:
                return False
            raise err
        if value is None:
            return self.delete_value(book, key, ignore=True) > 0
        value = self._encode(key, value)
        parms = [sqlid, key, value]
        query = DbHelper.bind(DbHelper.prep(
            DbBookSettings.SQL_BOOKSETTING_UPSERT, ), parms)
        query.exec()
        rtn = not self.is_error() and query.numRowsAffected() > 0
        self._check_error(query)
        query.finish()
        return rtn

    def get_all(self,
                book: str | int = None,
                order: str = 'key',
                fetchall: bool = True) -> list|QSqlQuery:
        """Retrieve all the booksettings, ordered by 'order' (key).
            You can ask for all entries and get a list of dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one

        Args:
            book (str | int, optional): _description_. Defaults to None.
            order (str, optional): _description_. Defaults to 'key'.
            fetchall (bool, optional): _description_. Defaults to True.

        Raises:
            ValueError: No book id

        Returns:
            list: _description_
        """
        if not book:
            raise ValueError('No book id')
        sql = DbBookSettings.SQL_BOOKSETTING_ALL.replace(':order', order)
        if fetchall:
            return DbHelper.fetchrows(sql,
                                      self.lookup_book_id(book),
                                      self.column_view,
                                      endquery=self._check_error)
        query = DbHelper.prep(sql)
        query.exec()
        self._check_error(query)
        return query

    def get_all_settings(self,
                         book: str | int | dict = None,
                         order: str = 'key',
                         raw: bool = False) -> dict:
        """ This returns all the settings for a book
            Order of data is by key unless you set 'order'
            If you don't want the values decoded, set 'raw' = true. No conversion will take place
        """
        settings = {}
        for entry in self.get_all(book, order):
            settings[entry['key']] = self._decode(
                entry['key'], entry['value'], raw)
        return settings

    def get_setting(self,
                    book: str | int | dict = None,
                    key: str = None,
                    fallback=True,
                    raw: bool = False):
        """ get a database setting for a book and a key
            If none is found, use the fallback
        """
        if not key:
            raise ValueError("No lookup key")
        book_id = self.lookup_book_id(book)
        parms = [book_id, key, key]
        rows = DbHelper.fetchrows(
            DbBookSettings.SQL_GET_VALUE, parms,
            ['setting', 'system'],
            endquery=self._check_error)
        if rows is not None and len(rows) > 0:
            if len(rows) == 1:
                if fallback:
                    return self._decode(key, rows[0]['setting'], raw=raw)
            else:
                return self._decode(key, rows[0]['setting'], raw=raw)
        return None

    def get_value(self,
                  book: str = None,
                  key: str = None,
                  fallback: bool = True,
                  default=None) -> Any:
        """ Fetch value for Book key or fallback to the system setting (if fallback is True )
            If no value exists, you get the default value
            If raw = True, no conversion occurs. You get whatever is there.
        """
        value = self.get_setting(book=book, key=key, fallback=fallback)
        return value if value is not None else default

    def get_bool(self, book=None, key=None, fallback=True, default=False) -> bool:
        """ Return a bool from the book value"""
        value = self.get_value(
            book=book, key=key, fallback=fallback, default=default)
        return to_bool(value)

    def get_int(self, book=None, key=None, fallback=True, default=0) -> int:
        """ Return an int value from the book """
        return to_int(self.get_value(book=book, key=key, fallback=fallback, default=default))

    def set_value(self, book: str | int, key: str, value=None, ignore=False) -> bool:
        """Set a column value using book or book id

        Args:
            book (str | int): Book name or ID.
            key (str): Column name to set.
            value (any, optional): Value to set for key.
                Defaults to None. (Delete key/value pair)
            ignore (bool, optional): Ignore errors.
                Defaults to False.

        Raises:
            ValueError: Key is required
            err: _description_

        Returns:
            bool: _description_
        """
        rtn = True
        try:
            if key is None or book is None:
                raise ValueError('Book and Key are required')

            value = self._encode(key, value)
            if value is None:
                return self.delete_value(book, key, ignore)
            book_id = self.lookup_book_id(book)
            if book_id is None:
                raise ValueError(f"No book found for {book}")
            parms = [book_id, key, value]
            sql = DbBookSettings.SQL_BOOKSETTING_ADD.format(
                ('OR IGNORE ' if ignore else ''))
            query = DbHelper.bind(DbHelper.prep(sql), parms)
            query.exec()
            self._check_error(query)
            rtn = self.was_good() and query.numRowsAffected() > 0

            query.finish()
        except Exception as err:
            self.logger.critical(
                "set_value_by_id BookID: '{id}' Key: '{key}' [{str(err)}]", trace=True)
            if ignore:
                return False
            raise err
        return rtn

    def delete_value(self, book: str | int = None, key=None, ignore=False) -> int:
        """Delete one key/value for book. If no book or key are passed an excepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted.

        Args:
            book (str | int, optional): Book name or ID. Defaults to None.
            key (_type_, optional): Key column. Defaults to None.
            ignore (bool, optional): Ignore db errors. Defaults to False.

        Raises:
            ValueError: No book or key passed
            err: Database error

        Returns:
            int: Number of rows affected
        """
        book_id = book
        try:
            if not book or key is None:
                raise ValueError('No book or key passed')
            book_id = self.lookup_book_id(book=book)
            parms = [self.lookup_book_id(book=book), key]
            query = DbHelper.bind(DbHelper.prep(
                DbBookSettings.SQL_BOOKSETTING_DELETE, ), parms)
            query.exec()
            self._check_error(query)
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self._critical_log(
                "delete_value.",
                book=book,
                book_id=book_id,
                key=None,
                err=err)
            if ignore:
                return 0
            raise err
        return rowcount

    def delete_all_values(self, book: str | int = None, ignore=False) -> int:
        """
            Delete one key for book. If no book or key are passed an excepion will be raised.
            If the book isn't found, you may get an exception (ignore=false)
            Return record number deleted. """
        try:
            if not book:
                raise ValueError('No book id')
            query = DbHelper.bind(
                DbHelper.prep(DbBookSettings.SQL_BOOKSETTING_DELETE_ALL),
                self.lookup_book_id(book))
            query.exec()
            self._check_error(query)
            rowcount = query.numRowsAffected()
            query.finish()
        except Exception as err:
            self._critical_log(
                "dbooksettings.delete_all_values.",
                book=book,
                book_id=book,
                key=None,
                err=err)
            if ignore:
                return 0
            raise err
        return rowcount
