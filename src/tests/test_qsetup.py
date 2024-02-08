"""
Test frame: Setup

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#pylint: disable=C0115
#pylint: disable=C0116
import unittest
import os.path

from PySide6.QtSql import QSqlQuery

from qdb.dbconn import DbConn
from qdb.setup import Setup
from qdb.keys import DbKeys



class TestSetup(unittest.TestCase):
    sql_get_tablenames = """
            SELECT count(*)
            FROM sqlite_schema
            WHERE type ='table'
            AND name NOT LIKE 'sqlite_%';"""
    sql_get_viewnames = """
            SELECT count(*)
            FROM sqlite_schema
            WHERE type ='view'
            AND name NOT LIKE 'sqlite_%';"""

    sql_get_genre = """
            SELECT id, name
            FROM Genre
            ORDER BY id ASC
            """
    sql_get_composer = """
            SELECT id, name
            FROM Composer
            ORDER BY id ASC
            """
    sql_count_composer = """SELECT COUNT(*) FROM Composer"""

    sql_get_system = """
            SELECT key, value
            FROM System
            ORDER BY key
        """

    def setUp(self):
        db = DbConn().open_db(':memory:')
        self.setup = Setup(":memory:")
        self.setup.drop_tables()
        self.query = QSqlQuery(db)

    def test_create_tables(self):
        self.assertTrue(self.query.exec(self.sql_get_tablenames))
        self.assertTrue(self.query.next())
        self.assertEqual(0, self.query.value(0))
        self.query.finish()

        self.assertTrue(self.query.exec(self.sql_get_viewnames))
        self.query.next()
        self.assertEqual(0, self.query.value(0))
        self.query.finish()

        self.setup.create_tables()

        self.assertTrue(self.query.exec(self.sql_get_viewnames))
        self.query.next()
        self.assertEqual(3, self.query.value(0), "Number of views")
        self.query.finish()

        self.assertTrue(self.query.exec(self.sql_get_tablenames))
        self.query.next()
        self.assertEqual(8, self.query.value(0))
        self.query.finish()

    def test_drop_tables(self):
        self.setup.create_tables()
        self.setup.drop_tables()

        self.assertTrue(self.query.exec(self.sql_get_tablenames))
        self.assertTrue(self.query.next())
        self.assertEqual(0, self.query.value(0), 'Number of tables')
        self.query.finish()

        self.assertTrue(self.query.exec(self.sql_get_viewnames))
        self.query.next()
        self.assertEqual(0, self.query.value(0), 'Number of views')
        self.query.finish()

    def test_init_genre(self):
        self.setup.create_tables()
        self.assertTrue(self.setup.init_genre())
        self.assertTrue(self.query.exec(self.sql_get_genre))

        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 1)
        self.assertEqual(self.query.value(1), 'Unknown')

        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 2)
        self.assertEqual(self.query.value(1), 'Various')

        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 3)
        self.assertEqual(self.query.value(1), 'Teaching')

        self.query.finish()

        self.assertFalse(self.setup.init_genre())

    def test_init_composers(self):
        self.setup.create_tables()
        self.assertTrue(self.setup.init_composer())

        self.assertTrue(self.query.exec(self.sql_count_composer))
        self.assertTrue(self.query.next())
        self.assertGreaterEqual(self.query.value(0),40)
        self.query.finish()

        self.assertTrue(self.query.exec(self.sql_get_composer))
        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 1)
        self.assertEqual(self.query.value(1), 'Unknown')

        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 2)
        self.assertEqual(self.query.value(1), 'Various')

        self.assertTrue(self.query.next())
        self.assertEqual(self.query.value(0), 3)
        self.assertEqual(self.query.value(1), 'Teaching')

        self.query.finish()

        self.assertFalse(self.setup.init_composer())

    def test_init_data(self):
        self.setup.create_tables()
        self.setup.init_data()

        self.assertTrue(self.query.exec(self.sql_get_system))
        rows = {}
        while self.query.next():
            rows[self.query.value(0)] = self.query.value(1)

        self.assertGreaterEqual(
            len(rows), 14, "System should have at least 14 entries")

        self.assertEqual(
            rows[DbKeys.SETTING_DEFAULT_IMGFORMAT], DbKeys.VALUE_GSDEVICE)
        self.assertEqual(rows[DbKeys.SETTING_PAGE_LAYOUT],
                         DbKeys.VALUE_PAGES_SINGLE)
        # , DbKeys.VALUE_REOPEN_LAST )
        self.assertTrue(rows[DbKeys.SETTING_LAST_BOOK_REOPEN])
        self.assertEqual(rows[DbKeys.SETTING_FILE_TYPE],
                         DbKeys.VALUE_FILE_TYPE)
        self.assertEqual(
            rows[DbKeys.SETTING_DEFAULT_SCRIPT], os.environ['SHELL'])
        self.assertEqual(
            rows[DbKeys.SETTING_DEFAULT_SCRIPT_VAR], DbKeys.VALUE_SCRIPT_VAR)
