"""
Test frame: DbConn


 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116

#import sys
import unittest
#sys.path.append("../")

from PySide6.QtSql      import QSqlDatabase, QSqlQuery
from qdb.keys           import DbKeys
from qdb.dbconn         import DbConn

class TestDbConn( unittest.TestCase ):
    """ Test qdb.dbconn """

    @classmethod
    def setUpClass(cls):
        pass

    # def test_delete_handles( self):
    #     DbConn().open_db( close=True)

    def test_open_close(self):
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.close_db()
        self.assertFalse( DbConn.is_open() )

        db = DbConn.open_db()
        self.assertIsNotNone( db )
        self.assertTrue( DbConn.is_open() )
        self.assertEqual( DbKeys.VALUE_DEFAULT_DB_FILENAME, DbConn.name() )

    def test_clear(self):
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.clear()
        self.assertFalse( DbConn.is_open() )
        self.assertTrue( DbConn.is_clear())

    def test_bad_close(self):
        """ Test trying to close the database when it's not open"""
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.close_db()
        #pylint: disable=W0212
        DbConn._qdb_conn = None
        #pylint: enable=W0212
        DbConn.close_db()
        db = DbConn.open_db()
        self.assertIsNotNone( db )
        self.assertTrue( DbConn.is_open() )
        self.assertEqual( DbKeys.VALUE_DEFAULT_DB_FILENAME, DbConn.name(),
                         f"Filename should be {DbKeys.VALUE_DEFAULT_DB_FILENAME}")

    def test_open_close_open(self):

        sql = DbConn.open_db(':memory:')
        self.assertIsInstance( sql , QSqlDatabase )
        self.assertTrue( DbConn.is_open() )

        query = QSqlQuery( DbConn.db() )
        self.assertIsInstance( query, QSqlQuery, type(query))
        query.clear()
        query.finish()


    def test_check_dbname(self):
        DbConn.open_db(':memory:')
        self.assertEqual( DbConn.name()   , DbKeys.VALUE_DEFAULT_DB_FILENAME,
                         f'name should be {DbKeys.VALUE_DEFAULT_DB_FILENAME}')
        self.assertEqual( DbConn.dbname() , ':memory:',
                         f'DbName should be {":memory:"}')
        DbConn.destroy_connection()
        self.assertIsNone( DbConn.name() )

    def test_connecection(self):
        DbConn.close_db()
        self.assertEqual( None, DbConn.get_connection() )
        DbConn.destroy_connection()

    def test_open_close_reopen(self):
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.close_db()
        self.assertFalse( DbConn.is_open())
        DbConn.reopen_db()
        self.assertTrue( DbConn.is_open())
        DbConn.destroy_connection()

    def test_double_close(self):
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.close_db()
        self.assertFalse( DbConn.is_open())
        DbConn.close_db()
        self.assertFalse( DbConn.is_open())
        DbConn.close_db()

    def test_destroy(self):
        DbConn.open_db(':memory:')
        self.assertTrue( DbConn.is_open() )
        DbConn.close_db()
        self.assertFalse( DbConn.is_open())
        self.assertEqual( DbConn.dbname() , ':memory:')
        DbConn.destroy_connection()

    def test_cursor(self):
        DbConn.open_db(':memory:')

        self.assertTrue( DbConn.is_open() )
        self.assertTrue( DbConn.is_valid( opendb=True) )
        query = QSqlQuery( DbConn.db() )
        self.assertIsInstance( query , QSqlQuery )
        query.prepare( 'SELECT 1 AS number;')
        self.assertTrue ( query.exec() )
        self.assertTrue( query.next() )

        self.assertEqual( 1 , query.value(0))
        query.finish()
        query.clear()
        del query
