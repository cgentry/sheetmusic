# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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
import fnmatch
from pickle import GET
from util.convert    import toInt
from db.dbconn     import DbConn
from db.dbsql      import _forceDictionary, _sqlInsert, _sqlUpsert, SqlInsert,SqlUpdate, SqlColumnNames
from db.dbsystem   import DbSystem
from db.keys       import DbKeys, BOOK
from db.dbgeneric  import DbGenericName, DbTransform

class DbGenre( DbGenericName ):
    def __init__(self):
        super().__init__()
        self.tableName='Genre'
    
class DbComposer( DbGenericName ):
    def __init__(self):
        super().__init__()
        self.tableName='Composer'
    
class DbBook():
    SQL_DELETE="""
            DELETE FROM Book 
            WHERE book=:book;
        """
    SQL_DELETE_ALL = """DELETE FROM Book"""
    SQL_EDIT_COMPOSER="UPDATE Book SET composer_id=:newValue WHERE composer_id = :oldValue"
    SQL_EDIT_GENRE="UPDATE Book SET genre_id=:newValue WHERE genre_id = :oldValue"
    SQL_GET_BOOK="""
            SELECT * 
            FROM BookView 
            WHERE book = :book
            LIMIT 1"""
    SQL_GET_BOOK_BY="""
            SELECT * 
            FROM BookView 
            WHERE ::column = :value
            LIMIT 1
    """
    SQL_GET_BOOK_SETTINGS_BY_ID="SELECT key, value FROM BookSetting WHERE book_id = :id"
    SQL_GET_COUNT="SELECT count(*) FROM Book"
    SQL_IS_BOOK_FIELD='SELECT EXISTS ( SELECT 1 FROM Book WHERE ::field=:replace ) as Bool'
    SQL_SELECT_ALL="""
        SELECT * From BookView 
        ORDER BY :order 
        COLLATE NOCASE ASC"""  
    SQL_SELECT_FILTER="""
        SELECT * 
        FROM   BookView
        WHERE  :filterName = ?
        ORDER BY :order
    """
    SQL_SELECT_BOOK_LIKE="""
        SELECT  *
        FROM    BookView
        WHERE   book like '%:filter%'
        ORDER BY book, genre, composer
    """
    SQL_SELECT_RECENT="""
        SELECT book, location, last_read
        FROM   Book
        WHERE  date_read IS NOT NULL
        ORDER  BY date_read DESC
        LIMIT  :limit
    """
    SQL_BOOK_INCOMPLETE="""
        SELECT * FROM Book 
        WHERE  name_default=1 
            OR genre_id is NULL 
            OR composer_id is NULL 
            OR numbering_starts = numbering_ends"""   
    SQL_UPDATE_READ_DATE="UPDATE Book SET date_read = datetime('now') WHERE book = ?"
    
    def __init__(self):
        super().__init__()
        self.columnNames = SqlColumnNames( 'Book')
        self.columnView  = SqlColumnNames( 'BookView')

    def _checkColumn( self, colname ):
        if colname not in self.columnNames:
            msg = "Invalid column name {}".format( colname )
            raise ValueError(msg)

    def _checkColumnView( self, colname ):
        if colname not in self.columnView:
            msg = "Invalid column name {} in view".format( colname )
            raise ValueError(msg)

    def _addSettings( self, cursor, bookRow , id ):
        result = cursor.execute( self.SQL_GET_BOOK_SETTINGS_BY_ID , {"id": id })
        row = result.fetchone()
        while row is not None:
            bookRow[ row['key']] = row['value']
            row = result.fetchone()
        return bookRow

    def getId( self , book:str )->int:
        result = DbConn().cursor().execute( "SELECT id FROM Book WHERE book=?", [book]).fetchone()
        if result is not None:
            return int( result['id'])
        return None

    def getBookByColumn( self, column:str, value:str)->dict:
        self._checkColumnView( column)
        sql = self.SQL_GET_BOOK_BY.replace('::column', column )
        result = DbConn().cursor().execute( sql ,{"value": value} )
        return DbTransform().rowToDictionary( result.fetchone() )

    def getBookById( self, id:int )->dict:
        return self.getBookByColumn( BOOK.id , id )
        
    def getBook( self, *argv, order='DESC', **kwargs ):
        argsToPass = _forceDictionary( argv, kwargs, ['book'])
        result = DbConn().cursor().execute( self.SQL_GET_BOOK ,argsToPass )
        return DbTransform().rowToDictionary( result.fetchone() )
        
    def getFilterBooks( self, filterName, filter, orderList , fetch='all'):
        self._checkColumnView( filterName )
        sql = self.SQL_SELECT_FILTER.replace( ':filterName', filterName )
        sql = sql.replace( ':order' , ','.join( orderList ) )
        result = DbConn().cursor().execute( sql , [ filter ])
        if fetch == 'all':
            return result.fetchall()
        return result

    def getLike( self, filterName ):
        sql = self.SQL_SELECT_BOOK_LIKE.replace( ':filter', filterName )
        return DbConn().cursor().execute( sql )

    def getAll(self, *argv, order:str='book',fetch='all', **kwargs):
        """
            Retrieve a list of all the books
            Pass either 'bookname' or book='title'. 
            Order can by any field but default is by book title
            by using 'fetch' you can return the cursor OR a full list
        """
        sql = self.SQL_SELECT_ALL.replace(':order', order)
        result = DbConn().cursor().execute(sql)
        return ( result.fetchall() if fetch == 'all' else result )

    def getRecent( self, fetch='all', limit:int=10 ):
        """
            Retrieve records from the books in date order (descending)
            limit is between 5 and 20. If you pass a non-int value, it will default to 10.
        """
        limit = toInt( limit , 10 )
        limit = str( min( 20, max(limit, 5 )) ) # must be between 5 and 20
        result = DbConn().cursor().execute( self.SQL_SELECT_RECENT.replace(':limit', limit ) )
        return ( result.fetchall() if fetch == 'all' else result )

    def getTotal( self, *argv, **kwargs)->int:

        """
            How many books?
            Pass either 'title' or book='title'.
        """
        rows = DbConn().cursor().execute(self.SQL_GET_COUNT, _forceDictionary(argv, kwargs, 'book') )
        result = rows.fetchone()
        return int( result[0])

    def cleanupArguments( self, kwargs )->dict:
        convertEntries = {}
        composerName = kwargs.pop('composer',None)
        genreName = kwargs.pop( 'genre', None)

        if composerName is not None:
            convertEntries['composer_id'] = DbComposer().getorsetId( composerName )
        if genreName is not None:
            convertEntries['genre_id'] = DbGenre().getorsetId( genreName )
        return convertEntries

    def updateName( self, oldName, newName ):
        """
            This is a short way to rename a book from 'oldname'
            to 'newname'. Keys that begin with an * will cause
            a rename to occur in the 'set'
        """
        changeList = {"book": oldName , "*book": newName.strip() }
        self.update( **changeList )

    def updateReadDate(self, bookName ):
        DbConn().cursor().execute( self.SQL_UPDATE_READ_DATE , [bookName])

    def update( self, **kwargs ):
        newAdditions = self.cleanupArguments( kwargs )
        kwargs.update( newAdditions )
        return SqlUpdate( 'Book', **kwargs )

    def upsertBook( self, **kwargs ):
        '''
            Update or insert a book into the database.
            This requires keyword parms (book="", pages="", etc)
        '''
        kwargs.update( self.cleanupArguments( kwargs ))
        return _sqlUpsert( 'Book', kwargs )

    def addBook(self, **kwargs)->int:
        """
            Add a bookmark to the database.
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
            kwargs['BOOK.source'] = None
        if BOOK.nameDefault not in kwargs:
            kwargs[BOOK.nameDefault] = 0
        kwargs.update( self.cleanupArguments( kwargs ) )
        return _sqlInsert( 'Book', kwargs )

    def delBook(self, *argv, **kwargs ):
        """
            Delete a book from the database by book
            Pass either book name or by named parameters
        """
        (conn, cursor) = DbConn().openDB()
        argsToPass = _forceDictionary( argv, kwargs, 'book')
        cursor.execute( self.SQL_DELETE, argsToPass )
        conn.commit()
        return cursor.rowcount > 0

    def delAllBooks(self, *argv, **kwargs ):
        """
            Delete every book in the book table. Don't do this unless you are really sure
            as it cannot be undone
        """
        (conn, cursor) = DbConn().openDB()
        cursor.execute( self.SQL_DELETE_ALL, _forceDictionary(argv, kwargs, 'book'))
        conn.commit()
        return cursor.rowcount > 0

    def addBookDirectory(self, location=dir ):
        """
            Returns true if we added anything, 
            False is it we added nothing or you passed nothing for location
        """
        addedRecords=False
        if location is None or location == "":
            return (False,"Location is empty")
        if not os.path.isdir( location ):
            return (False, "Location '{}' is not a directory".format( location ))
        sys = DbSystem()
        keys = DbKeys()
        type = sys.getValue(keys.SETTING_FILE_TYPE, 'png')
        for bookDir in [f.path for f in os.scandir(location) if f.is_dir()] :
            if not self.isLocation(bookDir ):
                pages = len(fnmatch.filter(os.listdir(bookDir), '*.' + type))
                name = os.path.basename( bookDir )
                recordID = SqlInsert("Book", book=name, total_pages=pages, location=bookDir, name_default=1)
                addedRecords = addedRecords or ( recordID >= 0 )
        addedMessage = "Records added" if addedRecords else "No new records found"
        return (addedRecords, addedMessage )

    def getIncompleteBooks( self ):
        """
        This will get a list of books that don't have pages set or genre and composer set
        You can then prompt for each book to be updated
        A list of reasons will be passed back. the field with a problem will be 'field:'
        """
        bookList={}
        result=DbConn().cursor().execute(self.SQL_BOOK_INCOMPLETE)
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                reasons = []
                if row['name_default'] == 1:
                    reasons.append('name: Default name used is "{}"'.format( row['book']))
                if row['composer_id'] is None or row['composer_id'] == '':
                    reasons.append("composer: entry is empty")
                if row['genre_id'] is None or row['genre_id'] == '' :
                    reasons.append("genre: entry is empty")
                if row['numbering_starts'] == row['numbering_ends']:
                    reasons.append("numbering: Page numbering isn't set")
                
                bookList[ row['book'] ] = reasons
        return bookList

    def _checkIfExists( self, fieldName:str, replace:str)->bool:
        if fieldName is None or replace is None or replace=='':
            return False
        sql = self.SQL_IS_BOOK_FIELD.replace('::field', fieldName )
        row = DbConn().cursor().execute( sql, {'replace': replace }).fetchone()
        return ( int( row[0] ) > 0 )

    def isBook( self, bookName:str )->bool:
        return self._checkIfExists( BOOK.book , bookName )

    def isLocation( self, location:str)->bool:
        return self._checkIfExists( BOOK.location , location )

    def isSource( self, source:str)->bool:
        return self._checkIfExists( BOOK.source , source )

    def getUniqueName( self, name:str )->str:
        """
            So, if you are adding a book but the name is there but
            its source is different, this will give you a unique name
            
            You should also check to see if the book is already added by 
            checking with 'isSource()'. If it is, delete the entry and addNew
        """
        if not self.isBook( name ):
            return name
        formatString = "{} [{}]"
        pattern = {'pattern' : formatString.format( name , '%') }
        result = DbConn().cursor().execute( "SELECT count(*) as count FROM Book where book like :pattern", pattern  ).fetchone()
        return formatString.format( name, 1+int(result[ 'count']) )

    def sourcesExist( self, sources:list )->list:
        """
            Pass in a list of locations and determine if the books
            are referenced. Return list of sources that ARE in the database
        """
        fileList = []
        for source in sources:
            if self.isSource( source ):
                fileList.append( source )
        return fileList

    ######################################
    # Operate on 'sub' tables:
    # Genre, Composer
    ######################################
    

    def editAllComposers( self, oldvalue:str=None, newvalue:str=None, commit=True)->int:
        """
            This acts to MIGRATE book records from one composer to another.
            It will create a new composer if needed.
        """
        if oldvalue is None or newvalue is None:
            return 0
        composer = DbComposer()
        oldID = composer.getID( oldvalue )
        if oldID is None:
            return 0
        newID = composer.getorsetId( newvalue , create=True)
        (conn, cursor) = DbConn().openDB()
        cursor.execute(self.SQL_EDIT_COMPOSER, {'newValue' : newID, 'oldValue': oldID })
        if commit:
            conn.commit()
        return cursor.rowcount 

    def editAllGenres( self, oldvalue:str=None, newvalue:str=None, commit=True)->int:
        """
            This acts to MIGRATE book records from one genre to another.
            It will create a new genre if needed.
            (If you want to rename a genre, you need to use the DbGenre class)
        """
        if oldvalue is None or newvalue is None:
            return 0
        composer = DbGenre()
        oldID = composer.getID( oldvalue )
        if oldID is None:
            return 0
        newID = composer.getorsetId( newvalue , create=True)
        (conn, cursor) = DbConn().openDB()
        cursor.execute(self.SQL_EDIT_GENRE, {'newValue' : newID, 'oldValue': oldID })
        if commit:
            conn.commit()
        return cursor.rowcount 

    
    #def isComposer( self, composer:str )->bool:
   