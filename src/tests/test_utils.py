"""
Test frame: Utils

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#ignore too many methods, missing doc strings
#pylint: disable=C0115
#pylint: disable=C0116
#pylint: disable=R0904

import unittest

from util.convert import to_int, to_bool

class TestUtils( unittest.TestCase):

    def test_toint_with_numeric_characters( self ):
        self.assertEqual( to_int(""), 0 )
        for i in range( -10,10,1):
            int_string = str( i )
            self.assertEqual( to_int( int_string ), i)
        self.assertEqual( to_int("10"), 10)
        self.assertEqual( to_int("-10"), -10 )

        x = float(.5)
        self.assertEqual( to_int(x,default=10), 0 )

    def test_toint_with_alphabetic_characters( self ):

        self.assertEqual( to_int("abc"), 0 )
        self.assertEqual( to_int("$10"), 0)
        self.assertRaises( ValueError,
                to_int, 'abc', ignore=False )
        self.assertRaises( ValueError,
                to_int,'$10', ignore=False)


    def test_toint_bool(self):
        self.assertEqual( 1 ,
            to_int( True, ignore=False) )

    def test_toint_with_none(self):
        self.assertEqual( to_int(None), 0 )

    def test_toint_with_integers(self):
        for i in range(-10,10,1 ):
            self.assertEqual( to_int(i), i )

    def test_toint_with_floats(self):
        self.assertEqual( to_int(10.5), 10 )

    def test_to_bool(self):
        self.assertTrue( to_bool(1))
        self.assertTrue( to_bool( 'yes'))
        self.assertTrue( to_bool( 'true'))
        self.assertTrue( to_bool( 't'))
        self.assertTrue( to_bool( 'ok'))
        self.assertTrue( to_bool( True))

        self.assertFalse( to_bool('no'))
        self.assertFalse( to_bool( False))
        self.assertFalse( to_bool( 0 ))
        self.assertFalse( to_bool(None))

if __name__ == "__main__":
    unittest.main()
