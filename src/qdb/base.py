from PySide6.QtSql import QSqlQuery, QSqlError
from qdb.util import DbHelper
from qdb.log import DbLog
from qdb.keys import LOG
from inspect import stack
from os import path
from inspect import stack


class DbBase():
    """
        A simple class to perform some basic QSql setups
    """
    _wasError = False
    _lastError = None
    _show_stack = False
    _errorMessages = {}

    def __init__(self):
        pass

    def setupLogger(self):
        print('ksetupLogger')
        self.logger = DbLog(self.__class__.__name__)
        print( 'end setupLogger')

    def getReturnCode(self, query: QSqlQuery):
        rtn = self.wasGood() and query.numRowsAffected() > 0
        query.finish()
        return rtn

    def _formatInsertVariable(self, table_name: str, field_value_dict: dict, replace: bool = False, ignore: bool = False) -> str:
        """ Take a dictionary and format for an insert 
            You can set mode of insert by setting replace or ignore flags"""
        field_names = ','.join(list(field_value_dict.keys()))
        field_values = ','.join(['?' for i in range(0, len(field_value_dict))])
        if replace:
            insertOp = 'OR REPLACE'
        elif ignore:
            insertOp = 'OR IGNORE'
        else:
            insertOp = ''

        return "INSERT {} INTO {} ({}) VALUES ({})".format(insertOp, table_name, field_names, field_values)

    def _prepareInsertVariable(self, sql, parms: dict) -> QSqlQuery:
        return DbHelper.bind(DbHelper.prep(sql), list(parms.values()))

    def _formatUpdateVariable(self, table_name: str, key_name: str,  field_value_dict: dict) -> str:
        """ 
            Take a dictionary and format for update. 
            You need to pass the keyfield and the keyvalue
            Which cannot be part of the parms
        """
        field_to_value = ["{} = ?".format(field_name.strip(
            '*')) for field_name in list(field_value_dict.keys())]

        return "UPDATE {} SET {}  WHERE {} = ?".format(table_name, ','.join(field_to_value), key_name)

    def showStack(self, show: bool = True):
        self._show_stack = show

    def _checkError(self, query: QSqlQuery) -> bool:
        self._errorMessages = {'sql': query.lastQuery(
        ), 'values': query.boundValues(), 'error_type': '?: Unknown error'}
        self._lastError = query.lastError()
        self._wasError = query.lastError().isValid()

        if self._lastError.type() == QSqlError.ConnectionError:
            self._errorMessages['error_type'] = 'Database: Connection Error'
        elif self._lastError.type() == QSqlError.StatementError:
            self._errorMessages['error_type'] = 'Program: SQL Error'
        elif self._lastError == QSqlError.TransactionError:
            self._errorMessages['error_type'] = 'Database: Transaction error'

        if self._wasError:
            self._errorMessages['error_db'] = self._lastError.databaseText()
            self._errorMessages['error_driver'] = self._lastError.driverText()
            if self._show_stack:
                stacklist = stack()
                for i in range(len(stacklist)-1, 0, -1):
                    stackinfo = stacklist[i]
                    tag = 'caller-' + str(len(stacklist) - i)
                    fname = "{}/{}".format(path.basename(path.dirname(
                        stackinfo.filename)), path.basename(stackinfo.filename))
                    self._errorMessages[tag] = "{}:{}@{}".format(
                        fname, stackinfo.function, stackinfo.lineno)
                caller = stack()[1].function
                self.loger.log(LOG.critical, caller, 'DbBase error')
                for k in sorted(self._errorMessages):
                    self.logger.log(LOG.critical, caller, "{:12}: '{}'".format(
                        k, self._errorMessages[k]))
        return self._wasError

    def lastError(self) -> QSqlError:
        """ Return last error returned from database operation"""
        return self._lastError

    def isError(self) -> bool:
        return self._wasError

    def wasGood(self) -> bool:
        """ Returns True if no error was reported """
        return not self._wasError

    def logmsg(self) -> str:
        if self._lastError and self._wasError:
            return "Database error: '{}'  Database: '{}' SQL: '{}'".format(
                self._errorMessages['error_type'],
                self._lastError.databaseText(),
                self._errorMessages['sql'])
        return ''


    def __init__(self):
        super().__init__()
        self._errorMessages = {}
        self._lastError = QSqlError()
        self._wasError = False
