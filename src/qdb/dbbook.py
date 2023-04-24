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

import os
from pickle import GET
from util.convert import toInt
from qdb.dbconn import DbConn
from qdb.dbsystem import DbSystem
from qdb.keys import DbKeys, BOOK
from qdb.mixin.bookid import MixinBookID
from qdb.dbgeneric import DbGenericName
from qdb.util import DbHelper
from qdb.base import DbBase
from PySide6.QtSql import QSqlQuery


class DbGenre(DbGenericName):
    def __init__(self):
        super().__init__()
        self.tableName = 'Genre'
        self.setupLogger()

    def getactive(self) -> list:
        SQL_GET_ACTIVE = 'SELECT name FROM Genre WHERE Genre.id IN ( SELECT genre_id FROM Book ) ORDER BY name'
        return self.getColumn(SQL_GET_ACTIVE)


class DbComposer(DbGenericName):
    def __init__(self):
        super().__init__()
        self.tableName = 'Composer'
        self.setupLogger()

    def getactive(self) -> list:
        SQL_GET_ACTIVE = 'SELECT name FROM Composer WHERE Composer.id IN ( SELECT composer_id FROM Book ) ORDER BY name'
        return self.getColumn(SQL_GET_ACTIVE)

class DbBook(MixinBookID, DbBase):
    
    SQL_DELETE = """
            DELETE FROM Book 
            WHERE book=?;
        """
    SQL_DELETE_BY_COLUMN="""
        DELETE FROM Book 
            WHERE ::column=?
    """
    SQL_DELETE_ALL = """DELETE FROM Book"""
    SQL_EDIT_COMPOSER = "UPDATE Book SET composer_id=? WHERE composer_id = ?"
    SQL_EDIT_GENRE = "UPDATE Book SET genre_id=? WHERE genre_id = ?"
    SQL_GET_BOOK_SETTINGS_BY_ID = "SELECT key, value FROM BookSetting WHERE book_id = ?"
    SQL_GET_COUNT = "SELECT count(*) FROM Book"
    SQL_IS_BOOK_FIELD = 'SELECT EXISTS ( SELECT 1 FROM Book WHERE ::key = ? ) as Bool'
    SQL_INSERT_BOOK = """INSERT INTO Book ( book, total_pages, location, name_default ) VALUES (? , ? , ? , '1')"""
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
        WHERE  :filterName = ?
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
        self.setupLogger()
        self.columnBook = DbConn.getColumnNames('Book')
        self.columnView = DbConn.getColumnNames('BookView')
        if not DbBook.SQL_IS_EXPANDED:
            DbBook.SQL_BOOK_INCOMPLETE = DbHelper.addColumnNames(
                DbBook.SQL_BOOK_INCOMPLETE, self.columnBook)

            DbBook.SQL_GET_BOOKVIEW = DbHelper.addColumnNames(
                DbBook.SQL_GET_BOOKVIEW, self.columnView)
            DbBook.SQL_GET_BOOKVIEW_BY = DbHelper.addColumnNames(
                DbBook.SQL_GET_BOOKVIEW_BY, self.columnView)
            DbBook.SQL_SELECT_BOOKVIEW_ALL = DbHelper.addColumnNames(
                DbBook.SQL_SELECT_BOOKVIEW_ALL, self.columnView)
            DbBook.SQL_SELECT_BOOKVIEW_FILTER = DbHelper.addColumnNames(
                DbBook.SQL_SELECT_BOOKVIEW_FILTER, self.columnView)
            DbBook.SQL_SELECT_BOOKVIEW_LIKE = DbHelper.addColumnNames(
                DbBook.SQL_SELECT_BOOKVIEW_LIKE, self.columnView)
            DbBook.SQL_GET_BOOKVIEW_BY_ID = DbHelper.addColumnNames(
                DbBook.SQL_GET_BOOKVIEW_BY_ID , self.columnView )

            DbBook.SQL_IS_EXPANDED = True

    def _checkColumn(self, colname):
        if colname not in self.columnBook:
            msg = "Invalid column name {}".format(colname)
            raise ValueError(msg)

    def _checkColumnView(self, colname):
        if colname not in self.columnView:
            msg = "Invalid column name {} in view".format(colname)
            raise ValueError(msg)

    def _checkIfExists(self, key: str = None, value: str = None) -> bool:
        if not key or not value:
            return False

        sql = DbBook.SQL_IS_BOOK_FIELD.replace('::key', key)
        returnID = DbHelper.fetchone(sql, value, default=0)
        return (int(returnID) > 0)


    """ -----------------------------------------------
            UTITLITY METHODS
        -----------------------------------------------
    """

    def cleanupArguments(self, kwargs) -> dict:
        """ cleanupArguments will strip out composer and genre, replacing them with composer_id and genre_id"""
        convertEntries = {}
        composerName = kwargs.pop('composer', None)
        genreName = kwargs.pop('genre', None)

        if composerName is not None:
            convertEntries['composer_id'] = DbComposer().getID(
                composerName, create=True)
        if genreName is not None:
            convertEntries['genre_id'] = DbGenre().getID(
                genreName, create=True)
        return convertEntries

    """ -----------------------------------------------
            INFORMATION METHODS
        -----------------------------------------------
    """
    def count(self) -> int:
        """ Return a count of how many books are in the database """
        return int(DbHelper.fetchone(DbBook.SQL_GET_COUNT, default=0))

    def isBook(self, bookName: str) -> bool:
        return self._checkIfExists(BOOK.book, bookName)

    def isLocation(self, location: str) -> bool:
        """ Check if the location exists """
        return self._checkIfExists(BOOK.location, location)

    def isSource(self, source: str) -> bool:
        """ Check if the book source is already in the library"""
        return self._checkIfExists(BOOK.source, source)

    def getUniqueName(self, name: str) -> str:
        """
            If you are adding a book but the name is there but
            its source is different, this will give you a unique name

            You should also check to see if the book is already added by 
            checking with 'isSource()'. If it is, delete the entry and addNew
        """
        if self.isBook(name):
            pattern = '{}%'.format(name)
            query = DbHelper.bind(DbHelper.prep(
                "SELECT count(*) as count FROM Book WHERE book LIKE ?"), pattern)
            if query.exec() and query.next():
                count = query.value(0)
            else:
                count = 0
            self._checkError(query)
            query.finish()
            del query
            if count is not None and count > 0:  # shouldn't have gotten here!
                return "{} [{}]".format(name, 1+int(count))
        return name

    def sourcesExist(self, sources: list[str]) -> list[list]:
        """
            Pass in a list of locations and determine if the books
            are referenced. Return list of sources that ARE in the database
        """
        fileList = []
        if sources is not None:
            if not isinstance( sources , list ):
                sources = [ sources ]
            if len( sources ) > 0 :
                sql = 'SELECT source FROM Book WHERE source in ({})'.format( ','.join('?'*len( sources ) ) )
                query = DbHelper.bind( DbHelper.prep( sql),  sources )
                if query.exec():
                    fileList = DbHelper.allList( query , 0 )
                else:
                    print( query.lastError().text())
        return fileList


    """ -----------------------------------------------
            RECORD READ METHODS
        -----------------------------------------------
    """   
    def getId(self, book: str) -> int:
        """ Shim for backward compatibility """
        return self.lookup_book_id( book )

    def getBookByColumn(self, column: str, value: str) -> dict:
        """ Get book by column """
        self._checkColumnView(column)
        sql = DbBook.SQL_GET_BOOKVIEW_BY.replace('::column', column)
        return DbHelper.fetchrow(sql,  value, self.columnView)

    def getBookById(self, id: int) -> dict:
        """ Get book by record ID """
        return DbHelper.fetchrow(DbBook.SQL_GET_BOOKVIEW_BY_ID,  id , self.columnView )

    def getBook(self, book: str) -> dict:
        """ Get book by book name """
        return DbHelper.fetchrow(DbBook.SQL_GET_BOOKVIEW, book, self.columnView)

    def getFilterBooks(self, filterName: str, filter: str, orderList: list = ['book']):
        """
            Retrieve all the books, ordered by 'order' and filtered by a column.
            This allows searches for queries.
            You can ask for all entries and get a list or book dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one
        """
        self._checkColumnView(filterName)
        sql = DbBook.SQL_SELECT_BOOKVIEW_FILTER.replace(
            ':filterName', filterName)
        sql = sql.replace(':order', ','.join(orderList))

        return DbHelper.fetchrows(sql, filter, self.columnView, endquery=self._checkError)

    def getLike(self, filter: str):
        sql = DbBook.SQL_SELECT_BOOKVIEW_LIKE.replace(':filter', filter)
        return DbHelper.fetchrows(sql, None, self.columnView, endquery=self._checkError)

    def getAll(self, order: str = 'book', fetchall=True):
        """
            Retrieve all the books, ordered by 'order'.
            You can ask for all entries and get a list or book dictionaries
            Or you can get a 'query' returned so you can retrieve them one-by-one
        """
        sql = DbBook.SQL_SELECT_BOOKVIEW_ALL.replace(':order', order)
        if fetchall:
            return DbHelper.fetchrows(sql, None, self.columnView, endquery=self._checkError)
        query = DbHelper.prep(sql)
        query.exec()
        return query

    def getAllNext(self, query: QSqlQuery) -> dict:
        """
            This will return a dictionary, or none, of the next record
            started with getAll.  It is a simple wrapper to DbHelper.record
        """
        return DbHelper.record(query, self.columnView)

    def getRecent(self, limit: int = 10):
        """
            Retrieve records from the books in date order (descending)
            limit is between 5 and 20. If you pass a non-int value, it will default to 10.
        """
        limit = toInt(limit, 10)
        limit = str(min(20, max(limit, 5)))  # must be between 5 and 20
        sql = DbBook.SQL_SELECT_RECENT.replace(':limit', limit)

        return DbHelper.fetchrows(sql, None, DbBook.COL_SELECT_RECENT, endquery=self._checkError)

    def getRecentNext(self, query: QSqlQuery) -> dict:
        return DbHelper.record(query, DbBook.COL_SELECT_RECENT)

    def getIncompleteBooks(self):
        """
        This will get a list of books that don't have pages set or genre and composer set
        You can then prompt for each book to be updated
        A list of reasons will be passed back. the field with a problem will be 'field:'
        """
        bookList = {}
        rows = DbHelper.fetchrows(
            DbBook.SQL_BOOK_INCOMPLETE, None, self.columnBook, endquery=self._checkError)
        if rows is not None:
            for row in rows:
                reasons = []
                if row['name_default'] == 1:
                    reasons.append(
                        'name: Default name used is "{}"'.format(row['book']))
                if row['composer_id'] is None or row['composer_id'] == '':
                    reasons.append("composer: entry is empty")
                if row['genre_id'] is None or row['genre_id'] == '':
                    reasons.append("genre: entry is empty")
                if row['numbering_starts'] == row['numbering_ends']:
                    reasons.append("numbering: Page numbering isn't set")

                bookList[row['book']] = reasons
        return bookList


    """ -----------------------------------------------
            RECORD UPDATE/ ADD  METHODS
        -----------------------------------------------
    """

    def updateName(self, oldName, newName):
        """
            This is a short way to rename a book from 'oldname'
            to 'newname'. Keys that begin with an * will cause
            a rename to occur in the 'set'
        """
        changeList = {"book": oldName, "*book": newName.strip()}
        self.update(**changeList)

    def updateReadDate(self, bookName) -> bool:
        query = DbHelper.prep(DbBook.SQL_UPDATE_READ_DATE)
        query.addBindValue(bookName)
        return query.exec()

    def update(self, **kwargs) -> int:
        newAdditions = self.cleanupArguments(kwargs)
        kwargs.update(newAdditions)

        if BOOK.id in kwargs:
            id = kwargs.pop(BOOK.id)
        else:
            id = self.lookup_book_id(kwargs.pop(BOOK.name))

        sql = self._formatUpdateVariable('Book', BOOK.id, kwargs)

        query = DbHelper.prep(sql)
        values = list(kwargs.values())
        values.append(id)
        query = DbHelper.bind(query, values)
        return id if query.exec() else -1

    def upsertBook(self, **kwargs) -> int:
        '''
            Update or insert a book into the database.
            This requires keyword parms (book="", pages="", etc)
        '''
        id = self.add(**kwargs)
        if id < 1:
            id = self.update(**kwargs)
        return id

    def add(self, **kwargs) -> int:
        """
            Add a book to the database.
            this requires keyword parms (book='', pages='', etc.)
            If you try and add a duplicate record, you will get an 
            sqlite3.IntegrityError exception.
            The return is the record ID (>0)
        """
        
        if BOOK.composer_id not in kwargs and BOOK.composer not in kwargs:
            kwargs['composer'] = 'Unknown'
        if BOOK.composer_id not in kwargs and BOOK.genre not in kwargs:
            kwargs['genre'] = 'Unknown'
        if BOOK.source not in kwargs:
            kwargs[BOOK.source] = None
        if BOOK.nameDefault not in kwargs:
            kwargs[BOOK.nameDefault] = 0
            
        kwargs.update(self.cleanupArguments(kwargs))
        query = DbHelper.prep( self._formatInsertVariable('Book', kwargs) )
        query = DbHelper.bind(query, list(kwargs.values()))
        id = (query.lastInsertId() if query.exec() else -1)
        self._checkError(query)
        query.finish()
        return id


    """ -----------------------------------------------
            RECORD DELETE METHODS
        -----------------------------------------------
    """
    def delBook(self, bookname: str) -> int:
        """
            Delete a book from the database by book
            Pass either book name or by named parameters
        """
        query = DbHelper.bind(DbHelper.prep(DbBook.SQL_DELETE), bookname)
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._checkError(query)
        query.finish()
        return rtn

    def delbycolumn( self, column:str, value:str|int)->int:
        self._checkColumnView(column)
        sql = DbBook.SQL_DELETE_BY_COLUMN.replace('::column', column)
        query = DbHelper.bind(DbHelper.prep(sql), value)
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._checkError(query)
        query.finish()
        return rtn

    def delAllBooks(self) -> int:
        """
            Delete every book in the book table. Don't do this unless you are really sure
            as it cannot be undone
        """
        query = QSqlQuery(DbConn.db())
        rtn = (query.numRowsAffected() if query.exec(
            DbBook.SQL_DELETE_ALL) else 0)
        self._checkError(query)
        query.finish()
        del query
        return rtn    


    ######################################
    # Operate on 'sub' tables:
    # Genre, Composer
    ######################################

    def editAllComposers(self, oldvalue: str = None, newvalue: str = None, commit=True) -> int:
        """
            This acts to MIGRATE book records from one composer to another.
            It will create a new composer if needed.
        """
        if not oldvalue or not newvalue:
            return 0
        composer = DbComposer()
        oldID = composer.getID(oldvalue, create=False)
        if oldID is None:
            return 0
        newID = composer.getID(newvalue, create=True)

        query = DbHelper.bind(DbHelper.prep(
            DbBook.SQL_EDIT_COMPOSER), [newID, oldID])
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._checkError(query)
        query.finish()
        del query
        return rtn

    def editAllGenres(self, oldvalue: str = None, newvalue: str = None, commit=True) -> int:
        """
            This acts to MIGRATE book records from one genre to another.
            It will create a new genre if needed.
            (If you want to rename a genre, you need to use the DbGenre class)
        """
        if not oldvalue or not newvalue:
            return 0
        genre = DbGenre()
        oldID = genre.getID(oldvalue)
        if oldID is None:
            return 0
        newID = genre.getID(newvalue, create=True)
        query = DbHelper.bind(DbHelper.prep(
            DbBook.SQL_EDIT_GENRE), [newID, oldID])
        rtn = (query.numRowsAffected() if query.exec() else 0)
        self._checkError(query)
        query.finish()
        del query
        return rtn
