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

from qdb.dbconn import DbConn
from qdb.util   import DbHelper
from qdb.base   import DbBase
from qdb.keys   import NOTE, BOOK
import logging
from PySide6.QtCore import QByteArray

class DbNote(DbBase):
    """
        You should have already opened the database.
        You can improve performance by instantiating this once 
        and all the statments get prepared. Makes it much faster
    """

    SQL_GET_ONE            = """SELECT * 
                                From Note
                                WHERE book_id= ?
                                AND   page=?
                                AND   sequence=?
                            """ 
    SQL_GET_ONE_BY_NAME    = """SELECT * FROM Note 
                                JOIN Book ON Book.id=Note.book_id
                                WHERE Book.book = ?
                                AND   Note.page = ?
                                AND   Note.sequence = ?
                            """
    SQL_GET_ALL            = """SELECT * 
                                From Note
                                WHERE book_id= ?
                                AND   page=?
                                ORDER BY sequence
                            """
    SQL_DELETE             = """DELETE FROM Note 
                                WHERE book_id= ?
                                AND   page=?
                                AND   sequence=?
                            """

    SQL_DELETE_PAGE_NOTES  = """DELETE FROM Note 
                                WHERE book_id= ?
                                AND   page=?
                            """
    SQL_COUNT_PAGE_NOTES   = """ SELECT COUNT(*) FROM Note
                                WHERE book_id = ?
                                AND   page = ?
                            """

    SQL_COUNT_PAGES        = """SELECT page , count( * ) as count
                                FROM Note
                                WHERE book_id = ?
                                GROUP BY page
                                ORDER BY page
                            """
    columnNames = None
    columnNames    = None

    SQL_IS_EXPANDED=False
    
    def __init__(self):
        super().__init__()
        if DbNote.columnNames is None or len( DbNote.columnNames) == 0 :
            DbNote.columnNames = DbConn.getColumnNames( 'Note')
        self.setupLogger()

    def getNote( self, book, page:int=0, seq:int=0 ,new=True)->dict:
        """ Get a note for a book's page and the sequence"""
        if isinstance( book, str ):
            rec =  DbHelper.fetchrow( DbNote.SQL_GET_ONE_BY_NAME , [book,page,seq] , DbNote.columnNames, endquery=self._checkError )
        else:
            rec =  DbHelper.fetchrow( DbNote.SQL_GET_ONE , [book,page,seq] , DbNote.columnNames, endquery=self._checkError )
        if rec is None and new and isinstance( book , int ):
            rec = self.new( '', book, page, seq )
        return rec
        
    def getAll(self, book_id:int, page:int):
        """ Get All notes for a page in order of sequence """
        return  DbHelper.fetchrows( DbNote.SQL_GET_ALL , [book_id,page] , DbNote.columnNames, endquery=self._checkError )
    
    def getNoteForBook( self, book )->str:
        """ Get the Book's main note (general, not for a page ) """
        return self.getNote( book ,0,0 )

    def deletePage( self, book, page:int=0, seq:int=0)->bool:
        query = DbHelper.prep( DbNote.SQL_DELETE )
        query = DbHelper.bind( query , [ book, page, seq] )
        query.exec()
        self._checkError( query )
        return self.getReturnCode( query )

    def deleteNote( self, note:dict)->bool:
        if isinstance( note , dict ):
            return self.deletePage( note[NOTE.book_id], note[NOTE.page], note[NOTE.seq])
        raise ValueError( "deleteNote requires a dictionary")

    def deleteAllPageNotes( self, book, page:int ):
        query = DbHelper.prep( DbNote.SQL_DELETE_PAGE_NOTES )
        query = DbHelper.bind( query , [ book, page] )
        query.exec()
        self._checkError( query )
        return self.getReturnCode( query )

    def count( self, book:int, page:int )->int:
        return  int( DbHelper.fetchone( DbNote.SQL_COUNT_PAGE_NOTES ,  [book,page]) )

    def add( self, note:dict ):
        """ Add a note to a book. page and sequence default to zero 
            If the record ID is greater than zero, we do an update 
            To add for a non-zero page, call addPage
        """
        if NOTE.id in note :
            return self.update( note )
        if not NOTE.book_id in note or note[NOTE.book_id] is None or note[NOTE.book_id] < 1:
            raise ValueError( "Note must have book id")
        sql = self._formatInsertVariable( 'Note',note )
        query = DbHelper.prep( sql )
        DbHelper.bind( query, list( note.values() ))
        id = ( query.lastInsertId() if query.exec() else -1 )
        self._checkError( query )
        query.finish()
        return id
    
    def addPage( self, note:dict ):
        """ Note: this will increment the sequence number for you """
        if not NOTE.page in note or note[NOTE.page] is None: 
            raise ValueError( "Note must have page number")

        note[ NOTE.seq] = self.count( note[ NOTE.book_id ] , note[ NOTE.page ]) 
        return self.add( note )

     
    def update( self, note:dict ):
        """ update will take a list of key/value pairs and update all the fields for this record """
        note_id = note.pop( NOTE.id )
        if note_id is None:
            raise ValueError( "Note must have record ID. Did you mean to add?")
        sql = self._formatUpdateVariable( 'Note', NOTE.id, note)
        query = DbHelper.prep( sql )
        values = list( note.values() ) 
        values.append( note_id )
        query = DbHelper.bind( query, values )
        if query.exec() :
            return id
        return -1

    def new(self, note:str, book_id:int , page:int=0, seq:int=0, loc=None,size=None)->dict:
        newNote = {
            NOTE.note:      note.strip(),
            NOTE.book_id:   book_id,
            NOTE.page:      page,
            NOTE.seq:       seq,
            NOTE.location:  None,
            NOTE.size:      None,
        }
        if size is not None:
            newNote[ NOTE.size ]     = self.encode( size )
        if loc is not None:
            newNote[ NOTE.location ] = self.encode(loc )
        return newNote

    def notePageList(self,book_id)->dict:
        page_count_dict = {}
        rows = DbHelper.fetchrows( DbNote.SQL_COUNT_PAGES ,[book_id] , [NOTE.page, 'count'])
        for row in rows:
            page_count_dict[ row[ NOTE.page]] = row[ 'count' ]
        return page_count_dict


    def decode( self , encoded_value:str):
        return None if encoded_value == '' or encoded_value is None else DbHelper.decode( encoded_value )
    
    def encode( self, value )->str:
        if value is None or ( isinstance( value , str ) and len(value) == 0 ):
            return None
        return DbHelper.encode( value )

