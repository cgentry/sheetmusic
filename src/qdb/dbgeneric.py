"""
 Database interface : Generic (base) interface class

 DbGenericName - simple key/value table

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtSql import QSqlQuery
from qdb.log import DbLog
from qdb.dbconn import DbConn
from qdb.util import DbHelper



class DbGenericName():
    """
        DbGenricName is a simple database class for tables
        Table only contains id, name, and value columns
    """
    table_name = ""
    table_fields = ['name', 'value', 'id']

    SQL_GET_LIKE = """
        SELECT name, value, id
        FROM :TABLE
        WHERE name LIKE ?
        ORDER BY name COLLATE NOCASE
        """
    SQL_SELECT_ID = """SELECT id FROM :TABLE WHERE name=?"""
    SQL_SELECT_ALL = """
        SELECT name
        FROM :TABLE
        ORDER BY name COLLATE NOCASE :sequence"""
    SQL_EDIT_NAME = """
        UPDATE :TABLE
        SET name = :new_value
        WHERE name = :current_value"""
    SQL_GET_ID = "SELECT id FROM :TABLE WHERE name=?"
    SQL_INSERT = "INSERT INTO :TABLE (name) VALUES (?)"

    def __init__(self, table: str = None):
        self.logger = None
        self.table_name = table

    def setup_logger(self):
        """ Initialise the logger for this class """
        self.logger =DbLog(self.__class__.__name__)

    def get_all(self, sequence='ASC') -> list:
        """ Fetch the 'name' field from the database and return it as a list (rather than a row) """
        query = QSqlQuery(DbConn.db())
        if not query.exec(self.SQL_SELECT_ALL.\
                    replace(':sequence', sequence).\
                    replace(':TABLE', self.table_name)):
            self.logger.critical("getall: {query.lastError().text()}")
            return []
        all_records = DbHelper.all_list(query, 0)
        query.finish()
        del query
        return all_records

    def get_column(self, sql:str) -> list:
        """Pass an SQL query in and return a list of all results

        Args:
            sql (str): SQL query string that selects ONE column

        Returns:
            list: return single column list
        """
        query = QSqlQuery(DbConn.db())
        if not query.exec(sql):
            self.logger.critical(
                f"getColumn: {query.lastError().text()}" )
            return []
        all_records = DbHelper.all_list(query, 0)
        query.finish()
        del query
        return all_records

    def get_id(self, name: str, create: bool = False) -> int:
        """Retrieve the 'id' field for a record matching name

        Args:
            name (str): Name to lookup
            create (bool, optional): Create the record if doesn't exist.
                Defaults to False.

        Returns:
            int: Key if found or created
        """
        sql = self.SQL_SELECT_ID.replace(':TABLE', self.table_name)
        val = DbHelper.fetchone(sql, param=name)
        if val is None and create:
            val = self.insert_id(name)
        return val

    def insert_id(self, name: str) -> int:
        """Insert a key/value pair into the table and return the last ID
        The value will be whatever is the default for the table.

        Args:
            name (str): Key to insert

        Returns:
            int: New record ID
        """
        sql = self.SQL_INSERT.replace(':TABLE', self.table_name)
        query = DbHelper.bind(DbHelper.prep(sql),  name)
        val = (query.lastInsertId() if query.exec() else None)
        query.finish()
        return val

    def edit(self, current_value: str, new_value: str) -> int:
        """Change the value of the name field

        If the values are the same or if you pass None for either,
        nothing is performed.

        Args:
            current_value (str): previous value
            new_value (str): new value

        Returns:
            int: number of rows changed
        """
        if current_value is None or new_value is None or current_value == new_value:
            return 0
        sql = self.SQL_EDIT_NAME.replace(':TABLE', self.table_name)
        query = DbHelper.bind(DbHelper.prep(sql),
                              {'new_value': new_value, 'current_value': current_value})
        rows = (query.numRowsAffected if query.exec() else 0)
        query.finish()
        return rows

    def has(self, name: str) -> bool:
        """Check to see if table has the value

        Args:
            name (str): value to check for

        Returns:
            bool: True if exists, False otherwise
        """
        return self.get_id(name) is not None
