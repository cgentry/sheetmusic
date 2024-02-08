"""
Database interface: Base for database

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from inspect import stack
from os import path

from PySide6.QtSql import QSqlQuery, QSqlError

from qdb.log import DbLog, LOG
from qdb.util import DbHelper

class DbBase():
    """
        A simple class to perform some basic QSql setups
    """
    _was_error = False
    _last_error = None
    _show_stack = False
    _err_msgs = {}

    def __init__(self):
        super().__init__()
        self._last_error = QSqlError()
        self.logger = None

    def setup_logger(self):
        """ Initialise the standard logger for the database """
        self.logger = DbLog(self.__class__.__name__)

    def get_rtn_code(self, query: QSqlQuery)->bool:
        """Return whether last operation was successful

        Args:
            query (QSqlQuery): Query operation

        Returns:
            bool: True if no error and rows were affected.
                False if error or no rows affected
        """
        rtn = self.was_good() and query.numRowsAffected() > 0
        query.finish()
        return rtn

    def _format_insert_variable(self,
                              table_name: str,
                              field_value_dict: dict,
                              replace: bool = False,
                              ignore: bool = False) -> str:
        """Format an Insert string for the database

        Args:
            table_name (str): Required table name
            field_value_dict (dict): Required key: value for insert
            replace (bool, optional): Use 'OR REPLACE' on insert. Defaults to False.
            ignore (bool, optional): Use 'OR IRGNORE' on insert. Defaults to False.

        Returns:
            str: Complete INSERT....TABLE... string
        """
        if table_name is None or field_value_dict is None:
            raise RuntimeError( 'Invalid parameters passed')
        field_names = ','.join(list(field_value_dict.keys()))
        field_values = ','.join(['?' for i in range(0, len(field_value_dict))])
        if replace:
            insert_op = 'OR REPLACE'
        elif ignore:
            insert_op = 'OR IGNORE'
        else:
            insert_op = ''

        return f"INSERT {insert_op} INTO {table_name} ({field_names}) VALUES ({field_values})"

    def _prepare_insert_variable(self, sql, parms: dict) -> QSqlQuery:
        """ Bind the parameters to an SQL statement
            The parms must be an key: value dictionary
        """
        return DbHelper.bind(DbHelper.prep(sql), list(parms.values()))

    def _format_update_variable(self,
                table_name: str,
                key_name: str,
                field_value_dict: dict) -> str:
        """Take a dictionary and format for update.
            You need to pass the keyfield and the keyvalue
            Which cannot be part of the parms

        Args:
            table_name (str): name of the db table
            key_name (str): Primary key column name
            field_value_dict (dict): key: value to be updated

        Returns:
            str: SQL statement that looks like
                UPDATE table SET key=?, key=? .... WHERE key_name=?
        """
        field_to_value = [f"{field_name.strip('*')} = ?" \
            for field_name in list(field_value_dict.keys())]
        field_values = ','.join(field_to_value)

        return f"UPDATE {table_name} SET {field_values}  WHERE {key_name} = ?"

    def show_stack(self, show: bool = True):
        """Determine if the statck should be shown on error
        This is usually used only for testing to stop large dumps

        Args:
            show (bool, optional): Show if true. Defaults to True.
        """
        self._show_stack = show

    def _check_error(self, query: QSqlQuery) -> bool:
        """ Passing the query object, will log and return true/false """
        self._err_msgs = {'sql': query.lastQuery(
        ), 'values': query.boundValues(), 'error_type': '?: Unknown error'}
        self._last_error = query.lastError()
        self._was_error = query.lastError().isValid()

        if self._last_error.type() == QSqlError.ConnectionError:
            self._err_msgs['error_type'] = 'Database: Connection Error'
        elif self._last_error.type() == QSqlError.StatementError:
            self._err_msgs['error_type'] = 'Program: SQL Error'
        elif self._last_error == QSqlError.TransactionError:
            self._err_msgs['error_type'] = 'Database: Transaction error'

        if self._was_error:
            self._err_msgs['error_db'] = self._last_error.databaseText()
            self._err_msgs['error_driver'] = self._last_error.driverText()
            if self._show_stack:
                # pylint: disable=C0209
                stacklist = stack()
                for i in range(len(stacklist)-1, 0, -1):
                    stackinfo = stacklist[i]
                    tag = 'caller-' + str(len(stacklist) - i)
                    fname = "{}/{}".format(
                        path.basename(path.dirname(stackinfo.filename)),
                                path.basename(stackinfo.filename))
                    self._err_msgs[tag] = "{}:{}@{}".format(
                        fname, stackinfo.function, stackinfo.lineno)
                caller = stack()[1].function
                self.logger.log(LOG.critical, caller, 'DbBase error')
                for k in sorted(self._err_msgs):
                    self.logger.log(LOG.critical, caller, "{:12}: '{}'".format(
                        k, self._err_msgs[k]))
                # pylint: enable=C0209
        return self._was_error

    def last_error(self) -> QSqlError:
        """ Return last error returned from database operation"""
        return self._last_error

    def is_error(self) -> bool:
        """ Was there an error? (True/False)"""
        return self._was_error

    def was_good(self) -> bool:
        """ Returns True if no error was reported """
        return not self._was_error

    def logmsg(self) -> str:
        """ Format an error message string"""
        if self._last_error and self._was_error:
            # pylint: disable=C0209
            return "Database error: '{}'  Database: '{}' SQL: '{}'".format(
                self._err_msgs['error_type'],
                self._last_error.databaseText(),
                self._err_msgs['sql'])
            # pylint: enable=C0209
        return ''
