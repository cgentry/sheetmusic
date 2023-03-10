from PySide6.QtSql import QSqlQuery
from qdb.dbconn    import DbConn
import logging
import  base64
import  pickle


class DbHelper:
    """ These are simple helper methods used to cut down on some of the
        code bulk that can occur. 
    """

    @staticmethod
    def addColumnNames( sqlstatement:str, column_names:list )->str:
        """ Simple routine to replace the '*' with the column names 
            (Usefull for implementing better dictionary queries
        """
        return sqlstatement.replace( '*', ','.join( column_names))

    @staticmethod
    def prep(  sqlstatement:str)->QSqlQuery:
        """ prep accepts an sql statment and returns a query with the statment prepped"""
        query=DbConn.query()
        if query.prepare( sqlstatement ):
            return query
        raise ValueError("Could not prepare SQL {};\nError '{}'".format( sqlstatement , query.lastError().text()  ))

    @staticmethod
    def bind( query:QSqlQuery , param , name:str=None )->QSqlQuery:
        """ Bind will bind values to an SQL query
            param: parameters to bind they can be:
                list - simple list of values
                dict - key, value pair(s)
                single -
                    this can be just the value (for a '?' in SQL)
                    or you can bind with value and name.
            name is only used when there is a single parameter passed.
        """
        if param:
            try:
                if isinstance( param, list ):
                    for value in param:
                        query.addBindValue( value )
                elif isinstance( param, dict ):
                    for key, value in param.items() :
                        query.bindValue( "+"+key , value )
                else:
                    if name:
                        query.bindValue( name , param )
                    else:
                        query.addBindValue( param )
            except Exception as err:
                logging.critical( "Bind error: {}\nParm type: {}\nParm: '{}'".format( str(err), type(param), param) )
                raise err
        return query

    @staticmethod
    def fetchone( sql:str , param=None, name:str=None, default=None, index:int=0, debug=False, endquery=None)->str:
        """ Fetch a single value of one row from the database. 
        
            sql:    SQL statement
            param:  Parameters to use for query. This can be a dictionary, list, or single value
            name:   named parameter - only used when a single value is in param
            index:  index of return values from SQL (e.g. select a, b FROM Table' pass 1 for 'b' )
            endquery: Function to call when query is done, e.g.: def endquery( query:QSqlQuery )
        """
        logging.debug("\nfetchone: ")
        query = DbHelper.bind( DbHelper.prep( sql ), param, name )
        if query.exec() and query.next():
            rtn = query.value(index)
        else:    
            rtn = default
        logging.debug(  "\tSQL: '{}'".format( query.lastQuery() ))
        logging.debug( "\t", query.boundValues() )
        logging.debug("\tLast error:", query.lastError(), "Return:", rtn )
        if endquery is not None:
            endquery( query )
        query.finish()
        return rtn

    @staticmethod
    def fetchrow( sql:str , param, db_fields_to_return:list, debug=False, endquery=None)->dict:
        """ Lookup a single row and return the names back. param is the key value(s)
            which can be a single entry (str), a list, or a dictionary. Return is 
            always a dictionary which is defined in 'db_fields_to_return'.
            db_fields_to_return must be the names, in order of returned values.
        """
        query = DbHelper.bind( DbHelper.prep( sql ) , param )
        if debug:
            msg = ",".join( [ str(x) for x in query.boundValues() ])
            logging.debug("fetchrow: SQL: '{}' Parms: {}".format( query.lastQuery() , msg ) )
        if query.exec():
            record = DbHelper.record( query ,db_fields_to_return)
        else:
            msg = ",".join( [ str(x) for x in query.boundValues() ])
            logging.critical( "fetchrow error: {}\n\t{}\nParms: '{}'".format(  query.lastError().text() , query.lastQuery() , msg ) )
            record = {}
        if endquery is not None:
            endquery( query )
        query.finish()
        if debug:
            logging.debug("fechrow: Result:", record )
        return record

    @staticmethod
    def fetchrows( sql:str , param, fields:list , endquery=None )->list:
        """ Fetch multiple rows that match the criteria
            param:  list or dictionary of values to bind
            fields: fields from the query to return
            endquery: routine to call at end of query. If None, call internal endquery
        """
        query = DbHelper.bind( DbHelper.prep(sql) , param )
        if query.exec():
            rtn = DbHelper.all( query , fields ) 
        else:
            rtn =  [] 
        if endquery is not None:
            endquery( query )
        query.finish()
        return rtn

    @staticmethod
    def query( sql:str, param , name:str=None)->QSqlQuery:
        """ Perform prep and bind operation with an sql statement and then params"""
        return DbHelper.bind( DbHelper.prep( sql ) , param , name )

    @staticmethod
    def all(query:QSqlQuery, fields:list)->list:
        """ Take the executed query for multiple records and
            return a list of dictionaries that contain the values
        """
        rtnList = []
        record = DbHelper.record( query ,fields)
        while isinstance( record , dict ) :
            rtnList.append( record )
            record = DbHelper.record( query ,fields)
        return rtnList

    @staticmethod
    def allList( query:QSqlQuery, index:int=0 )->list:
        """ This takes the executed query and returns a list for a single field by index"""
        rtnList = []
        while query.next():
            rtnList.append(query.value(index) )
        return rtnList

    @staticmethod
    def allListByName( query:QSqlQuery, fieldname:str )->list:
        """ This takes the query and returns a list for a single field by name"""
        fieldNo = query.record().indexOf( fieldname )
        return DbHelper.allList( query, fieldNo )

    @staticmethod
    def record( query:QSqlQuery, fields:list):
        """ Take the executed query and return a dictionary.
            The fields is a list of names matching return parameters
        """
        newRecord = None
        if query.next():
            newRecord = {}
            for i,name in enumerate( fields ):
                newRecord[ name ] = query.value(i)
        else:
            logging.debug("record: {} SQL: {} Parms{}".format( 
                query.lastError().text() , 
                query.lastQuery() , 
                ",".join( [ str(x) for x in query.boundValues() ] ) ) 
            )
        return newRecord

    @staticmethod
    def encode( value )->str:
        """ encode will take any arbitrary value and encode to ascii"""
        if value is None:
            return None
        ps= pickle.dumps( value )
        en = base64.b64encode(ps).decode('ascii') 
        return en 

    @staticmethod
    def decode( value:str ):
        """ decode takes a string that has been encoded by 'encode' and return the original value """
        if value is None:
            return None
        dc =  pickle.loads(base64.b64decode(value))
        return dc

       
    