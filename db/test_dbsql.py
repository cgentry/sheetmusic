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

import sys
import sqlite3
import unittest

sys.path.append("../")
from db.dbsql  import SqlColumnNames, SqlUpsert, SqlRowString, SqlInsert, SqlGetID,SqlUpdate, _sqlGetID,_forceDictionary,_generateKeys, _generateSetValues, _primaryKeyList
from db.dbconn import DbConn
from db.setup  import Setup


class TestSql( unittest.TestCase):
    
    def setUp(self):
        (self.conn, self.cursor) = DbConn().openDB(':memory:')
        self.setup = Setup(":memory:")
        self.setup.dropTables()
        self.setup.createTables()
        
    def tearDown(self):
        self.setup.dropTables()

    def test_primarykeylist_position( self ):
        keyList = _primaryKeyList( ['test1'], None, 'book')
        self.assertEqual( keyList[0], 'test1')

    def test_primarykeylist_key( self ):
        args = {'book': 'test1'}
        keyList = _primaryKeyList( ['test2'], args, 'book')
        self.assertEqual( keyList[0], 'test1' )
        
    def test_insert_genre(self):
        cursor = DbConn().cursor()
        data = ['test1','test2','test3']
        for i in range( len(data)-1, 0):
            rtn = SqlInsert( 'Genre', name=data[i])
        rtn = cursor.execute( "SELECT * FROM Genre ORDER BY id")
        idx = 0
        for row in rtn.fetchall():
            self.assertEqual( row['id'],idx+1 )
            self.assertEqual( row['name'], data[idx] )
            idx =+ 1
    
    def test_insert_genre_duplicate(self):
        cursor = DbConn().cursor()
        rtn = SqlInsert('Genre', name='test1')
        self.assertEqual( rtn, 1 )

        fault=False
        try:
            SqlInsert('Genre', name='test1')
        except:
            fault=True
        self.assertTrue(fault,"** Duplicate insert did not trigger exception")

    def test_insert_genre_ignore_duplicate(self):
        (conn,cursor) = DbConn().handles()
        for i in range(1,4):
            with self.subTest(i=i):
                name="test{}".format(i)        
                rtn = SqlInsert('Genre', name=name, ignore=False,commit=True)
                self.assertEqual( rtn , i)
        conn.commit()
        for i in range(1,4):
            with self.subTest(i=i):
                name="test{}".format(i)        
                rtn = SqlInsert('Genre', name=name, ignore=True, commit=True)
                self.assertEqual( rtn , i, name)
    
    def test_insert_no_parms(self):
        flag = False
        try:
            SqlInsert('Genre')
        except ValueError:
            flag = True
        self.assertTrue( flag , "SqlInsert did not flag for no parameters")

        try:
            SqlInsert('',key='value')
        except ValueError:
            flag = True
        self.assertTrue( flag , "SqlInsert did not flag for no table name")

    def test_forceDictionary(self):
        original = {"one":"val1"}
        addin = {"two":"val2"} 
        combined = original | addin
        dt = _forceDictionary( ["val2"], original, "two")
        self.assertEqual( dt , combined )

        dt = _forceDictionary( None , combined, "one", "two") 
        self.assertEqual( dt, combined  )
        dt = _forceDictionary( ["val1", "val2"], None, "one", "two")
        self.assertEqual( dt, combined )
        dt = _forceDictionary( ["val1", "val2"], {}, "one", "two")
        self.assertEqual( dt,combined )

        dt = _forceDictionary( ["val1", "val2", "val3"], {}, "one", "two")
        self.assertEqual( dt, combined )

        dt = _forceDictionary( [ "val2"], {}, "two", "three")
        self.assertEqual( dt, addin )

        dt = _forceDictionary( ["val1", "val2", "val3"], {}, ["one", "two"])
        self.assertEqual( dt, combined )

        dt = _forceDictionary( [ "val2"], {}, ["two", "three"])
        self.assertEqual( dt, addin )
        
    def test_generateKeys(self):
        dbkey = _generateKeys( 'Book')
        self.assertEqual( dbkey, 'book=?' )
        dbkey = _generateKeys( 'Composer')
        self.assertEqual( dbkey, 'name=?' )

    def test_generateSetValues(self):
        vals = _generateSetValues('Book', {"total_pages": 10,"last_page": 20})
        self.assertEqual( vals, 'total_pages=?,last_page=?')

    def test_generateSetValues_withKey(self):
        vals = _generateSetValues('Book', {'*book': 'newBook', "total_pages": 10,"last_page": 20})
        self.assertEqual( vals, 'book=?,total_pages=?,last_page=?')

    def test_sqlupdate(self):
        booktitle = 'title1'
        SqlInsert("Book", book=booktitle, source='source', location='loc')
        result=self.cursor.execute("SELECT * FROM Book WHERE Book.book='title1'")
        row = result.fetchone()
        self.assertEqual( row['source'], 'source')

        rtn = SqlUpdate('Book', book='title1', source='new source')
        self.assertEqual( rtn , 1 )

        result=self.cursor.execute("SELECT source FROM Book WHERE Book.book=?", [ 'title1' ] )
        row = result.fetchone()
        self.assertEqual( row['source'], 'new source')

    def test_sqlupdate_noparms(self):
        flag = False
        try:
            SqlUpdate('Book')
        except ValueError:
            flag = True
        self.assertTrue( flag , "No parms for update call.")

        flag = False
        try:
            SqlUpdate(None)
        except ValueError:
            flag = True
        self.assertTrue( flag , "No title or parms for update call.")

    def test_sqlupsert( self):
        SqlUpsert("Book", book='title1', source='source', location='loc')
        result=self.cursor.execute("SELECT id, source, location FROM Book WHERE Book.book='title1'")
        row = result.fetchone()
        self.assertEqual( row['id'], 1)
        self.assertEqual( row['source'],   'source')
        self.assertEqual( row['location'], 'loc')

        rtn = SqlUpsert('Book', book='title1', source='new source', location='new loc')
        self.assertEqual( rtn , 1 )

        result=self.cursor.execute("SELECT source, location FROM Book WHERE Book.book=?", [ 'title1' ] )
        row = result.fetchone()
        self.assertEqual( row['source'], 'new source')
        self.assertEqual( row['location'], 'new loc')

    def test_sqlupsert_record_id( self):
        rn=SqlUpsert("Book", book='title1', source='source', location='loc')
        self.assertEqual( rn, 1)
        rn=SqlUpsert("Book", book='title2', source='source', location='loc')
        self.assertEqual( rn, 2)
        rn=SqlUpsert("Book", book='title3', source='source', location='loc')
        self.assertEqual( rn, 3)
        rn=SqlUpsert("Book", book='title4', source='source', location='loc')
        self.assertEqual( rn, 4)
        rn=SqlUpsert("Book", book='title5', source='source5', location='loc5')
        self.assertEqual( rn, 5)
        result=self.cursor.execute("SELECT id, source, location FROM Book WHERE Book.book='title5'")
        row = result.fetchone()
        self.assertEqual( row['id'], 5)
        self.assertEqual( row['source'], 'source5')
        self.assertEqual( row['location'], 'loc5')

        ## Perform updates and check record numbers are correct
        rn=SqlUpsert("Book", book='title4', source='source4b', location='loc4b')
        self.assertEqual( rn, 4,'Update record 4')
        rn=SqlUpsert("Book", book='title1', source='source1b', location='loc1b')
        self.assertEqual( rn, 1, 'Update record 1')

    def test_SqlRowString(self):
        SqlUpsert("Book", book='title1', source='source', location='loc')
        result=self.cursor.execute("SELECT book, source, location FROM Book WHERE Book.book='title1'")
        self.assertEqual( SqlRowString( result) , "book='title1', source='source', location='loc'" )

    def test_SqlRowString_Empty(self):
        self.assertEqual( SqlRowString( None) , "(None)" )

    def test_getid(self):
        rn=SqlUpsert("Book", book='title1', source='source', location='loc')
        self.assertEqual( rn, 1)
        rn=SqlUpsert("Book", book='title2', source='source', location='loc')
        self.assertEqual( rn, 2)
        rn=SqlUpsert("Book", book='title3', source='source', location='loc')
        self.assertEqual( rn, 3)
        rn=SqlUpsert("Book", book='title4', source='source', location='loc')
        self.assertEqual( rn, 4)
        rn=SqlUpsert("Book", book='title5', source='source5', location='loc5')
        self.assertEqual( rn, 5)

        for i in range(1,5):
            title = "title{}".format( i )
            self.assertEqual( i, SqlGetID( 'Book', title ) )
            self.assertEqual( i , SqlGetID( 'Book', book=title ))

        self.assertRaises(ValueError, _sqlGetID, None, 'title1' )

    def test_ColumnNames(self):
        names = SqlColumnNames('Book')
        for name in ['id', 'book', 'composer_id', 'genre_id', 'source', 'location', 'version', 'layout', 'aspectRatio', 'total_pages', 'last_read', 'numbering_starts', 'numbering_ends', 'name_default', 'date_added']:
            self.assertTrue( name in names )

if __name__ == "__main__":
    unittest.main()