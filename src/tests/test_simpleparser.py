# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
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

import logging
import unittest
from util.simpleparse import SDOption, SDButton, SDEntry, SDEntriesMixin
from PySide6.QtWidgets import QDialogButtonBox

class TestSimpleParser(unittest.TestCase):
    OPTIONS_NOT_OPTION="type='title' label='label' options='require' "
    NOTYPE="type=''"
    BADQUOTE="type=' label='BADQUOTE'"
    ALLOPTIONS="type='title' label='BADQUOTE' option='ro ignore include require' "

    TITLE1="type='title' label='TITLE1'"
    TITLE2="type='title' label='TITLE2' tag='title2'"
    TITLE3="type='title' label='TITLE2' label='TITLE3'"
    TITLE_NOLABEL="type='title'"

    BUTTON_BLANK=  "type='button' label='BUTTON_BLANK' "
    BUTTON_ACCEPT= "type='button' label='BUTTON_ACCEPT'  value='accept'"
    BUTTON_REJECT= "type='button' label='BUTTON_REJECT'  value='reject'"
    BUTTON_BAD=    "type='button' label='BUTTON_BAD'     value='noway'"

    CHECK_TRUE=    "type='check'  label='CHECK1'         value='true'"
    CHECK_YES=     "type='check'  label='CHECK3'         value='YES'"
    CHECK_OK =     "type='check'  label='CHECK3'         value='ok'"
    CHECK_Y=      "type='check'  label='CHECK3'          value='y'"
    CHECK_CHECK=   "type='check'  label='CHECK1'         value='check'"
    CHECK_CHECKED= "type='check'  label='CHECK1'         value='checked'"
    CHECK_FALSE=   "type='check'  label='CHECK_FALSE'    value='false'"
    CHECK_NO   =   "type='check'  label='CHECK3'         value='NO'"
    CHECK_BLANK=   "type='check'  label='CHECK2'"

    CHECK_LIST_TRUE=  [ CHECK_TRUE, CHECK_YES, CHECK_OK, CHECK_Y , CHECK_CHECKED, CHECK_CHECKED]
    CHECK_LIST_FALSE= [ CHECK_FALSE, CHECK_NO , CHECK_BLANK]

    DROP_NODROP_NODATA     ="type='drop' label='DROP_EMPTY' "
    DROP_BAD_DATA          = "type='drop' label='BAD DATA' dropdown='alpha;beta;epsilong' data='a;b;c;d;e' "
    DROP_NODATA            ="type='drop' label='DROP_NODATA' dropdown='alpha;beta;epsilon' "
    DROP_NODATA_SPLIT      ="type='drop' label='DROP_SPLIT'  dropdown='alpha|beta|epsilon' split='|' "
    DROP_DROP_DATA         ="type='drop' label='DROP_DATA'   dropdown='alpha;beta;epsilon' data='a;b;c' "
    DROP_LIST_DROPONLY     = [DROP_NODATA, DROP_NODATA_SPLIT]
    DROP_VALS = [ 'alpha', 'beta', 'epsilon']

    DROP_REPLACE            ="type='drop' label='DROP_REPLACE'   dropdown='$ALPHA;$BETA;$DELTA' data='$ALPHA;$BETA;$DELTA' value='$BETA' "

    DIR_NOLABEL            = "type='dir'"
    DIR_LABEL_NOVALUE_OK   = "type='dir' label='DIR NO VALUE'"
    DIR_LABEL_VALUE_OK     = "type='dir' label='VALUE OK' value='/tmp/' "
    DIR_LABEL_OPT_OK       = "type='dir' label='VALUE_OPT' option='require ignore' "
    DIR_LIST_OK            = [ DIR_LABEL_NOVALUE_OK, DIR_LABEL_VALUE_OK, DIR_LABEL_OPT_OK ]
    

    FILE_NOLABEL            = "type='file'"
    FILE_LABEL_NOVALUE_OK   = "type='file' label='FILE NO VALUE'"
    FILE_LABEL_VALUE_OK     = "type='file' label='VALUE OK' value='/tmp/' "
    FILE_LABEL_OPT_OK       = "type='file' label='VALUE_OPT' option='require ignore' "
    FILE_LIST_OK            = [ FILE_LABEL_NOVALUE_OK, FILE_LABEL_VALUE_OK, FILE_LABEL_OPT_OK ]
    
    TEXT_NOLABEL            = "type='text' "
    TEXT_LABEL_NOVALUE_BAD  = "type='text' label='TEXT NO VALUE'"
    TEXT_LABEL_VALUE_OK     = "type='text' label='TEXT-LABEL-VALUE-OK' value='text-label-value-ok' "
    TEXT_LABEL_OPT_OK       = "type='text' label='TEXT-LABEL-OPT-OK'   value='text-label-opt-ok'  option='require ignore' "
    TEXT_LIST_OK            = [ TEXT_LABEL_VALUE_OK, TEXT_LABEL_OPT_OK ]

    ELEMENT_LIST_ONE        = [  
                                BUTTON_ACCEPT, 
                                BUTTON_REJECT, 
                                DROP_DROP_DATA, 
                                CHECK_OK, 
                                FILE_LABEL_OPT_OK,
                                TEXT_LABEL_VALUE_OK,
                                TEXT_LABEL_OPT_OK ,
                                DIR_LABEL_OPT_OK ]

    def setUp( self ):
        self.obj = SDEntry()
    
    def tearDown(self):
        self.obj.reset()

    def test_formatunique_name(self):
        pline = self.obj._parse_line( TestSimpleParser.TITLE1 )
        self.assertEqual( self.obj.format_unique_name() , 'TITLE_1' )
        self.assertEqual( pline[ SDOption.KEY_TAG ], 'TITLE_1' )
        self.assertEqual( self.obj.value( SDOption.KEY_TAG ), 'TITLE_1')

    def test_changed(self):
        self.obj._parse_line( TestSimpleParser.TITLE1 )
        self.assertFalse( self.obj.changed() )
        self.obj.set_changed( True )
        self.assertTrue( self.obj.changed() )
        self.obj.set_changed( False )
        self.assertFalse( self.obj.changed() )

    def test_options(self):
        self.obj._parse_line( TestSimpleParser.OPTIONS_NOT_OPTION )
        self.assertDictEqual( self.obj.value( SDOption.KEY_OPTIONS ) , {'require':True} )
        self.assertEqual( self.obj.value( SDOption.KEY_OPTION ), 'require')

    def test_isset(self):
        self.obj._parse_line( TestSimpleParser.FILE_LABEL_VALUE_OK )
        self.assertTrue( self.obj.is_key( SDOption.KEY_TYPE ) )
        self.assertTrue( self.obj.is_key( SDOption.KEY_LABEL ) )
        self.assertTrue( self.obj.is_key( SDOption.KEY_VALUE ) )

        self.assertTrue( self.obj.is_set( SDOption.KEY_TYPE ) )
        self.assertTrue( self.obj.is_set( SDOption.KEY_LABEL ) )
        self.assertTrue( self.obj.is_set( SDOption.KEY_VALUE ) )

        self.assertFalse( self.obj.is_set( SDOption.KEY_OPTION ) )
        self.assertFalse( self.obj.is_set( SDOption.KEY_DROP ) )
        self.assertFalse( self.obj.is_set( SDOption.KEY_DATA ) )
        self.assertFalse( self.obj.is_set( SDOption.KEY_FILTER ) )

    def test_all_options(self):
        self.obj._parse_line( TestSimpleParser.ALLOPTIONS)
        for key in [ SDOption.OPTION_IGNORE, SDOption.OPTION_INCLUDE, SDOption.OPTION_READONLY, SDOption.OPTION_REQ ]:
            self.assertTrue( self.obj.is_option( key  ) )

    def test_notype(self):
        err = False
        try:
            pline = self.obj._parse_line( TestSimpleParser.NOTYPE )
        except  Exception as rtn:
            err = True
            self.assertEqual( str( rtn ), "Invalid type: \"\" Line: \"type=''\"")
        self.assertTrue( err )
        err = False

        try:
            self.obj._parse_line( TestSimpleParser.BADQUOTE )
        except  Exception as rtn:
            err = True
            self.assertEqual( str( rtn ), "Invalid type: \"label=\" Line: \"type=' label='BADQUOTE'\"")
        self.assertTrue( err )
    
    def test_parse_title( self ):
        pline = self.obj._parse_line( TestSimpleParser.TITLE1 )
        self.assertIn( SDOption.KEY_TYPE,  pline )
        self.assertIn( SDOption.KEY_LABEL, pline )
        self.assertIn( SDOption.KEY_SEQ, pline )
        self.assertIn( SDOption.KEY_TYPE_SEQ, pline )

        self.assertEqual( pline[ SDOption.KEY_TYPE], 'title' )
        self.assertEqual( pline[ SDOption.KEY_LABEL], 'TITLE1' )
        self.assertEqual( pline[ SDOption.KEY_SEQ], 1 )
        self.assertEqual( pline[ SDOption.KEY_TYPE_SEQ], 1 )
        self.assertEqual( pline[ SDOption.KEY_TAG] , 'TITLE_1' , pline)

        pline = self.obj._parse_line( TestSimpleParser.TITLE2 )
        self.assertEqual( pline[ SDOption.KEY_TYPE], 'title' )
        self.assertEqual( pline[ SDOption.KEY_LABEL], 'TITLE2' )
        self.assertEqual( pline[ SDOption.KEY_TAG] , 'title2', pline )
        self.assertEqual( pline[ SDOption.KEY_SEQ], 2 )
        self.assertEqual( pline[ SDOption.KEY_TYPE_SEQ], 2 )

        pline = self.obj._parse_line( TestSimpleParser.TITLE3 )
        self.assertEqual( pline[ SDOption.KEY_TYPE], 'title' )
        self.assertEqual( pline[ SDOption.KEY_LABEL], 'TITLE3' )
        self.assertEqual( pline[ SDOption.KEY_TAG] , 'TITLE_3')

        with self.assertRaises( ValueError ) as cm:
            self.obj._parse_line( TestSimpleParser.TITLE_NOLABEL)
        self.assertEqual( str(cm.exception) , "Type 'title' requires a label parameter (label='')" )
            
    def test_parse_button(self):
        self.obj._parse_line( TestSimpleParser.BUTTON_BLANK , )
        self.assertTrue( self.obj.value( SDOption.KEY_LABEL) , 'BUTTON_BLANK' )
        self.assertTrue( self.obj.value( SDOption.KEY_VALUE ), 'accept')

        self.obj._parse_line( TestSimpleParser.BUTTON_ACCEPT )
        self.assertTrue( self.obj.value( SDOption.KEY_LABEL) , 'BUTTON_ACCEPT' )
        self.assertTrue( self.obj.value( SDOption.KEY_VALUE ), 'accept')

        self.obj._parse_line( TestSimpleParser.BUTTON_REJECT )
        self.assertTrue( self.obj.value( SDOption.KEY_LABEL) , 'BUTTON_REJECT' )
        self.assertTrue( self.obj.value( SDOption.KEY_VALUE ), 'reject')

        with self.assertRaises( ValueError ) as cm:
            self.obj._parse_line( TestSimpleParser.BUTTON_BAD )
        ex = cm.exception
        self.assertEqual( str(ex) , "Button 'BUTTON_BAD' can only be accept or reject not 'noway'")
        
    def test_parse_checkbox(self):
        for check in TestSimpleParser.CHECK_LIST_TRUE :
            self.obj._parse_line( check )
            self.assertTrue( self.obj.value( SDOption.KEY_VALUE ) )
        for check in TestSimpleParser.CHECK_LIST_FALSE :
            self.obj._parse_line( check )
            self.assertFalse( self.obj.value( SDOption.KEY_VALUE ) )

    def test_parse_dir(self):
        for dir in TestSimpleParser.DIR_LIST_OK:
            self.obj._parse_line( dir )
        # now recheck for values

        self.obj._parse_line( TestSimpleParser.DIR_LABEL_NOVALUE_OK )
        self.assertFalse( self.obj.is_set( SDOption.KEY_VALUE ))
        self.assertFalse( self.obj.is_set( SDOption.KEY_OPTION ))

        self.obj._parse_line( TestSimpleParser.DIR_LABEL_VALUE_OK )
        self.assertFalse( self.obj.is_set( SDOption.KEY_OPTION ))
        self.assertTrue( self.obj.is_set( SDOption.KEY_VALUE ))
        self.assertEqual( self.obj.value( SDOption.KEY_VALUE ), '/tmp/')

        self.obj._parse_line( TestSimpleParser.DIR_LABEL_OPT_OK )
        self.assertTrue( self.obj.is_set( SDOption.KEY_OPTION ))
        self.assertTrue( self.obj.is_option( SDOption.OPTION_REQ))
        self.assertFalse( self.obj.is_option( SDOption.OPTION_INCLUDE))
        self.assertFalse( self.obj.is_option( SDOption.OPTION_READONLY))
        self.assertTrue( self.obj.is_option( SDOption.OPTION_IGNORE))
        self.assertFalse( self.obj.is_set( SDOption.KEY_VALUE ))

    def test_parse_file(self):
        for dir in TestSimpleParser.FILE_LIST_OK:
            self.obj._parse_line( dir )
        # now recheck for values

        self.obj._parse_line( TestSimpleParser.FILE_LABEL_NOVALUE_OK )
        self.assertFalse( self.obj.is_set( SDOption.KEY_VALUE ))
        self.assertFalse( self.obj.is_set( SDOption.KEY_OPTION ))

        self.obj._parse_line( TestSimpleParser.FILE_LABEL_VALUE_OK )
        self.assertFalse( self.obj.is_set( SDOption.KEY_OPTION ))
        self.assertTrue( self.obj.is_set( SDOption.KEY_VALUE ))
        self.assertEqual( self.obj.value( SDOption.KEY_VALUE ), '/tmp/')

        self.obj._parse_line( TestSimpleParser.FILE_LABEL_OPT_OK )
        self.assertTrue( self.obj.is_set( SDOption.KEY_OPTION ))
        self.assertTrue( self.obj.is_option( SDOption.OPTION_REQ))
        self.assertFalse( self.obj.is_option( SDOption.OPTION_INCLUDE))
        self.assertFalse( self.obj.is_option( SDOption.OPTION_READONLY))
        self.assertTrue( self.obj.is_option( SDOption.OPTION_IGNORE))
        self.assertFalse( self.obj.is_set( SDOption.KEY_VALUE ))

    def test_parms_dropdown(self):
        for drop in TestSimpleParser.DROP_LIST_DROPONLY :
            self.obj._parse_line( drop )
            self.assertIsInstance( self.obj.value( SDOption.KEY_DROP ) , list )
            self.assertIsInstance( self.obj.value( SDOption.KEY_DATA ) , list )
            self.assertListEqual( self.obj.value( SDOption.KEY_DROP ) , TestSimpleParser.DROP_VALS )
            self.assertListEqual( self.obj.value( SDOption.KEY_DATA ) , TestSimpleParser.DROP_VALS )
        self.obj._parse_line( TestSimpleParser.DROP_DROP_DATA )
        self.assertListEqual( self.obj.value( SDOption.KEY_DROP), TestSimpleParser.DROP_VALS )
        self.assertListEqual( self.obj.value( SDOption.KEY_DATA), ['a','b','c' ])


        with self.assertRaises( ValueError ) as cm:
            self.obj._parse_line( TestSimpleParser.DROP_NODROP_NODATA )
        ex = cm.exception
        self.assertEqual( str(ex) , "Dropdown box 'DROP_EMPTY' requires keyword \"dropdown='....'\".")

        with self.assertRaises( ValueError ) as cm:
            self.obj._parse_line( TestSimpleParser.DROP_BAD_DATA )
        self.assertEqual( str(cm.exception) , "Dropdown error: 'BAD DATA' Count of option 'dropdown' 3, does not match 'data': 5")

    def test_text(self):
        for text in TestSimpleParser.TEXT_LIST_OK:
            self.obj._parse_line( text )

        self.obj._parse_line( TestSimpleParser.TEXT_LABEL_NOVALUE_BAD )

    def test_replace(self):
        self.obj._parse_line( TestSimpleParser.DROP_REPLACE )
        self.assertListEqual( self.obj.value( SDOption.KEY_DROP) , [ '$ALPHA','$BETA', '$DELTA'])
        self.assertListEqual( self.obj.value( SDOption.KEY_DATA) , [ '$ALPHA','$BETA', '$DELTA'])
        self.assertEqual( self.obj.value( SDOption.KEY_VALUE)    , '$BETA')
        self.obj.replace( {'ALPHA':'replace1', 'BETA':'replace2', 'DELTA':'replace3'} )
        self.assertListEqual( self.obj.value( SDOption.KEY_DROP) , [ 'replace1','replace2', 'replace3'])
        self.assertListEqual( self.obj.value( SDOption.KEY_DATA) , [ 'replace1','replace2', 'replace3'])
        self.assertEqual( self.obj.value( SDOption.KEY_VALUE)    , 'replace2')

    def test_tokens_call(self):
        rtn = self.obj._parse_line( TestSimpleParser.DROP_REPLACE )
        rtn2 = self.obj.tokens()
        self.assertDictEqual( rtn , rtn2 )

    def test_button_accept( self ):
        btn = SDButton()
        self.obj._parse_line( TestSimpleParser.BUTTON_ACCEPT )
        btn.setElement( self.obj )
        self.assertEqual( btn.text , 'BUTTON_ACCEPT')
        self.assertTrue( btn.isAccept() )
        self.assertFalse( btn.isReject() )

    def test_button_accept_role( self ):
        btn = SDButton()
        self.obj._parse_line( TestSimpleParser.BUTTON_ACCEPT )
        self.obj.setValue( SDOption.KEY_VALUE , QDialogButtonBox.AcceptRole )
        btn.setElement( self.obj )
        self.assertEqual( btn.text , 'BUTTON_ACCEPT')
        self.assertTrue( btn.isAccept() )
        self.assertFalse( btn.isReject() )

    def test_button_reject( self ):
        btn = SDButton()
        self.obj._parse_line( TestSimpleParser.BUTTON_REJECT )
        btn.setElement( self.obj )
        self.assertEqual( btn.text , 'BUTTON_REJECT')
        self.assertFalse( btn.isAccept() )
        self.assertTrue( btn.isReject() )

    def test_button_reject_role( self ):
        btn = SDButton()
        self.obj._parse_line( TestSimpleParser.BUTTON_REJECT )
        self.obj.setValue( SDOption.KEY_VALUE , QDialogButtonBox.RejectRole )
        btn.setElement( self.obj )
        self.assertEqual( btn.text , 'BUTTON_REJECT')
        self.assertFalse( btn.isAccept() )
        self.assertTrue( btn.isReject() )

    def test_parse_elements_find( self ):
        sdel = SDEntriesMixin()
        sdel.parse( TestSimpleParser.ELEMENT_LIST_ONE )
        find = sdel.findElements( SDOption.TYPE_TEXT )
        self.assertEqual( 2 , len(find ))
        self.assertEqual( find[0].value( SDOption.KEY_LABEL), 'TEXT-LABEL-VALUE-OK')
        self.assertEqual( find[0].value( SDOption.KEY_VALUE), 'text-label-value-ok')
        self.assertEqual( find[1].value( SDOption.KEY_LABEL), 'TEXT-LABEL-OPT-OK')
        self.assertEqual( find[1].value( SDOption.KEY_VALUE), 'text-label-opt-ok')

        find = sdel.findElements( SDOption.TYPE_DROPDOWN )
        self.assertEqual( 1 , len(find))
        self.assertListEqual( find[0].value( SDOption.KEY_DROP), TestSimpleParser.DROP_VALS )
        self.assertListEqual( find[0].value( SDOption.KEY_DATA), ['a','b','c' ])

    def test_parse_elements_placeholder(self):
        """ These just call the dummy routines """
        sdel = SDEntriesMixin()
        sdel.loadCache( None, None )
        sdel.saveCache()

    def test_parse_elements_find_buttons(self):
        sdel = SDEntriesMixin()
        sdel.parse( TestSimpleParser.ELEMENT_LIST_ONE )
        find = sdel.findButtons()
        self.assertEqual( 2 , len(find ))
        
        self.assertIsInstance( find[1] , SDButton )

        btn = find[0]
        self.assertIsInstance( btn , SDButton )
        self.assertEqual( btn.text , 'BUTTON_ACCEPT')
        self.assertTrue( btn.isAccept() )
        self.assertFalse( btn.isReject() )

        btn = find[1]
        self.assertIsInstance( btn , SDButton )
        self.assertEqual( btn.text , 'BUTTON_REJECT')
        self.assertFalse( btn.isAccept() )
        self.assertTrue( btn.isReject() )
        
    def test_parse_elements_scriptname(self):
        sdel = SDEntriesMixin()
        sdel.setScriptName( 'test1')
        self.assertEqual( 'test1', sdel.scriptName() )


