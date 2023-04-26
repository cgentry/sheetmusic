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

import re
import os
from PySide6.QtCore import Qt
from PySide6.QtGui  import QIntValidator, QValidator
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit, QMessageBox,
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton , QCheckBox)

from qdb.keys         import BOOK, DbKeys
from qdb.mixin.fieldcleanup import MixinFieldCleanup
from ui.editItem      import UiGenericCombo
from qdb.dbbook       import DbComposer, DbGenre
from qdil.preferences import DilPreferences
from qdb.dbsystem     import DbSystem
from qdb.dbbooksettings import DbBookSettings
from util.convert     import toInt

class simpleValidator( QValidator ):
    badChars = r'[?%\\|/\n\t\r]+'

    def __init__(self):
        super().__init__();

    def validate(self, arg1:str, arg2 ):
        if len( arg1.strip() ) == 0 :
            return QValidator.Invalid
        if re.search( self.badChars , arg1 ) or arg1.startswith(' '):
            return QValidator.Invalid
        return QValidator.Acceptable

class UiProperties(MixinFieldCleanup, QDialog):
    '''
    This creates a simple grid and populates it with info from the Book
    Changes can be made and data will be returned if a change is made.
    '''
    bpData = 0
    bpLabel = 1

    btnTxtIgnore = u'Continue With No Changes'
    btnTxtCancel = u'Cancel'
    btnTxtApply  = u'Apply Changes and Continue'

    pdf_options = {'Use System Setting' : None,  'Image conversion': False, 'PDF Page render': True}
    pdf_values  = {None: 'Use System Setting',  '0': 'Image conversion', '1': 'PDF Page render'}

    staticBookInformation = [
        [ BOOK.location,     'Book location'],
        [ BOOK.totalPages,   'Total pages'],
        [ BOOK.source,       'Original book source'],
        [ BOOK.dateAdded,    'Date added'],
        [ BOOK.pdfCreated,   'PDF Creation date'],
        [ BOOK.fileCreated,  'File date created'],
        [ BOOK.fileModified, 'File date modified'],
    ]
    def __init__(self, properties:dict=None,parent=None):
        super().__init__(parent)
        self.dbbooksettings = DbBookSettings()
        self.createPropertiesTable()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.propertiesTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.cleanupLevel = DilPreferences().getValueInt( DbKeys.SETTING_NAME_IMPORT, DbKeys.VALUE_NAME_IMPORT_FILE_0 )
        self.resize(700, 500)
        if properties:
            self.set_properties( properties )

    def clear(self):
        """ clear will remove all content from the QTable and reset counters"""
        self.propertiesTable.clear()
        self.propertiesTable.horizontalHeader().hide()
        self.selectedProperty = None
        self.selectedPage = None
        self.propertiesTable.setRowCount(0)
        self.changes = {}
        self.flagChanged = False
        self.defaultButton()

    def createPropertiesTable(self):
        self.propertiesTable = QTableWidget()
        self.propertiesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.propertiesTable.setColumnCount(1)
        self.propertiesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.propertiesTable.setShowGrid(True)
        self.propertiesTable.setDisabled( False )
    
    def add_buttons(self)->None:
        """ OVERRIDE: Add additional buttons here. """
        pass

    def createButtons(self):
        self.btn_skip = QPushButton( self.btnTxtIgnore )
        self.btn_apply = QPushButton( self.btnTxtApply )
        self.btn_cancel = QPushButton( self.btnTxtCancel)
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.btn_skip, QDialogButtonBox.ResetRole)
        self.buttons.addButton( self.btn_apply, QDialogButtonBox.YesRole)
        self.buttons.addButton( self.btn_cancel , QDialogButtonBox.RejectRole)
        self.buttons.clicked.connect(self.button_clicked)
        self.add_buttons()
    
    def button_default_action( self, btn ):
        """ OVERRRIDE: To extend button actions on 'clicked', override and check btn.text """
        self.accept()

    def button_clicked(self, btn ):
        if btn.text() == self.btnTxtIgnore:
            self.changes={}
            self.accept()
        elif btn.text() == self.btnTxtCancel:
            self.changes={}
            self.reject()
        else:
            self.button_default_action( btn )
    
    def isReject(self)->bool:
        return (self.result() == self.DialogCode.Rejected )
    
    def isSkip(self)->bool:
        return( self.result()==self.DialogCode.Accepted and len(self.changes) == 0 )

    def isApply( self )->bool:
        return( self.result()==self.DialogCode.Accepted and len(self.changes) > 0 )

    def _format_static_property(self, label:str, itemValue, isMutable:bool):
        headerW = QTableWidgetItem( str( label ))
        pageW   = QTableWidgetItem( str(itemValue)) 
        if isMutable:  
            pageW.setFlags(  Qt.ItemIsEditable|Qt.ItemIsEnabled)
        else:
            pageW.setFlags(Qt.NoItemFlags)
        return ( headerW, pageW )

    def _insertPropertyEntry(self, property ):
        ''' Insert a row into the book's property table
        
        Pass in a list of values: name and property value'''
        row = self.propertiesTable.rowCount()
        self.propertiesTable.insertRow(row)
        self.propertiesTable.setVerticalHeaderItem( row , property[0] )
        if isinstance( property[1] ,  QTableWidgetItem ):
            self.propertiesTable.setItem(row, 0, property[1])
        else:
            self.propertiesTable.setCellWidget( row, 0, property[1])

    def defaultButton(self):
        """ If there are changes, activate buttons """
        apply = (len( self.changes ) > 0 )
        self.btn_apply.setDefault(apply)
        self.btn_apply.setEnabled( apply )
        self.btn_skip.setDefault( ( not apply ) )

    def changedName(self, value):
        self.changes[ BOOK.name ] = self.clean_field_value( value )
        self.defaultButton()

    def validatePage( self, value )->bool:
        value = value.strip()
        i = toInt( value, -1)
        if value == '' or (i >= 0 and i <= 999):
            return True
        QMessageBox.warning( self, 'Invalid Value', 'Page number must be 0 to 999')
        return False

    def changedStart( self, value ):
        if self.validatePage( value ):
            self.changes[ BOOK.numberStarts] = toInt(value,0 )
            self.defaultButton()

    def changedEnd( self, value ):
        if self.validatePage( value ):
            self.changes[ BOOK.numberEnds] = toInt(value,0 )
            self.defaultButton()

    def changedLink( self, value ):
        self.changes[ BOOK.link ] = value.strip()
        self.defaultButton()

    def changedAuthor( self, value ):
        self.changes[ BOOK.author ] = value.strip()
        self.defaultButton()
        
    def changedComposer(self, value):
        self.changes[ BOOK.composer ] = value.strip()
        self.defaultButton()

    def changedGenre( self, value ):
        self.changes[ BOOK.genre ] = value.strip()
        self.defaultButton()

    def changeRender( self, value ):
        value = value.strip()
        self.changes[ DbKeys.SETTING_RENDER_PDF ] = UiProperties.pdf_options.get( value )
        self.defaultButton()

    def _nameProperty( self , label:str, musicbook:dict , valueKey:str, onChange, isInt:bool=False , cleanup:bool=True, readonly:bool=False):
        name = QLineEdit()
        if isInt:
            value = str(musicbook[valueKey] if valueKey in musicbook else 1)
        else:
            if valueKey not in musicbook or musicbook[ valueKey ] is None:
                musicbook[ valueKey ] = ''
                value = ''
            else:
                if cleanup:
                    value = self.clean_field_value( str(musicbook[valueKey]) )
                else:
                    value = self.remove_ctrl_char( str( musicbook[ valueKey ]) )
        name.setText( value )
        if isInt:
            name.setValidator( QIntValidator( 0, 999, self ) )
        else:
            name.setValidator( simpleValidator() )
        name.setReadOnly( readonly )
        name.setObjectName( valueKey )
        name.textEdited.connect( onChange )
        self._insertPropertyEntry( [QTableWidgetItem( label ) , name] )

    def _comboPropertyValue( self, label:str, datasource,  currentEntry, changeFunction ):
        """ Create a combo (dropdown) option list based on a db entry and list"""
        combo = UiGenericCombo( True, datasource, currentEntry, label )
        combo.currentTextChanged.connect( changeFunction )
        self._insertPropertyEntry( [ QTableWidgetItem( label ) , combo ])
        
    def _comboProperty( self, label:str, dbentry,  musicbook:dict, valueKey:str, changeFunction ):
        """ Create a combo (dropdown) option list based on a db entry and list"""
        currentEntry = ( str(musicbook[valueKey] ) if valueKey in musicbook else 'Unknown' )
        self._comboPropertyValue( label, dbentry, currentEntry, changeFunction )
    
    def _checkboxProperty( self, label:str, ischecked:bool, checkedFunction ):
        cbox = QCheckBox()
        cbox.setText( label )
        cbox.setCheckable(True)
        cbox.setChecked( ischecked )
        cbox.stateChanged.connect( checkedFunction )
        self._insertPropertyEntry( [QTableWidgetItem( ''), cbox ])

    def add_additional_properties(self)->None:
        """ OVERRIDE: To extend the editable rows, use this hook """
        pass

    def add_additional_static_properties(self)->None:
        """ OVERRIDE: To extend the static rows, use this hook """
        pass


    def _add_source_type( self, musicbook:dict ):
        """ Figure out what type of entry we have (PDF or PNG) and display options based upon that """
        label = 'Book Display Using'
        if not os.path.exists( musicbook[ BOOK.location ] ):
            self._insertPropertyEntry( self._format_static_property(
                label, '(Book not found)', False ) )
            return
               
        if os.path.isdir( musicbook[ BOOK.location ]):
            self._insertPropertyEntry( self._format_static_property(
                label, 'PNG (image files)', False ) )
            return

        pdf_render = self.dbbooksettings.getSetting( musicbook[ BOOK.id ], DbKeys.SETTING_RENDER_PDF , fallback=False, raw=True )
        current_entry = UiProperties.pdf_values[ pdf_render ]
        self._comboPropertyValue( label, UiProperties.pdf_options , current_entry  , self.changeRender )

    def get_changes(self)->dict:
        """ get the properties that have changed """
        return self.changes
    
    def set_properties(self, musicbook:dict ):
        """
        musicbook is the database row for the book which can be indexed
        by name. We pick out the names and put them into the table.
        """
        self.setModal(True)
        self.setWindowTitle("Book properties for " + musicbook[ BOOK.name])
        
        self.clear()
        
        self._nameProperty( 'Book name' , musicbook,  BOOK.name, self.changedName)
        
        self._comboProperty( 'Composer', DbComposer(), musicbook, BOOK.composer, self.changedComposer )
        self._comboProperty( 'Genre'   , DbGenre(),    musicbook, BOOK.genre,    self.changedGenre    )

        self._nameProperty( 'Offset to page 1', musicbook, BOOK.numberStarts, self.changedStart , isInt = True)
        self._nameProperty( 'Last page number', musicbook, BOOK.numberEnds,   self.changedEnd  ,  isInt = True )
        self._nameProperty( 'Web Link',         musicbook, BOOK.link,         self.changedLink ,  isInt = False , cleanup=False)
        self._nameProperty( 'Author' ,          musicbook, BOOK.author,       self.changedAuthor, isInt = False , cleanup=False)
        self.add_additional_properties()

        self._add_source_type( musicbook )
        for prop in self.staticBookInformation:
            data = musicbook[ prop[ self.bpData] ] if prop[self.bpData] in musicbook else "(no data)"
            
            tableEntry = self._format_static_property(
                prop[ self.bpLabel ], 
                data,
                False,
            )
            self._insertPropertyEntry(tableEntry)
        self.add_additional_static_properties()
        self.propertiesTable.resizeColumnsToContents()

        #self.adjustSize(  )


    
class UiPropertiesImages( UiProperties ):
    """ Property images extends the Properties to provide a checkbox for saving TOML informatin"""
    
    def save_toml_file(self)->bool:
        return self._save_toml_file
    
    def add_additional_properties(self):
        self._save_toml_file = True
        self._checkboxProperty( 'Save properties in file' , True, self.checkbox_changed)

    def checkbox_changed( self , state ):
        self._save_toml_file = state