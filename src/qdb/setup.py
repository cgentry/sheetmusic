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

import logging
import os.path
import os
from decimal import *

from qdb.dbconn import DbConn
from qdb.keys   import DbKeys, ProgramConstants
from qdb.util   import DbHelper
from PySide6.QtSql  import QSqlQuery
from util.convert   import toBool

class Setup():

    def __init__(self, location:str=None):
        self.query = QSqlQuery( DbConn.db() )
        self.logger = logging.getLogger( 'sheetmusic.Setup')

    def __del__(self):
        del self.query

    def createTables(self):
        tables = [
            "System     ( key  TEXT PRIMARY KEY, value TEXT )",
            """Book     ( 
                          id            INTEGER PRIMARY KEY ASC,
                          book          TEXT NOT NULL UNIQUE, 
                          composer_id   INTEGER DEFAULT NULL, 
                          genre_id      INTEGER DEFAULT NULL,
                          author        TEXT DEFAULT NULL,
                          publisher     TEXT DEFAULT NULL,
                          source        TEXT DEFAULT NULL, 
                          source_type   TEXT NOT NULL CHECK( source_type in ('png','pdf')) DEFAULT 'png',
                          location      TEXT NOT NULL,
                          version       TEXT DEFAULT "0.6",
                          layout        TEXT DEFAULT 'single',
                          link          TEXT,
                          aspectRatio      BOOLEAN NOT NULL CHECK (aspectRatio in (0,1)) DEFAULT 1,
                          total_pages      INTEGER DEFAULT 0, 
                          last_read        INTEGER DEFAULT 1, 
                          numbering_starts INTEGER DEFAULT 1, 
                          numbering_ends   INTEGER DEFAULT 1,
                          name_default     INTEGER DEFAULT O,
                          date_added       DATETIME DEFAULT current_timestamp,
                          date_updated     DATETIME DEFAULT NULL,
                          date_read        DATETIME DEFAULT NULL,
                          date_file_created DATETIME DEFAULT NULL, 
                          date_file_modified  DATETIME DEFAULT NULL, 
                          date_pdf_created DATETIME DEFAULT NULL, 
                          date_pdf_modified DATETIME DEFAULT NULL
                        )""",
            """Bookmark  ( id           INTEGER PRIMARY KEY ASC,
                           book_id      INTEGER NOT NULL,
                           bookmark     TEXT NOT NULL, 
                           page         INT NOT NULL,
                           CONSTRAINT fk_book
                                FOREIGN KEY (book_id)
                                REFERENCES Book(book_id)
                                ON DELETE CASCADE
                        )""",
            """BookSetting ( id      INTEGER PRIMARY KEY ASC,
                             book_id INTEGER NOT NULL,
                             key     TEXT NOT NULL, 
                             value   TEXT NOT NULL,
                             date_added       DATETIME DEFAULT current_timestamp,
                             date_updated     DATETIME DEFAULT NULL,
                             UNIQUE   (book_id, key ),
                             CONSTRAINT fk_booksetting
                                FOREIGN KEY (book_id)
                                REFERENCES Book(book_id)
                                ON DELETE CASCADE)""",

            """Composer  ( id   INTEGER PRIMARY KEY ASC,
                           name TEXT    NOT NULL UNIQUE )""",
            """Genre     ( id   INTEGER PRIMARY KEY ASC,
                           name TEXT    UNIQUE NOT NULL)
            """,
            """Note     ( id        INTEGER PRIMARY KEY ASC,
                          note      TEXT    DEFAULT '',
                          location  BLOB    DEFAULT NULL,
                          size      BLOB    DEFAULT NULL,
                          book_id   INTEGER NOT NULL,
                          page      INTEGER NOT NULL DEFAULT 0,
                          sequence  INTEGER NOT NULL DEFAULT 0,
                          CONSTRAINT fk_notes
                                FOREIGN KEY (book_id)
                                REFERENCES Book(book_id)
                                ON DELETE CASCADE)
            """
            ]
        ### Non unique indexes    
        idx = [
            "Book_Composer ON Book     (composer_id)",
            "Book_Genre    ON Book     (genre_id)",
            "Bookmark_Book ON Bookmark (book_id)",
            "Book_Notes    ON Notes    (book_id, page,sequence)",
        ]
        unique_idx = [
            "Bookmark_PAGE    ON Bookmark    (book_id, page)",
            "Bookmark_MARK    ON Bookmark    (book_id, bookmark)",
            "BookSetting_BOOK ON BookSetting (book_id, key)",
            "NoteSequence     ON Note        (book_id, page, sequence)",
        ]
        views = [
            """BookView AS 
               SELECT 
                    Book.*,
                    datetime( Book.date_added ,  'localtime') AS local_added,
                    datetime( Book.date_updated, 'localtime') AS local_updated,
                    datetime( Book.date_read,    'localtime') AS local_read,
                    Composer.id    AS composer_id, 
                    Composer.name  AS composer, 
                    Genre.id       AS genre_id,
                    Genre.name     AS genre
               FROM Book
               LEFT JOIN Composer ON Book.composer_id = Composer.id
               LEFT JOIN Genre    ON Book.genre_id = Genre.id
               LEFT JOIN Note     ON Note.book_id = Book.id AND Note.page = 0 AND Note.sequence = 0
            """,
            """BookmarkView AS
                SELECT
                    Book.book         AS book, 
                    Bookmark.* 
                    FROM Bookmark
                    LEFT JOIN Book ON Book.id = Bookmark.book_id
                """,
            """BookSettingView AS
                    SELECT
                        Book.book       AS book, 
                        BookSetting.*,
                        datetime( BookSetting.date_added ,  'localtime') AS local_added,
                        datetime( BookSetting.date_updated, 'localtime') AS local_updated
                    FROM BookSetting
                    LEFT JOIN Book ON Book.id = BookSetting.book_id
                """
        ]
        booktrigger = """
            CREATE TRIGGER IF NOT EXISTS BookTrigger
            AFTER UPDATE ON Book
            BEGIN
                UPDATE Book SET date_updated = datetime('now') WHERE id = old.id;
            END;
        """

        settingtrigger = """
            CREATE TRIGGER IF NOT EXISTS SettingTrigger
            AFTER UPDATE ON BookSetting
            BEGIN
                UPDATE BookSetting SET date_updated = datetime('now') WHERE id = old.id;
            END;
        """

        for tableCreate in tables:
            self.query.exec( "CREATE TABLE IF NOT EXISTS {};".format( tableCreate) )
        
        for indexCreate in idx:
            self.query.exec( "CREATE INDEX IF NOT EXISTS {};".format(indexCreate ) )
        for indexCreate in unique_idx:
            self.query.exec( "CREATE UNIQUE INDEX IF NOT EXISTS {};".format(indexCreate ) )

        try:
            for viewCreate in views:
                self.query.exec( "CREATE VIEW IF NOT EXISTS {};".format(viewCreate))
        except Exception as err:
            self.logger.exception("Invalid view: '{}".format( viewCreate ) )
            raise err

        self.query.exec( booktrigger )
        self.query.exec( settingtrigger )
        DbConn.commit()

    def dropTables(self):
        """
        WARNING:
            You really don't want to do this casually. It will wipe out ALL the data
        """
        tables = [
            "Book","Genre","Composer","Bookmark","System","Booksetting","Note"
        ]
        views = ["BookView","BookmarkView","BookSettingView"]

        for table in tables:
            self.query.exec("DROP TABLE IF EXISTS {};".format( table ))
        for view in views:
            self.query.exec("DROP VIEW IF EXISTS {};".format( view ))
        DbConn.commit()

    def _update_null(self, current:Decimal )->Decimal:
        """ Used to increment by .1 when nothing is to be done"""
        current += Decimal(0.1)
        self.logger.info("Update database to {}: No action needed.".format( current))
        return Decimal(current)
    
    def _update_0_5(self, current:Decimal)->Decimal:
        """ Update from 0.5 to 0.6
            Insert new value for source_type
        """
        sql = "ALTER TABLE Book ADD source_type TEXT NOT NULL CHECK( source_type in ('png','pdf')) DEFAULT 'png'"
        if not DbHelper.prep( sql ).exec() :
            raise RuntimeError('Version 0.6: Could not update Book table for source_type')
        self.logger.info("Update database to 0.6 from 0.5: Book.status_type added.")
        return Decimal('0.6')

    def system_update(self)->bool:
        """ Check to see if we need to update the system. This could be when verions IDs change"""
        getcontext().prec = 1
        update_functions = {
            '0.1' : self._update_null,
            '0.2' : self._update_null,
            '0.3' : self._update_null,
            '0.4' : self._update_null,
            '0.5' : self._update_0_5,
        }

        sql_version= "SELECT value FROM System WHERE key='{}'".format( DbKeys.SETTING_VERSION )
        sql_update = "UPDATE System SET value=? WHERE key='{}'".format( DbKeys.SETTING_VERSION)

        db_version  = Decimal( DbHelper.fetchone( sql_version , default="0.0" ) )
        if db_version == Decimal(0.0):
            raise ValueError('value wrong! '+sql_version )
        
        pgm_version = Decimal( ProgramConstants.version_main )
        if db_version < pgm_version:
            str_db_version = str( db_version )
            self.logger.info("DB version {}, Software version {}".format( db_version , pgm_version ))
            while str_db_version in update_functions:
                db_version = update_functions[ str_db_version ]( db_version )
                str_db_version = str( Decimal(db_version ) )
                self.query.prepare( sql_update )
                self.query.addBindValue( str_db_version )
                if not self.query.exec():
                    raise RuntimeError('Couldnt update System version number')
            return True
        return False
        
    def initSystem(self)->bool:
        user_script_dir = os.path.expanduser(DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR)
        user_script_inc = os.path.join( user_script_dir , 'include')
        shell = os.environ[ 'SHELL']
        if not shell:
            shell = DbKeys.VALUE_SCRIPT_CMD
        data = {
            DbKeys.SETTING_KEEP_ASPECT:         DbKeys.VALUE_KEEP_ASPECT,
            DbKeys.SETTING_DEFAULT_PATH_MUSIC:  os.path.expanduser(DbKeys.VALUE_DEFAULT_DIR),
            DbKeys.SETTING_PATH_USER_SCRIPT:    os.path.expanduser(DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR),
            DbKeys.SETTING_DEFAULT_IMGFORMAT:   DbKeys.VALUE_GSDEVICE,
            DbKeys.SETTING_PAGE_LAYOUT:         DbKeys.VALUE_PAGES_SINGLE,
            DbKeys.SETTING_LAST_BOOK_REOPEN:    DbKeys.VALUE_REOPEN_LAST,
            DbKeys.SETTING_FILE_TYPE:           DbKeys.VALUE_FILE_TYPE,
            DbKeys.SETTING_DEFAULT_SCRIPT:      shell,
            DbKeys.SETTING_DEFAULT_SCRIPT_VAR:  DbKeys.VALUE_SCRIPT_VAR,
            DbKeys.SETTING_BOOK_DEFAULT_GENRE:  DbKeys.VALUE_DEFAULT_GENRE,
            DbKeys.SETTING_FILE_PREFIX:         DbKeys.VALUE_FILE_PREFIX,
            DbKeys.SETTING_FILE_RES:            DbKeys.VALUE_FILE_RES,
            DbKeys.SETTING_LAST_IMPORT_DIR:     DbKeys.VALUE_LAST_IMPORT_DIR,
            DbKeys.SETTING_NAME_IMPORT:         DbKeys.VALUE_NAME_IMPORT_FILE_1,
            DbKeys.SETTING_LOGGING_ENABLED:     False,
            DbKeys.SETTING_VERSION:             ProgramConstants.version_main,
        }
 
        sql = '''INSERT OR IGNORE INTO System( key, value ) VALUES(?,?)'''
        
        added = 0
        for key, value in data.items() :
            self.query.prepare( sql )
            self.query.addBindValue( key )
            self.query.addBindValue( value )
            if not self.query.exec():
                print("ERROR: system insert", self.query.lastError().text(), "\nValues:", self.query.boundValues() )
            added += self.query.numRowsAffected()
            self.query.finish()

        #self.insertPdfScript( )
        DbConn.commit()
        ## Make sure user script dirs are created.
        ## 750 = Owner: Read/Write/Exe , Group: Read/Exe, Other: No access
        os.makedirs( user_script_inc, mode=0o750, exist_ok=True )
        return (added > 0 )

    def initGenre(self)->bool:
        """
            Initialise Genre UNLESS there are records there. If none,
            fill up with some initial data
        """ 
        self.query.exec("SELECT COUNT(*) as count FROM Genre")
        self.query.exec()
        self.query.next()
        rowCount = self.query.value(0)
        self.query.finish()
        if rowCount == 0:
            self.query.prepare("INSERT OR IGNORE INTO Genre ( name ) VALUES ( ?)")
            for g in [ 
                "Unknown", "Various", "Teaching", "Alternative",
                "Blues", "Christmas", "Choral", "Classical", "Country" ,
                "Folk",  "Gospel", "Holiday", "Indie Rock", "Jazz", 
                "Latin", "Metal", "Movie", "Musical", "New Age", "Opera", 
                "Pop", "R&B", "Religious", "Reggae", "Rock" , "Soul", 
                "Traditional", "Theatre", "Vocal", "World"]:
                
                self.query.addBindValue( g )
                self.query.exec()
            DbConn.commit()
        return rowCount == 0

    def initComposer(self)->bool:
        """
            Initialise Composers UNLESS there are records there. If none,
            fill up with some initial data
        """
        self.query.exec("SELECT COUNT(*) as count FROM Composer")
        self.query.exec()
        self.query.next()
        rowCount = self.query.value(0)
        self.query.finish()

        if rowCount == 0:
            self.query.prepare("INSERT OR IGNORE INTO Composer ( name ) VALUES ( ?)")
            for g in ["Unknown", "Various", "Teaching", 'Anonymous',
                'Bach, C.P.E.', 'Bach, J.C.', 'Bach, J.S.', 
                'Beethoven', 'Brahms',
                'Chopin', 'Debussy', 'Duruflé, Maurice', 'Dvořák', 
                'Elgar', 'Giovanni, Gabrieli', 'Glass, Philip', 'Grieg, Edvard',
                'Handel', 'Haydn', 'Liszt', 'Mahler', 'Mendelssohn', 
                'Messiaen, Olivier', 'Mixed', 'Pachelbel', 'Purcell', 'Rachmaninov', 'Saint-Saëns', 
                'Schubert', 'Satie, Erik', 'Shostakovich', 'Shumann', 'Strauss, Richard', 
                'Stravinsky', 'Tchaikovsky', 'Verdi', 'Vivaldi', "Wagner"
                'Walton, William', 'Widor, Charles Marie', 'Williams, Vaughan',
                "Verdi","Vivaldi"]:
                self.query.addBindValue( g )
                self.query.exec()
            DbConn.commit()
        return rowCount == 0

    def initData(self):
        """
            initData will pre-load the database with the default settings. It doesn't
            override values that have been set so is safe to call anytime.
        """
        self.createTables()
        self.initSystem()
        self.initComposer()
        self.initGenre()
        DbConn.commit()

    def logging(self, directory_location )->bool:
        try:
            sql = "SELECT value FROM System WHERE key='{}'".format( DbKeys.SETTING_LOGGING_ENABLED )
            should_show_logging = toBool( DbHelper.fetchone( sql , default = 0 ) )
        except Exception as err:
            logging.exception("DB error getting key '{}': {}".format( DbKeys.SETTING_LOGGING_ENABLED, str(err)) )
            should_show_logging = False 

        fileoutput = os.path.join( directory_location , 'sheetmusic.log')
        level      = logging.INFO if should_show_logging else logging.ERROR 
        logging.basicConfig( 
            filename=fileoutput, 
            filemode='w', 
            format='%(asctime)s %(levelname)-8s : %(name)-12s %(message)s' , 
            datefmt='%m-%d %H:%M', 
            level=level)
        
        return should_show_logging

# if __name__ == "__main__":
#     s = Setup(":memory:")
#     s.createTables()
#     s.initData()
#     (conn, cursor) = DbConn().openDB()

#     SqlInsert( 'Book', book='test1', composer_id=1, genre_id=1, location='/loc', source='/source')
#     SqlUpsert( 'Bookmark', book_id=1, bookmark='Bach' ,page=10)
#     SqlUpsert( 'Bookmark', book_id=1, bookmark='Bach2', page=20 )

#     sql = """SELECT 
#             Book.book as book, Bookmark.*
#             FROM Bookmark
#             LEFT JOIN Book ON Book.id = Bookmark.book_id
#             WHERE book=:book and page <=:page
#             ORDER BY page DESC LIMIT 1
#         """
#     result = self.query.execute(sql , {'book':'test1', 'page':30})
   
#     = DbConn().openDB(close=True)