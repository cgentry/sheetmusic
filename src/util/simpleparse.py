# This Python file uses the following encoding: utf-8
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
#
#
from os import path
import re
from PySide6.QtWidgets import ( QDialogButtonBox , QPushButton)

# This module is used by the SimpleDialog class
# It contains all of the parsing routines to split up the dialog keys
# Three types of lines are entered (values surrounded by '[....]' may be optional )
#   No additional parms:        type='TYPE' label='TEXT STRING'
#   keyword parms               type='TYPE' [label='TEXT STRING'] [keyword='VALUE'] [keyword='VALUE'] ....
#   String of parms             type='TYPE' [label='TEXT STRING'] [VALUE] [VALUE] [VALUE]
#
class SDOption():
    KEY_DATA        = 'data'    # data for dropdown
    KEY_DROP        = 'dropdown' 
    KEY_FILTER      = 'filter'  # file filter
    KEY_HEIGHT      = 'height'
    KEY_LABEL       = 'label'
    KEY_OPTION      = 'option'
    KEY_SPLIT       = 'split'   # Single character seperator for parms
    KEY_TAG         = 'tag'
    KEY_TYPE        = 'type'
    KEY_VALUE       = 'value'
    KEY_WIDTH       = 'width'   # How wide to set this option

    ALT_KEY_OPTION  = 'options'

    KEY_OPTIONS     = 'optlist' # INTERNAL: split dictionary options
    KEY_RETRY       = 'retry'   # INTERNAL: where to set focus
    KEY_SEQ         = 'seq'     # INTERNAL: absolute sequence from list
    KEY_SET         = 'set'     # INTERNAL: Was input by user
    KEY_TYPE_SEQ    = 'eseq'    # INTERNAL: Type sequence

    TYPE_BUTTON      = 'button'
    TYPE_CHECK       = 'check'
    TYPE_DIR         = 'dir'
    TYPE_DIRECTORY   = 'dir'
    TYPE_DROPDOWN    = 'drop'
    TYPE_ERROR       = 'error'
    TYPE_FILE        = 'file'
    TYPE_SIZE        = 'size'
    TYPE_TEXT        = 'text'
    TYPE_TITLE       = 'title'

    # Options we understand that can be included
    # single keyword
    OPTION_IGNORE   = 'ignore'  # Allow ignore option on file/dir entries.
    OPTION_INCLUDE  = 'include' # Include in output IF value set
    OPTION_READONLY = 'ro'      # Read-only field. DON'T put this on file/dir fields
    OPTION_REQ      = 'require' # require input

    # patterns with keyword data..... 


    # Current INPUT types that we understand and accept
    LIST_TYPES       = [ TYPE_BUTTON, TYPE_CHECK , TYPE_DIR, TYPE_DROPDOWN, TYPE_ERROR, TYPE_TITLE, TYPE_FILE, TYPE_SIZE, TYPE_TEXT]

    # Fields passed to us ( KEY_.*='value' )
    LIST_INPUT      = [ KEY_DATA, KEY_DROP, KEY_FILTER, KEY_HEIGHT, KEY_LABEL, KEY_OPTION,  KEY_SPLIT, KEY_TAG, KEY_TYPE, KEY_VALUE, KEY_WIDTH ]

    # All the fields we use for internal purposes
    LIST_INTERNAL   = LIST_INPUT + [ KEY_OPTIONS , KEY_SEQ , KEY_TYPE_SEQ , KEY_SET , KEY_RETRY ]

    # The fields we return to user - subset of LIST_INTERNAL
    LIST_RETURN     = [ KEY_SEQ , KEY_TAG , KEY_VALUE , KEY_TYPE, KEY_SET ]

    # The TYPES we return to user - subset of LIST_TYPES
    LIST_TYPES_RTN  = [ TYPE_FILE , TYPE_DIR ,TYPE_TEXT , TYPE_CHECK, TYPE_DROPDOWN ]

    # Types that require a label field
    LIST_TYPES_LBL  =   [ TYPE_FILE , TYPE_DIR ,TYPE_TEXT , TYPE_BUTTON, TYPE_CHECK, TYPE_DROPDOWN , TYPE_TITLE ]

    LIST_SINGLE_OPTIONS = [ OPTION_REQ , OPTION_INCLUDE , OPTION_IGNORE,  OPTION_READONLY ]

class SDEntry( ):
    REGEX_KEYWORDS         = None
    REGEX_SINGLE_OPTION    = None
    REGEX_MULTI_OPTION     = None
    type_counter           = None
    line_counter           = 0
    DEFAULT_SPLIT          = ';'
    SINGLE_OPTION_SPLIT    = '|'

    def __init__( self ):
        if SDEntry.REGEX_KEYWORDS is None:
            self._init_regex()
        if SDEntry.type_counter is None:
            self.reset()
        
    def reset( self )->None:
        """ Clear any counters that are class level """
        SDEntry.type_counter = dict( zip( SDOption.LIST_TYPES , [0]*len(SDOption.LIST_TYPES) ) )
        SDEntry.line_counter = 0

    def _init_regex(self)->None:
        """
        Compile the regular expressions to run parsing just a wee bit faster

        REGEX_KEYWORD       will match all the input keywords (type='file' , type='dir', etc)
        REGEX_SINGLE_OPTION will match all the single keyword options: require include ignore...
        REGEX_    
        """
        type_match='|'.join( SDOption.LIST_INPUT + [ SDOption.ALT_KEY_OPTION])
        self.regex_keywords = r"\s*({})\s*=\s*'\s*([^']*)\s*'\s*".format( type_match)
        SDEntry.REGEX_KEYWORDS = re.compile( self.regex_keywords )

        single_match='|'.join( SDOption.LIST_SINGLE_OPTIONS )
        SDEntry.REGEX_SINGLE_OPTION=r"\s*({})\s*[{}]?".format( single_match  , SDEntry.SINGLE_OPTION_SPLIT)

    def format_unique_name( self )->str:
        """ 
        Generate a unique name for this object: TAG_SEQ

        The TAG will be forced to upper case, also suitable for shell scripts
        """
        return self.value( SDOption.KEY_TAG )
    
    def _init_token_dictionary( self )->None:
        self._tokens = dict( zip( SDOption.LIST_INTERNAL , ['']*len(SDOption.LIST_INTERNAL)))
        self._tokens[ SDOption.KEY_OPTIONS] = None
        self._tokens[ SDOption.KEY_SPLIT] = self.DEFAULT_SPLIT
        self._tokens[ SDOption.KEY_RETRY] = False
        self._tokens[ SDOption.KEY_SET ]  = False
    
    def _parse_keywords(self  , input_line:str )->None:
        """ Find all the key entries: key='value' and key='muti-value|multi-value' """

        key_values = re.findall(SDEntry.REGEX_KEYWORDS, input_line)
        for key_value in key_values :
            key = key_value[0].strip()
            if key == SDOption.ALT_KEY_OPTION :
                key = SDOption.KEY_OPTION
            self._tokens[ key ] = key_value[1].strip()

        # Split 'option' into 'options' dictionary
        self._tokens[ SDOption.KEY_OPTIONS] = {}
        if self.is_set( SDOption.KEY_OPTION ):
            option = self.value( SDOption.KEY_OPTION )
            single_list = re.findall( SDEntry.REGEX_SINGLE_OPTION , input_line ) 

            for key in single_list:
                self._tokens[ SDOption.KEY_OPTIONS ][key.strip()] = True
    
    def _require_label(self )->None:
        if not self.is_set( SDOption.KEY_LABEL ):
            raise ValueError("Type '{}' requires a label parameter (label='')".format( self.value( SDOption.KEY_TYPE )) )
        
    def _set_tag(self)->None:
        if not self.is_set( SDOption.KEY_TAG ):
            new_tag = "{}_{}".format( 
                self.value( SDOption.KEY_TYPE ).upper() , 
                self.value( SDOption.KEY_TYPE_SEQ ))
            self.setValue(SDOption.KEY_TAG , new_tag )

    def _check_field_button(self)->None:
        self._require_label()
        if not self.is_set( SDOption.KEY_VALUE ):
            self.setValue( SDOption.KEY_VALUE , 'accept')
        elif self.value( SDOption.KEY_VALUE ) not in ['accept', 'reject']:
            raise ValueError("Button '{}' can only be accept or reject not '{}'".format(
                self.value( SDOption.KEY_LABEL ) , self.value( SDOption.KEY_VALUE )
            ))

    def _check_field_box( self )->None:
        """ Enure we have a label and that the value is set to a boolean depending on string"""
        self._require_label()
        self.setValue( SDOption.KEY_VALUE, self.value( SDOption.KEY_VALUE).lower() in [ '1', 'check', 'checked', 'true', 'yes', 'y', 'ok'] )

    def _check_field_dir( self )->None:
        self._require_label()

    def _check_field_dropdown(self)->None:
        """
        Dropdown combobox will always have a selected value, either from value or the first entry

        KEYWORDS:   split       Single character used to split values in dropdown or data
                                (default is ;)
                    dropdown    has a list of values to be displayed in the dropdown box
                    data        list of return values for each item in dropdown. 
                                If nothing specified, the values in dropdown are used
        
        """
        self._require_label()
        
        if not self.is_set( SDOption.KEY_DROP ):
            raise ValueError("Dropdown box '{}' requires keyword \"dropdown='....'\".".format( 
                self.value( SDOption.KEY_LABEL ) ,
                self.value( SDOption.KEY_SEQ )))
        
        value = self._split_value( SDOption.KEY_DROP  )
        self.setValue( SDOption.KEY_DROP , value )

        if self.is_set( SDOption.KEY_DATA ):
            self.setValue( SDOption.KEY_DATA , self._split_value( SDOption.KEY_DATA ) )
        else:
            self.setValue( SDOption.KEY_DATA , self.value( SDOption.KEY_DROP ))

        if not self.is_set( SDOption.KEY_VALUE ):
            self.setValue( SDOption.KEY_VALUE , value[0]) 

        if len( self.value( SDOption.KEY_DATA)) != len( self.value( SDOption.KEY_DROP ) ):
            raise ValueError("Dropdown error: '{}' Count of option 'dropdown' {}, does not match 'data': {}".format( 
                self.value( SDOption.KEY_LABEL), len( self.value( SDOption.KEY_DROP)),  len( self.value( SDOption.KEY_DATA) ) ))
        pass

    def _check_field_file(self)->None:
        self._require_label()
        pass

    def _check_field_text(self)->None:
        self._require_label()
        pass

    def _check_field_title(self)->None:
        self._require_label()
        
    def setValue( self, key:str, value)->None:
        self._tokens[ key ] = value

    def set_changed( self, flag:bool=True)->None:
        self.setValue( SDOption.KEY_SET , flag )

    def changed( self )->None:
        return self.value( SDOption.KEY_SET)
    
    def is_key( self, key:str )->bool:
        """ Determine if the key is within this parsed entry """
        return key in self._tokens
    
    def is_set( self, key:str )->bool: 
        """ Determine if the key is within this parsed entry, and is set """
        return key in self._tokens and self._tokens[ key ] != '' and self._tokens[key] is not None 
    
    def is_type( self, key_type:str)->bool:
        """ Check to see if this entry is of type 'key_type"""
        return self._tokens[ SDOption.KEY_TYPE] == key_type

    def value( self, key:str, default='')->str:
        """ Return the value for a parsed entry or, if not set, return default """
        if self.is_set( key ):
            return self._tokens[key]
        return default
    
    def _split_value( self, key:str ,default:str=""  )->list:
        """split the keyed string up by the value 'split """

        value     = self.value( key ,default )
        delimiter = self.value( SDOption.KEY_SPLIT , self.DEFAULT_SPLIT)
        split_list = value.split( delimiter )
        return [ value.strip() for value in split_list ]

    def is_option( self, key:str )->bool:
        """ Return if the key is within the options"""
        return key in self._tokens[ SDOption.KEY_OPTIONS ]
                                                                   
    def _set_sequence( self )->None:
        """ Keep a sequence counter for each type and 'brand' that into this token dictionary """
        SDEntry.type_counter[ self.value( SDOption.KEY_TYPE ) ] +=1
        SDEntry.line_counter += 1
        
        self.setValue( SDOption.KEY_SEQ      , SDEntry.line_counter )
        self.setValue( SDOption.KEY_TYPE_SEQ , SDEntry.type_counter[ self.value( SDOption.KEY_TYPE ) ] ) 

    def replace( self , keywords:dict )->None:
        """ Replace all the occurances of a keyword in value, data and drop."""
        if isinstance( keywords, dict ):
            for key, word in keywords.items():
                key = '$' + key 

                value = self._tokens[ SDOption.KEY_VALUE ]
                if isinstance( value , str ) and key in value:
                    self._tokens[ SDOption.KEY_VALUE ] = value.replace( key , word  ) 

                if self.is_type( SDOption.TYPE_DROPDOWN ):
                    for index, entry in enumerate( self.value( SDOption.KEY_DROP ) ):
                        if key in entry:
                            self._tokens[ SDOption.KEY_DROP ][index] = entry.replace( key, word )
                    for index, entry in enumerate( self.value( SDOption.KEY_DATA ) ):
                        if entry == key:
                            self._tokens[ SDOption.KEY_DATA ][index] = entry.replace( key, word )

    def _parse_line( self , line_input:str , line_number:int=0 )->dict:
        """
        Split all the values into a list of dictionary entries.
        
        The TAG field will be returned as passed in or, if blank, a new name of 'type'_'count' will be created.
        If you pass a list of keywords, they should be 'key':'value'. These will replace values in the ALUE field
        """

        self._init_token_dictionary()
        self._parse_keywords( line_input )
        if   self.is_type( SDOption.TYPE_BUTTON ):
            self._check_field_button()
        elif self.is_type(  SDOption.TYPE_CHECK )   : 
            self._check_field_box()
        elif self.is_type(SDOption.TYPE_DIR):
            self._check_field_dir()   
        elif self.is_type(SDOption.TYPE_DROPDOWN ):
            self._check_field_dropdown() 
        elif self.is_type(SDOption.TYPE_FILE ):
            self._check_field_file()
        elif self.is_type( SDOption.TYPE_TEXT):
            self._check_field_text()
        elif self.is_type( SDOption.TYPE_TITLE ):
            self._check_field_title()
        elif self.is_type( SDOption.TYPE_SIZE ):
            pass
        else:
            raise ValueError('Invalid type: "{}" Line: "{}"'.format( self.value( SDOption.KEY_TYPE), line_input ))
        
        self._set_sequence()
        self._set_tag()
        return self._tokens
    
    def tokens(self)->dict:
        """ 
        return the dictionary with all tokens.
        
        This isn't strictly needed. If you keep the class, you have the access routines
        """

        return self._tokens

class SDEntriesMixin():
    """ Read and generate a list of tokens """

    def setupElements(self):
        self.elements = []
        self._keywords  = {}
        if not hasattr( self, 'filename'):
            self.filename = None
        if not hasattr( self, '_script'):
            self.filename = None

    def loadCache( self, parse_file:str, keywords:dict=None)->list:
        """ Load cache file if it exists otherwise load file """
        return self.parseFile( parse_file, keywords)

    def saveCache( self ):
        pass

    def findElements( self, token_type:str )->list:
        """ Search out and return all of the elements that are type 'ktoken_typeey' """
        rtn_list = []
        for element in self.elements:
            if element.value( SDOption.KEY_TYPE ) == token_type:
                rtn_list.append( element )
        return rtn_list

    def findButtons( self )->list:
        """ Find all the button definitions that parsed and return a list of SDButton"""
        self.buttons = []
        button_list = self.findElements(  SDOption.TYPE_BUTTON )

        for button in button_list:
            newButton = SDButton( )
            newButton.setElement( button )
            self.buttons.append( newButton )
        return self.buttons

    def setScriptName(self, name:str):
        self._script = name 

    def scriptName(self)->str:
        return self._script

    def setRetry( self, element:SDEntry, obj )->None:
        element.setValue( SDOption.KEY_RETRY , obj )

    def parse( self, parse_list:list , keywords:dict=None )->list:
        """ Parse the list passed by calling SDEntry on each line. """
        self.setupElements()
        self.setKeywords( keywords )
        for line in parse_list:
            parser = SDEntry()
            parser._parse_line( line )
            self.elements.append( parser )
        return self.elements
    
    def parseFile( self, parse_file:str, keywords:dict=None)->list:
        if parse_file is None:
            self.setupElements()
            return self.elements

        self.filename = parse_file
        with open( parse_file , 'r') as f :
            parse_list = f.readlines()
        return self.parse( parse_list , keywords )
    
    def setKeywords( self , keywords:dict )->None:
        """ 
            This will setup for keyword replacment. 
            
            Can be passed when parsing or later. 
            If saving, call after a save() request is made and after a load() is done
        """
        if not isinstance( keywords, dict ) and keywords is not None:
            raise RuntimeError("Keyword type '{}' not valid. Must be a dictionary or None".format( type( keywords)))
        self._keywords = keywords

    def keywords(self)->dict:
        if not hasattr( self, '_keywords'):
            self._keywords = {}
        return self._keywords

    def replace_keywords(self):
        """ Goes through all the keywords in the list and issues a replacement in each element """
        kwords = self.keywords()
        for element in self.elements:
            element.replace( kwords )
    
class SDButton():
    """This handles button genration and insertion into a DialogButtonBox

        Note that buttons are currently only in the translate role and can't
        be anything else
    """
    translate_role = {
        'accept': QDialogButtonBox.AcceptRole,
        'reject': QDialogButtonBox.RejectRole,
    }
    def __init__(self)->None:
        self._text = ''
        self._role = QDialogButtonBox.RejectRole

    def setElement(self, tokens:SDEntry )->None:
        self.setButton( tokens.value( SDOption.KEY_LABEL ) , tokens.value( SDOption.KEY_VALUE ) )

    def setButton(self , text:str, role )->None:
        """ Setup the button text and role. Translates roles from 'accept', 'reject'"""
        self._text = text

        if isinstance( role , str ):
            if role in SDButton.translate_role:
                self._role = SDButton.translate_role[ role.lower() ]
        elif isinstance( role , QDialogButtonBox.ButtonRole ):
            self._role = role

    def isAccept(self)->bool:
        return self._role == QDialogButtonBox.AcceptRole
    
    def isReject(self)->bool:
        return self._role == QDialogButtonBox.RejectRole
    
    def text( self )->str:
        return self._text
    
    def role(self)->QDialogButtonBox.ButtonRole:
        return self._role
