"""
Database : System table interface

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.util import DbHelper
from qdb.base import DbBase

class DbSystem(DbBase):
    """
        You should have already opened the database.
        You can improve performance by instantiating this once
        and all the statments get prepared. Makes it much faster
    """

    SQL_SYSTEM_GET = "SELECT value FROM System WHERE key=?"
    SQL_SYSTEM_GET_ALL = "SELECT key, value FROM System"
    SQL_SYSTEM_INSERT_REPLACE = "INSERT OR REPLACE INTO System( key, value ) VALUES(?,?)"
    SQL_SYSTEM_INSERT_IGNORE = "INSERT OR IGNORE  INTO System( key, value ) VALUES(?,?)"
    SQL_SYSTEM_INSERT_FAIL = "INSERT            INTO System( key, value ) VALUES(?,?)"
    SQL_SYSTEM_DELETE = "DELETE FROM System Where key=?"

    SQL_FLAG_INSERT_REPLACE = 1
    SQL_FLAG_INSERT_IGNORE = 2
    SQL_FLAG_INSERT_FAIL = 0

    sql_has_been_prepared = False

    def __init__(self):
        super().__init__()
        self.setup_logger()

    def get_all(self) -> dict:
        """
            Return all the values in the database as a dictionary
            Note you really should be doing a 'get' for values you
            want rather than sucking in all of them. This is used by
            the UI interface
        """
        values = {}
        query = QSqlQuery(DbConn.db())
        if query.exec("SELECT * FROM System"):
            while query.next():
                values[query.value(0)] = query.value(1)
        else:
            self.logger.error(f"{query.lastError().text()}")
        self._check_error(query)
        query.finish()
        return values

    def save_all_list(self,
                      new_data: list,
                      replace: bool = False,
                      ignore: bool = False) -> int:
        """ Save all data from a list of values """
        count = 0
        for item in new_data:
            if 'key' in item and 'value' in item:
                if self.set_value(item['key'], item['value'], replace, ignore):
                    count += 1
        return count

    def save_all_dict(self,
                      new_data: dict,
                      replace: bool = False,
                      ignore: bool = False) -> int:
        """ Save all data from a dictionary """
        count = 0
        for key, value in new_data.items():
            if self.set_value(key, value, replace=replace, ignore=ignore):
                count += 1
        return count

    def save_all(self, new_data: dict, replace: bool = False, ignore: bool = False) -> int:
        """
            The input should be either dictionary values:
                {key:..., value:..., key:..., value:...}
            or a list of key/value pairs:
                [ {key: value}, {key: value}....]
            anything else raises value error
            You should set them one-by-one, but this is used by the UI interface
        """
        try:
            if isinstance(new_data, list):
                return self.save_all_list(new_data, replace, ignore)
            if isinstance(new_data, dict):
                return self.save_all_dict(new_data, replace, ignore)
        except Exception as err:
            # msg = "saveAll: type '{}' value '{}'".format( type( item ), item)
            # self.logger.critical( msg ,trace=True )
            raise err

        msg = f"saveAll: Invalid type passed '{type(new_data)}'"
        self.logger.error(msg)
        raise ValueError(msg)

    def get_value(self, key: str, default: str = None) -> str:
        """ Fetch value from database using key """
        rtn = default
        if key:
            rtn = DbHelper.fetchone(self.SQL_SYSTEM_GET, param=key, default=default)
        return rtn

    def set_value(self,
                  key: str,
                  value: str = None,
                  replace: bool = False,
                  ignore: bool = False) -> bool:
        """
            Insert a value into the dbtable System.
            if the value is None, the key will be deleted from the database
            True or false will be returned if the operation is a success
        """
        if key is None or key == '':
            raise ValueError('No key passed')
        if value is None:
            query = DbHelper.bind(DbHelper.prep(self.SQL_SYSTEM_DELETE), key)
            query.exec()
            self._check_error(query)
            query.finish()
            del query
            return self.was_good()

        if replace:
            sql = self.SQL_SYSTEM_INSERT_REPLACE
        elif ignore:
            sql = self.SQL_SYSTEM_INSERT_IGNORE
        else:
            sql = self.SQL_SYSTEM_INSERT_FAIL

        query = DbHelper.prep(sql)
        query = DbHelper.bind(query, [key, value])
        query.exec()
        self._check_error(query)
        query.finish()
        del query
        return self.was_good()
