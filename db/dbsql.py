# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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

import sqlite3
import logging
from db.dbconn     import DbConn
from db.keys       import DbKeys

###
### dbsql contains a number of methods that are used instead of stored procs
### Think of them as 'macro' commands. Most try to take a sensible number of
### parms and perform functions that will protect the db against (my) stupid
### mistakes.
###
### Every function requires the database be open before using.

def  _primaryKeyList( byPosition, byName, keyName )->list:
    
    if byName is not None and keyName in byName:
        return [ byName[keyName ]]
    return [byPosition[0] ]

def _forceDictionary(byPosition, byName, *argv):
    """"
        ForceDictionary will take the args, kwargs, and a list of paramters as they should have been
        passed and turn them into a dictionary. This is primarily used for single parameter SQL
        statements. Makes the calling just a bit shorter and similar to what was used in previous versions

        Note: *argv can either be a tuple or a tuple containing a list. 
    """
    if byName is None:
        byName = {}
    if byPosition is None or len(byPosition) == 0 or argv is None:
        return byName
    if isinstance(argv[0],list):
        # list
        for index, arg in enumerate(argv[0]):
            if index >= len(byPosition):
                break
            byName[arg] =str( byPosition[index] )
    else:
        # tuple 
        for index, arg in enumerate(argv):
            if index >= len(byPosition):
                break
            byName[arg] = byPosition[index]
    return byName
    
def _insertStatment( table, fields, ignore=False):
    if table =="" or table is None:
        raise ValueError( "No table name passed")
    if fields is None or len(fields) < 1:
        raise ValueError( "{}: Not enough parameters passed".format("table"))
    IGNORE = "OR IGNORE " if ignore else ""
    replacement_string = '?,'*len(fields)
    return "INSERT {}INTO {} ( {} ) VALUES ( :{} )".format( 
        'OR IGNORE ' if ignore else "" , 
        table , 
        ",".join( fields.keys()), 
        ", :".join( fields.keys() ) )


def _sqlInsert(table, fields, ignore=False, commit=True )->int:
    """
        Insert a record into the database. If you set 'ignore' as True
        then it will get the current record ID for the existing record.
        If false, it will re-raise the error
    """
    (conn, cursor ) = DbConn().handles()
    originalFields = fields.copy()
    try:
        sql = _insertStatment( table, fields, ignore=False)
        cursor.execute( sql , list( fields.values() ) )
        recordID = int(cursor.lastrowid)
    except sqlite3.OperationalError as err:
        logging.error("Exception: '{}' SQL: '{}', Fields: '{}'".format( err , sql, fields ))
        raise err
    except sqlite3.IntegrityError as err:
        if ignore:
            recordID = _sqlGetID( table, originalFields )
        else:
            raise err
    finally:
        if commit:
            conn.commit()
    del originalFields
    return recordID

def SqlCleanDB( ):
    (con, cursor) = DbConn().handles()
    for table in DbKeys().primaryKeys:
        cursor.execute( "REINDEX {};".format( table ))
    cursor.execute("vacuum;")

def _checkParms(  table, args, kwargs ):
    if not table:
        raise ValueError("No table name passed")
    if len( args ) == 0 and len( kwargs ) == 0:
        raise ValueError("No parameters passed ")

def SqlInsert( table, ignore=False ,commit=True, *args, **kwargs )->int:
    """
        Insert a record into the database. If you set 'ignore' as True
        then it will get the current record ID for the existing record.
        If false, it will re-raise the error
        Return is the record ID for the key
    """
    _checkParms( table, args, kwargs )
    return _sqlInsert(table, _forceDictionary(args, kwargs, DbKeys.primaryKeys[table][0]), ignore=ignore, commit=commit )

def _generateKeys( table , useName=False):
    """
        generate keys takes a table name, looks up the keys and builds a 
        key list from the keyvalues. 
        e.g.: book, 'title1' becomes book='title1'
    """
    keys = DbKeys.primaryKeys[ table ]
    kvlist = []
    for i in range(len( keys ) ):
        if useName:
            kvlist.append( "{}=:{}".format( keys[i] , keys[i]))
        else:
            kvlist.append( "{}=?".format( keys[i] ))
    return "{}".format( " AND ".join( kvlist) )

def _generateSetValues( table, fields ):
    """
        generate the setter values for an update. This takes a table and
        a list of fields. Table is optional but will prepend the field name
        It wll look like 'table.field=:field'. This requires a dictionary 
        for the field to be set.
        Note: keyvalues can contain '*' + the primary key name. This will
        add in a 'set' for the primary key.
    """
    valueList = []
    for key in fields.keys():
        if key not in DbKeys.primaryKeys[ table ]:
            if key.startswith( '*'):
                key = key.lstrip('*')
            valueList.append( "{}=?".format(  key ) )
    return ','.join(valueList)

def _resequenceValues( table, fields )->list:
    """
        _resequence Values takes the table name and field list
        and makes sure data values appear before key values.
        This matches what you expect in an UPDATE statement:
        UPDATE table SET field=? WHERE key=?
    """
    dataValues = []
    keyValues = []
    for key,value in fields.items():
        if key in DbKeys.primaryKeys[ table ]:
            keyValues.append( value )
        else:
            dataValues.append( value )
    return dataValues +  keyValues

def _updateStatement( table, fields ):
    """
        Generate a general update statement.
        The key(s) must be in the fields list.
    """
    if table is None or table == "":
        raise ValueError("No table specified")
    if fields is None or len( fields ) < 2:
        raise ValueError("No fields to update ({})".format( type(fields)))
    sql = "UPDATE {} SET {} WHERE {};".format( 
        table, 
        _generateSetValues( table, fields ), 
        _generateKeys( table ) )
    return sql

def _sqlGetID( table, fields ):
    """
        Get the record ID for a field.
        The query requires only primary fields
        If no record found you get -1
    """
    if table is None or table == "":
        raise ValueError("No table specified")

    keyvalues = []
    keyList = DbKeys.primaryKeys[ table ]
    for kv in keyList:
        keyvalues.append(fields[kv]) 
    sql = "SELECT id FROM {} WHERE {}".format(
        table,
        _generateKeys(table ) )
    result = DbConn().cursor().execute( sql ,  keyvalues )
    recordID=-1
    if result is not None:
        row = result.fetchone()
        if row is not None:
            recordID = int(row['id'])
    return recordID

def SqlGetID( table,  *args, **kwargs)->int:
    """
        This will return the ID for a table. It can be called as:
        SqlGetID( table, 'keyvalue', .....) or
        SqlGetID( table, primarykey1='keyvalue'....)
        If the keyvalues are passed as args the sequence must match
        the order listed in DbKeys. Mainly good for single key tables.
    """
    _checkParms( table, args, kwargs )
    fields = _forceDictionary( args, kwargs , DbKeys.primaryKeys[ table ] )
    return _sqlGetID( table, kwargs )

def SqlUpdate( table,  commit=True, *args, **kwargs)->int:
    """
        Update the database from the data passed.
        The number of records changed is returned.
    """
    _checkParms( table, args, kwargs )
    (conn, cursor ) = DbConn().handles()
    ## key value must be last
    keyedArgs = _forceDictionary( args , kwargs, 'book')
    qArgs = _resequenceValues( table, keyedArgs )
    cursor.execute( _updateStatement( table, keyedArgs ) ,qArgs )
    if commit:
        conn.commit()
    return cursor.rowcount

def _sqlUpsert( table, fields, commit=True )->int:
    """
        Construct the INSERT ... ON CONFLICT action
        Two keys are allowed. They will be removed from the CONFLICT
        statement (otherwise you get errors)
        Why not use OR REPLACE? Because partial updates may not
        contain all fields. This allows a similar action and won't
        replace everything.
    """
    
    (conn, cursor ) = DbConn().handles()
    originalFields = fields.copy()
    try:
        sql = _insertStatment( table, fields, ignore=False)
        cursor.execute( sql , list( fields.values() ) )
        recordID = int(cursor.lastrowid)
    except sqlite3.OperationalError as err:
        logging.error("Exception: '{}' SQL: '{}', Fields: '{}'".format( err , sql, fields ))
        raise err
    except sqlite3.IntegrityError as err:
        qArgs = _resequenceValues( table, originalFields )
        sql = _updateStatement( table, originalFields )
        cursor.execute( sql , qArgs  )
        recordID = _sqlGetID( table, originalFields )
    finally:
        if commit:
            conn.commit()
    del originalFields
    return recordID

def SqlUpsert( table, commit=True, *args, **kwargs ):
    """
        Construct the INSERT ... ON CONFLICT statement
        Two keys are allowed. They will be removed from the CONFLICT
        statement (otherwise you get errors)
    """
    _checkParms( table, args, kwargs )
    return _sqlUpsert( table, _forceDictionary(args, kwargs, DbKeys.primaryKeys[table][0]), commit=commit )

def SqlRowString( result )->str:
    """
        Take a result, get all the rows and output in a 'pretty' format.
        The result will be returned as a string. This is only used during
        debugging.
    """
    lines = []
    if result is None:
        return('(None)')
    try:
        result = result.fetchall()
    finally:
        for row in result:
            line = []
            for key in row.keys():
                line.append( "{}='{}'".format( key , row[key]))
            lines.append(", ".join( line ))
    return ("\n".join( lines) )
    
def SqlColumnNames( table:str )->list:
    """
        Returns a list of the column names as a simple list
    """
    col_data = DbConn().connection().execute(f'PRAGMA table_info({table});').fetchall()
    return [entry[1] for entry in col_data]

def SqlDump( filename:str ):
    con = DbConn().connection()
    with open(filename, 'w') as f:
        for line in con.iterdump():
            f.write('%s\n' % line)

