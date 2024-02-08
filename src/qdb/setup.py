"""
Database Module for setup

Part of the SheetMusic system
(c) Copyright 2022-2023 Charles Gentry

You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import os.path
import os
from decimal import Decimal, getcontext

from PySide6.QtSql import QSqlQuery
from constants import ProgramConstants
from qdb.dbconn import DbConn
from qdb.keys import DbKeys
from qdb.util import DbHelper
from util.convert import to_bool

class Setup():
    """ Class is used to setup the database.

        create_tables: initialise all tables
        drop_tables: dump all the tables in the db
        init_composer: setup composer table
        init_data: fill in initial data
        init_genre: setup genre table
        init_system: start the system
        logging: setup logging
        system_update: Check for incremental update
        update_n_n: Incremental update to database
        update_null: update when nothing happening
    """
    def __init__(self, location: str = None):
        del location
        self.query = QSqlQuery(DbConn.db())
        self.logger = logging.getLogger('sheetmusic.Setup')

    def __del__(self):
        del self.query

    def create_tables(self):
        """ Create tables in database.
            Only use during initialisation
        """
        tables = [
            """Log        (
                            id            INTEGER PRIMARY KEY ASC,
                            level         INTEGER NOT NULL,
                            class         TEXT default '',
                            method        TEXT default '',
                            msg           TEXT NOT NULL,
                            date_added    DATETIME DEFAULT current_timestamp )""",
            "System     ( key  TEXT PRIMARY KEY, value TEXT )",
            """Book     (
                          id            INTEGER PRIMARY KEY ASC,
                          book          TEXT NOT NULL UNIQUE,
                          composer_id   INTEGER DEFAULT NULL,
                          genre_id      INTEGER DEFAULT NULL,
                          author        TEXT DEFAULT NULL,
                          publisher     TEXT DEFAULT NULL,
                          source        TEXT DEFAULT NULL,
                          source_type   TEXT NOT NULL
                                CHECK( source_type in ('png','pdf')) DEFAULT 'png',
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
            """Note      ( id   INTEGER PRIMARY KEY ASC,
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
        # Non unique indexes
        idx = [
            "Book_Composer ON Book     (composer_id)",
            "Book_Genre    ON Book     (genre_id)",
            "Bookmark_Book ON Bookmark (book_id)",
            "Book_Notes    ON Notes    (book_id, page,sequence)",
            "Log_Level     ON Log      (level, date_added)",
            "Log_Date      ON Log      (date_added, level)"
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

        for table_create in tables:
            self.query.exec(
                f"CREATE TABLE IF NOT EXISTS {table_create};" )

        for index_create in idx:
            self.query.exec(f"CREATE INDEX IF NOT EXISTS {index_create};")
        for index_create in unique_idx:
            self.query.exec(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {index_create};")

        try:
            for view_create in views:
                self.query.exec(f"CREATE VIEW IF NOT EXISTS {view_create};")
        except Exception as err:
            self.logger.critical("Invalid view: '%s' %s", view_create , str(err))
            raise err

        self.query.exec(booktrigger)
        self.query.exec(settingtrigger)
        DbConn.commit()

    def drop_tables(self):
        """
        WARNING:
            You really don't want to do this casually. It will wipe out ALL the data
        """
        tables = [
            "Book", "Bookmark", "Booksetting", "Composer", "Genre", "Log", "Note", "System"
        ]
        views = ["BookView", "BookmarkView", "BookSettingView"]

        for table in tables:
            self.query.exec(f"DROP TABLE IF EXISTS {table};")
        for view in views:
            self.query.exec(f"DROP VIEW IF EXISTS {view};")
        DbConn.commit()

    def _update_null(self, current: Decimal) -> Decimal:
        """ Used to increment by .1 when nothing is to be done"""
        current += Decimal(0.1)
        self.logger.info(
            "Update database to %s: No action_ needed.", current)
        return Decimal(current)

    def _update_0_5(self, current: Decimal) -> Decimal:
        """ Update from 0.5 to 0.6
            Insert new value for source_type
        """
        del current
        sql = """ALTER TABLE Book
                ADD source_type TEXT NOT NULL
                CHECK( source_type in ('png','pdf'))
                DEFAULT 'png'"""
        if not DbHelper.prep(sql).exec():
            raise RuntimeError(
                'Version 0.6: Could not update Book table for source_type')
        self.logger.info(
            "Update database to 0.6 from 0.5: Book.status_type added.")
        return Decimal('0.6')

    def _update_0_6(self, current: Decimal) -> Decimal:
        """ Update from 0.5 to 0.6
            Insert New Table
        """
        del current
        self.create_tables()
        self.logger.info("Update database to 0.6 from 0.5: Log file added.")
        return Decimal('0.6')

    def system_update(self) -> bool:
        """ Check to see if we need to update the system. This could be when verions IDs change"""
        getcontext().prec = 1
        update_functions = {
            '0.1': self._update_null,
            '0.2': self._update_null,
            '0.3': self._update_null,
            '0.4': self._update_null,
            '0.5': self._update_0_5,
            '0.6': self._update_0_6,
        }
        self._update_0_6(0.6)
        sql_version = f"SELECT value FROM System WHERE key='{DbKeys.SETTING_VERSION}'"
        sql_update = f"UPDATE System SET value=? WHERE key='{DbKeys.SETTING_VERSION}'"

        db_version = Decimal(DbHelper.fetchone(sql_version, default="0.0"))
        if db_version == Decimal(0.0):
            raise ValueError('value wrong! '+sql_version)

        pgm_version = Decimal(ProgramConstants.VERSION_MAIN)
        if db_version < pgm_version:
            str_db_version = str(db_version)
            self.logger.info("DB version %s, Software version %s",
                db_version, pgm_version)
            while str_db_version in update_functions:
                db_version = update_functions[str_db_version](db_version)
                str_db_version = str(Decimal(db_version))
                self.query.prepare(sql_update)
                self.query.addBindValue(str_db_version)
                if not self.query.exec():
                    raise RuntimeError('Couldnt update System version number')
            return True
        return False

    def init_system(self) -> bool:
        """ Initialise the database and all tables """
        user_script_dir = os.path.expanduser(
            DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR)
        user_script_inc = os.path.join(user_script_dir, 'include')
        shell = os.environ['SHELL']
        if not shell:
            shell = DbKeys.VALUE_SCRIPT_CMD
        data = {
            DbKeys.SETTING_KEEP_ASPECT:         DbKeys.VALUE_KEEP_ASPECT,
            DbKeys.SETTING_DEFAULT_PATH_MUSIC:
                os.path.expanduser(DbKeys.VALUE_DEFAULT_DIR),
            DbKeys.SETTING_PATH_USER_SCRIPT:
                os.path.expanduser(DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR),
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
            DbKeys.SETTING_VERSION:             ProgramConstants.VERSION_MAIN,
        }

        sql = '''INSERT OR IGNORE INTO System( key, value ) VALUES(?,?)'''

        added = 0
        for key, value in data.items():
            self.query.prepare(sql)
            self.query.addBindValue(key)
            self.query.addBindValue(value)
            if not self.query.exec():
                print("ERROR: system insert", self.query.lastError()(
                ).text(), "\nValues:", self.query.boundValues())
            added += self.query.numRowsAffected()
            self.query.finish()

        # self.insertPdfScript( )
        DbConn.commit()
        # Make sure user script dirs are created.
        # 750 = Owner: Read/Write/Exe , Group: Read/Exe, Other: No access
        os.makedirs(user_script_inc, mode=0o750, exist_ok=True)
        return added > 0

    def init_genre(self) -> bool:
        """
            Initialise Genre UNLESS there are records there. If none,
            fill up with some initial data
        """
        self.query.exec("SELECT COUNT(*) as count FROM Genre")
        self.query.exec()
        self.query.next()
        row_count = self.query.value(0)
        self.query.finish()
        if row_count == 0:
            self.query.prepare(
                "INSERT OR IGNORE INTO Genre ( name ) VALUES ( ?)")
            for g in [
                "Unknown", "Various", "Teaching", "Alternative",
                "Blues", "Christmas", "Choral", "Classical", "Country",
                "Folk",  "Gospel", "Holiday", "Indie Rock", "Jazz",
                "Latin", "Metal", "Movie", "Musical", "New Age", "Opera",
                "Pop", "R&B", "Religious", "Reggae", "Rock", "Soul",
                    "Traditional", "Theatre", "Vocal", "World"]:

                self.query.addBindValue(g)
                self.query.exec()
            DbConn.commit()
        return row_count == 0

    def init_composer(self) -> bool:
        """
            Initialise Composers UNLESS there are records there. If none,
            fill up with some initial data
        """
        self.query.exec("SELECT COUNT(*) as count FROM Composer")
        self.query.exec()
        self.query.next()
        row_count = self.query.value(0)
        self.query.finish()

        if row_count == 0:
            self.query.prepare(
                "INSERT OR IGNORE INTO Composer ( name ) VALUES ( ?)")
            for g in ["Unknown", "Various", "Teaching", 'Anonymous',
                      'Bach, C.P.E.', 'Bach, J.C.', 'Bach, J.S.',
                      'Beethoven', 'Brahms', 'Chopin',
                      'Debussy', 'Duruflé, Maurice',
                      'Dvořák', 'Elgar', 'Giovanni, Gabrieli',
                      'Glass, Philip', 'Grieg, Edvard','Handel',
                      'Haydn', 'Liszt', 'Mahler',
                      'Mendelssohn','Messiaen, Olivier',
                      'Mixed', 'Pachelbel', 'Purcell',
                      'Rachmaninov', 'Saint-Saëns','Schubert',
                      'Satie, Erik', 'Shostakovich', 'Shumann',
                      'Strauss, Richard','Stravinsky',
                      'Tchaikovsky', 'Verdi', 'Vivaldi',
                      "Wagner", 'Walton, William',
                      'Widor, Charles Marie', 'Williams, Vaughan',
                      "Verdi", "Vivaldi"]:
                self.query.addBindValue(g)
                self.query.exec()
            DbConn.commit()
        return row_count == 0

    def init_data(self):
        """
            initData will pre-load the database with the default settings. It doesn't
            override values that have been set so is safe to call anytime.
        """
        self.create_tables()
        self.init_system()
        self.init_composer()
        self.init_genre()
        DbConn.commit()

    def logging(self, directory_location) -> bool:
        """ Setup logging"""

        sql = f"SELECT value FROM System WHERE key='{DbKeys.SETTING_LOGGING_ENABLED}'"
        should_show_logging = to_bool(DbHelper.fetchone(sql, default=0))
        # except Exception as err:
        #     logging.exception(
        #         "DB error getting key %s: '%s'",DbKeys.SETTING_LOGGING_ENABLED, str(err))
        #     should_show_logging = False

        fileoutput = os.path.join(directory_location, 'sheetmusic.log')
        level = logging.INFO if should_show_logging else logging.ERROR
        logging.basicConfig(
            filename=fileoutput,
            filemode='w',
            format='%(asctime)s %(levelname)-8s : %(name)-12s %(message)s',
            datefmt='%m-%d %H:%M',
            level=level)

        return should_show_logging

# if __name__ == "__main__":
#     s = Setup(":memory:")
#     s.create_tables()
#     s.init_data()
#     (conn, cursor) = DbConn().open_db()

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

#     = DbConn().open_db(close=True)
