# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from config import Config

class dummyPref():
    """
    Dummy class for testing fallback to QSetting
    """
    def __init__(self):
        self.data = {}
    
    def set( self, key, value ):
        self.data[key] = value

    def clear(self):
        self.data.clear()

    def contains(self, key ):
        return key in self.data

    def value(self, key , value=None):
        if key in self.data:
            return self.data[key]
        return value

    

class TestConfig( unittest.TestCase): 
    @classmethod
    def setUpClass(self):
        self.pref = dummyPref()

    def test_pref(self):
        """ just a simple test to make sure pref works correctly """
        self.pref.clear()
        self.pref.set( 'key','data')
        self.assertEqual( self.pref.value( 'key',value='notfound'),'data')
        self.assertEqual( self.pref.value('nokey',value='notfound'), 'notfound')
        self.pref.clear()
        self.assertIsNone( self.pref.value( 'key'))


    def test_getConfig(self):
        self.pref.clear()
        cfg = Config(self.pref)
        cfg.read_string( sampleData )
        self.assertEqual(cfg.getConfig('key-1'), '10')
        self.assertEqual(cfg.getConfig('key-1','section-1'), '10')

        self.assertEqual(cfg.getConfig('value-1','section-3') , '30')
        self.assertEqual(cfg.getConfig('notreal','section-3', '?'), '?' )

    def test_setConfig(self):
        self.pref.clear()
        cfg=Config(self.pref)
        cfg.setConfig("key1", 10)
        cfg.setConfig("key2", 20, "section1")

        self.assertEqual(cfg.getConfig('key1'), '10')
        self.assertEqual(cfg.getConfig('key2', 'section1'), '20')
        

    def test_getConfigInt(self):
        self.pref.clear()
        self.pref.set('fallback','42')
        cfg=Config(self.pref)
        cfg.setConfig("key1", 10)
        cfg.setConfig("key2", 20, "section1")

        self.assertEqual(cfg.getConfigInt('key1'), 10)
        self.assertEqual(cfg.getConfigInt('key2', 'section1'), 20)

        self.assertEqual(cfg.getConfigInt( 'fallback' ), 42 )
        self.assertEqual(cfg.getConfigInt( 'fallback', fallback=False) , 0)

    def test_sectionsSorted(self):
        self.pref.clear()
        self.pref.set('fallback','44')
        cfg = Config(self.pref)
        cfg.read_string( sampleData )
        sections = cfg.sectionsSorted()
        for i in range(0,len(sections)-1):
            name = "section-{:d}".format(i+1)
            self.assertEqual(sections[i], name )
        self.assertEqual(cfg.getConfig( 'fallback' ), '44' )
        self.assertIsNone(cfg.getConfig( 'fallback', fallback=False) )
    
    def test_pformat(self):
        self.pref.clear()
        cfg = Config(self.pref)
        cfg.read_string( sampleData )
        self.assertEqual( pprint_output, cfg.pformat())
    
    def test_pformat_nodefault(self):
        self.pref.clear()
        cfg = Config( self.pref)
        cfg.read_string("[section-2]\nkey-1=10\n[section-1]\nkey-2=20\n")
        self.assertEqual(pnodefault_output, cfg.pformat() )

    def test_fallback_to_pref(self):
        self.pref.clear()
        self.pref.set('only-pref','only-value')
        cfg = Config(self.pref)
        cfg.read_string(sampleData )
        self.assertEqual( cfg.getConfig("only-pref","section-3"), "only-value")
        self.assertEqual( cfg.getConfig("only-pref",None), "only-value")
        self.assertEqual( cfg.getConfig("only-pref"), "only-value")
        self.assertEqual( cfg.getConfig("only-pref",'DEFAULT'), "only-value")
        self.assertEqual( cfg.getConfig("only-pref",value='novalue',fallback=False), "novalue")

    def test_fallback_to_default(self):
        self.pref.clear()
        cfg = Config(self.pref)
        cfg.read_string(sampleData )
        self.assertEqual( cfg.getConfig("key-1","section-1",value=99), '10')
        self.assertEqual( cfg.getConfigInt("key-1","section-1",value=99), 10)



pnodefault_output="""[section-2]:
	[key-1]: 10
[section-1]:
	[key-2]: 20
"""
sampleData = """#
[DEFAULT]
key-1 = 10
key-2 = 20

[section-3]
value-1 = 30

[section-1]
value-1 = 40

[section-2]

[section-4]
"""

pprint_output = """DEFAULT:
key-1: 10
key-2: 20
[section-3]:
	[value-1]: 30
	[key-1]: 10
	[key-2]: 20
[section-1]:
	[value-1]: 40
	[key-1]: 10
	[key-2]: 20
[section-2]:
	[key-1]: 10
	[key-2]: 20
[section-4]:
	[key-1]: 10
	[key-2]: 20
"""