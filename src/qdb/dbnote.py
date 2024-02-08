"""
Database : Note table interface

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""


from qdb.base   import DbBase
from qdb.dbconn import DbConn
from qdb.fields.note import NoteField
from qdb.util   import DbHelper

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
    SQL_GET_PAGE_NOTES     = """SELECT *
                                From Note
                                WHERE book_id= ?
                                AND   page=?
                                ORDER BY sequence
                            """
    SQL_GET_ALL_NOTES      = """SELECT *
                               FROM Note
                               WHERE book_id = ?
                               ORDER BY page, sequence
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
    column_names = None
    column_names    = None

    SQL_IS_EXPANDED=False

    def __init__(self):
        super().__init__()
        if DbNote.column_names is None or len( DbNote.column_names) == 0 :
            DbNote.column_names = DbConn.get_column_names( 'Note')
        self.setup_logger()

    def _check_note( self, note:dict )->dict:
        """Check three key fields in note: book_id, page, seq
        If book_id is empty, throw error
        if page is empty, set to zero
        if seq is empty, set to zero

        Args:
            note (dict): Note dictionary

        Returns:
            dict: Checked, and repaired, note
        """
        if not NoteField.BOOK_ID in note or \
            note[NoteField.BOOK_ID] is None or \
                note[NoteField.BOOK_ID] < 1:
            raise ValueError( "Note must have book id")

        if not NoteField.PAGE in note or \
            note[NoteField.PAGE ] is None:
            note[NoteField.PAGE] = 0
        if not NoteField.SEQ in note or \
            note[NoteField.SEQ ] is None:
            note[NoteField.SEQ ] = 0

        return note

    def get_note( self, book:str|int, page:int=0, seq:int=0 ,new=True)->dict:
        """Get a note for a page
        This will fetch a note and a sequence
        Optionally, return a new, blank note

        Args:
            book (str|int): Book ID or name
            page (int, optional): Book's page number
                Defaults to 0.
            seq (int, optional): Note page number.
                Defaults to 0 (first)
            new (bool, optional): If true, create a new note.
                Defaults to True.

        Returns:
            dict: Note's data in dictionary form
        """

        if isinstance( book, str ):
            rec =  DbHelper.fetchrow(
                        DbNote.SQL_GET_ONE_BY_NAME ,
                        [book,page,seq] ,
                        DbNote.column_names,
                        endquery=self._check_error )
        else:
            rec =  DbHelper.fetchrow(
                        DbNote.SQL_GET_ONE ,
                        [book,page,seq] ,
                        DbNote.column_names,
                        endquery=self._check_error )

        if rec is None and new and isinstance( book , int ):
            return NoteField.new( {
                NoteField.BOOK_ID: book ,
                NoteField.PAGE: page,
                NoteField.SEQ: seq
            })
        return rec

    def get_notes_for_page(self, book_id:int, page:int)->list:
        """Get all notes for a page

        Args:
            book_id (int): DB Book's ID
            page (int): Book's page number

        Returns:
            list: list of notes [ {}, .... {} ]
        """
        return  DbHelper.fetchrows(
                        DbNote.SQL_GET_PAGE_NOTES ,
                        [book_id,page] ,
                        DbNote.column_names,
                        endquery=self._check_error )

    def get_note_for_book( self, book:str|int )->dict:
        """Get the first note for a book (page zero)

        Args:
            book (str | int): Book ID or name

        Returns:
            dict: Note's data in dictionary form
        """
        return self.get_note( book ,0,0 )

    def get_all( self, book_id:int )->list:
        """Get all notes for a book, including page zero

        Args:
            book_id (int): DB Book ID

        Returns:
            list: List of dictionary of notes
        """
        return  DbHelper.fetchrows(
                        DbNote.SQL_GET_ALL_NOTES ,
                        [book_id] ,
                        DbNote.column_names,
                        endquery=self._check_error )

    def delete_page( self, book:int, page:int=0, seq:int=0)->bool:
        """Delete a single note page

        Args:
            book (int): DB Book ID
            page (int, optional): Book's page number
                Defaults to 0. (Note for book)
            seq (int, optional): Note Sequence for page.
                Defaults to 0 (first note)

        Returns:
            bool: True if deleted
        """
        query = DbHelper.prep( DbNote.SQL_DELETE )
        query = DbHelper.bind( query , [ book, page, seq] )
        query.exec()
        self._check_error( query )
        return self.get_rtn_code( query )

    def delete_note( self, note:dict)->bool:
        """Delete a note, given a note's dictionary

        Args:
            note (dict): Note dictionary
                Must contain Book_id, page and seq

        Raises:
            ValueError: If note is not a dictionary

        Returns:
            bool: True if page deleted
        """
        if isinstance( note , dict ):
            return self.delete_page( \
                note[NoteField.BOOK_ID], \
                note[NoteField.PAGE], \
                note[NoteField.SEQ])
        raise ValueError( "deleteNote requires a dictionary")

    def delete_all_page_notes( self, book:int, page:int ):
        """Delete all notes for a single page

        Args:
            book (int): DB Book ID
            page (int): Book's page number

        Returns:
            _type_: True if deleted
        """
        query = DbHelper.prep( DbNote.SQL_DELETE_PAGE_NOTES )
        query = DbHelper.bind( query , [ book, page] )
        query.exec()
        self._check_error( query )
        return self.get_rtn_code( query )

    def count( self, book:int, page:int )->int:
        """Count number of notes for a page

        Args:
            book (int): DB Book ID
            page (int): Page number

        Returns:
            int: Number of notes
        """
        return  int( DbHelper.fetchone( DbNote.SQL_COUNT_PAGE_NOTES ,  param=[book,page]) )

    def add( self, note:dict )->int:
        """Add a note to a book. page and sequence default to zero
            If the record ID is greater than zero, we do an update
            To add for a non-zero page, call addPage

        Args:
            note (dict): Dictionary for note

        Raises:
            ValueError: No book id

        Returns:
            int: Record number of note
        """
        if not isinstance( note, dict ) or not note :
            raise ValueError( "Note passed is not dictionary")
        if NoteField.ID in note and note[NoteField.ID] is not None :
            return self.update( note )

        note = self._check_note( note )
        sql = self._format_insert_variable(
                        table_name='Note',
                        field_value_dict=note )
        query = DbHelper.prep( sql )
        DbHelper.bind( query, list( note.values() ))
        note_id = ( query.lastInsertId() if query.exec() else -1 )
        self._check_error( query )
        query.finish()
        return note_id

    def add_page( self, note:dict )->int:
        """this will increment the sequence number for you

        Args:
            note (dict): Dictonary of note contents

        Raises:
            ValueError: No page number, No record ID

        Returns:
            int: Record number of new note
        """
        if not isinstance( note, dict ):
            raise ValueError( "Note passed must be a dictionary")
        if not NoteField.PAGE in note or note[NoteField.PAGE] is None:
            raise ValueError( "Note must have page number")

        note[ NoteField.SEQ] = self.count( note[ NoteField.BOOK_ID ] , note[ NoteField.PAGE ])
        return self.add( note )

    def update( self, note:dict )->int:
        """update will take a list of key/value pairs
        update all the fields for this record

        Args:
            note (dict): Note ID

        Raises:
            ValueError: No record number

        Returns:
            int: int of record or -1 if nothing found
        """
        note_id = note.pop( NoteField.ID )
        if note_id is None:
            raise ValueError( "Note must have record ID. Did you mean to add?")
        sql = self._format_update_variable( 'Note', NoteField.ID, note)
        query = DbHelper.prep( sql )
        values = list( note.values() )
        values.append( note_id )
        query = DbHelper.bind( query, values )
        if query.exec() :
            return id
        return -1

    def note_page_list(self,book_id:int)->dict:
        """Retrieve a dictionary of all pages and note count

        Args:
            book_id (int): DB id for book

        Returns:
            dict: [ page# : note-count]
        """
        page_count_dict = {}
        rows = DbHelper.fetchrows( DbNote.SQL_COUNT_PAGES ,[book_id] , [NoteField.PAGE, 'count'])
        for row in rows:
            page_count_dict[ row[ NoteField.PAGE]] = row[ 'count' ]
        return page_count_dict
