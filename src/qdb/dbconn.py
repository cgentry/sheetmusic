"""
Database interface: Generic DB Connector

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from dataclasses import dataclass
import logging
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from qdb.keys import DbKeys


@dataclass(init=False)
class DbVars():
    """ System-wide databse variables """
    _qdb_conn = None
    _qdb_name = None
    _qdb_path = None


class DbConn(DbVars):
    """ Low level Connection to Database connector"""

    @staticmethod
    def open_db(dbpath: str = None,
                dbname: str = DbKeys.VALUE_DEFAULT_DB_FILENAME,
                trace: bool = False) -> QSqlDatabase:
        """Open a database connector

        Args:
            dbpath (str, optional): Path to database file.
                If none passed, use previous path
                Defaults to None.
            dbname (str, optional): Name to give connection.
                Defaults to DbKeys.VALUE_DEFAULT_DB_FILENAME.
            trace (bool, optional): Future flag.
                Defaults to False.

        Raises:
            ValueError: No path to database

        Returns:
            QSqlDatabase: Database connection
        """
        del trace  # Will need to reimplement.

        if DbVars._qdb_conn is None or not DbVars._qdb_conn.isValid():
            if dbpath is None:
                if DbVars._qdb_path is None:
                    raise ValueError("\tNo library name passed")

                return DbConn.reopen_db()
        else:  # DbVars._qdb_conn is not none
            DbVars._qdb_conn.open()
            return DbVars._qdb_conn

        DbVars._qdb_path = dbpath
        DbVars._qdb_conn = QSqlDatabase.addDatabase(
            "QSQLITE", connectionName=dbname)
        DbVars._qdb_conn.setDatabaseName(dbpath)

        DbVars._qdb_name = QSqlDatabase.connectionName(DbVars._qdb_conn)
        DbVars._qdb_conn.open()
        return DbVars._qdb_conn

    @staticmethod
    def reopen_db() -> QSqlDatabase:
        """Reopen the current database connection

        Returns:
            QSqlDatabase: Database connection
        """
        DbVars._qdb_conn = QSqlDatabase.database(DbVars._qdb_name, open=True)
        if not DbVars._qdb_conn.isValid():
            logging.critical("DB Open error: %s",
                             DbVars._qdb_conn.lastError().text())
        return DbVars._qdb_conn

    @staticmethod
    def db() -> QSqlDatabase:
        """Reopen the database connection
        This is an alias for reopen_db()

        Returns:
            QSqlDatabase: Database connection
        """
        return DbConn.reopen_db()

    @staticmethod
    def is_open() -> bool:
        """ Return true if the database connection is open """
        if DbVars._qdb_name is not None:
            return QSqlDatabase.database(DbVars._qdb_name, open=False).isOpen()
        return False

    @staticmethod
    def close_db():
        """ This will close the db but doesn't destroy the db entry """
        if DbVars._qdb_conn is not None and DbVars._qdb_conn.isOpen():
            DbVars._qdb_conn.commit()
            DbVars._qdb_conn.close()

    @staticmethod
    def clear():
        """Clear path and name variables
        """
        DbConn.close_db()
        DbVars._qdb_path = None
        DbVars._qdb_name = None

    @staticmethod
    def is_clear() -> bool:
        """Determine if the path and name have been cleared

        Returns:
            bool: True if the path and name are empty
        """
        return DbVars._qdb_path is None and DbVars._qdb_name is None

    @staticmethod
    def destroy_connection():
        """ Remove the database connection from Qt system
        ONLY use this when exiting the program
        """
        DbConn.close_db()
        DbVars._qdb_conn = None
        QSqlDatabase.removeDatabase(DbVars._qdb_name)
        DbConn.clear()

    @staticmethod
    def is_valid(opendb=False) -> bool:
        """ This wil chek if the database is valid
        If opendb=True, the database will be re-opened."""
        return QSqlDatabase.database(DbVars._qdb_name, open=opendb).isValid()

    @staticmethod
    def name() -> str:
        """ This will return the connection name, not the db name """
        return (QSqlDatabase.connectionName(DbVars._qdb_conn)
                if DbVars._qdb_conn is not None
                else None)

    @staticmethod
    def dbname() -> str:
        """ This will return the db name ( VALUE_DEFAULT_DB_FILENAME ) """
        if DbVars._qdb_conn is not None:
            return QSqlDatabase.databaseName(DbVars._qdb_conn)
        return None

    @staticmethod
    def get_connection(opendb=False) -> QSqlDatabase:
        """ Return a database connection """
        rtn = QSqlDatabase.database(DbVars._qdb_name, open=opendb)
        return rtn if rtn.isValid() else None

    @staticmethod
    def query() -> QSqlQuery:
        """ Create an SQL Query connection """
        return QSqlQuery(DbConn.db())

    @staticmethod
    def get_column_names(table: str) -> list:
        """ Retrieve a list of all column names from the database
            (Usefull when creating queries)
        """
        if not DbVars._qdb_conn or DbVars._qdb_conn.isOpenError():
            raise RuntimeError("Database is not open")
        columns = []
        record = DbVars._qdb_conn.record(table)
        for index in range(0, record.count()):
            name = record.fieldName(index)
            if ':' in name:
                x = name.split(':')
                columns.append(x[0])
            else:
                columns.append(name)
        return columns

    @staticmethod
    def commit() -> bool:
        """ write out all transactions in database """
        if DbVars._qdb_conn is not None and DbVars._qdb_conn.isOpen():
            return DbVars._qdb_conn.commit()
        return False

    @staticmethod
    def clean_db() -> None:
        """Issue a re-index on the database then vacuum

        This will compact the database with clean indexes
        """
        query = QSqlQuery(DbVars._qdb_conn)
        for table in DbKeys().primaryKeys:
            query.exec(f"REINDEX {table};")

        query.exec("vacuum;")
        query.finish()
        del query
