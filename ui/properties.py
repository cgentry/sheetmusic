# This Python file uses the following encoding: utf-8
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

import re
from PySide6.QtCore import Qt
from PySide6.QtGui  import QIntValidator, QValidator
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QLineEdit, QMessageBox,
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView, QPushButton )

from qdb.keys         import BOOK, DbKeys
from ui.editItem      import UiGenericCombo
from qdb.dbbook       import DbComposer, DbGenre
from qdil.preferences import DilPreferences
from util.convert     import toInt

class simpleValidator( QValidator ):
    badChars = r'[?%\\|/\n\t\r]+'

    def __init__(self):
        super().__init__();

    def fixupt(self, needsCleanup ):        # No newline, returns or tabs
        needsCleanup = re.sub( self.badChars , ' ' , needsCleanup)
        return needsCleanup.strip()

    def validate(self, arg1:str, arg2 ):
        if len( arg1.strip() ) == 0 :
            return QValidator.Invalid
        if re.search( self.badChars , arg1 ) or arg1.startswith(' '):
            return QValidator.Invalid
        return QValidator.Acceptable

class UiProperties(QDialog):
    '''
    This creates a simple grid and populates it with info from the Book
    Changes can be made and data will be returned if a change is made.
    '''
    bpData = 0
    bpLabel = 1

    btnTxtIgnore = u'Continue'
    btnTxtCancel = u'Cancel'
    btnTxtApply  = u'Apply'

    staticBookInformation = [
        [ BOOK.location,     'Book location'],
        [ BOOK.totalPages,   'Total pages'],
        [ BOOK.source,       'Original book source'],
        [ BOOK.dateAdded,    'Date added'],
    ]
    def __init__(self, parent=None):
        super(UiProperties, self).__init__(parent)
        self.createPropertiesTable()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.propertiesTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.cleanupLevel = DilPreferences().getValueInt( DbKeys.SETTING_NAME_IMPORT, DbKeys.VALUE_NAME_IMPORT_FILE_0 )
        self.resize(500, 300)

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
    

    def createButtons(self):
        self.skipButton = QPushButton( self.btnTxtIgnore )
        self.applyButton = QPushButton( self.btnTxtApply )
        self.cancelButton = QPushButton( self.btnTxtCancel)
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.skipButton, QDialogButtonBox.ResetRole)
        self.buttons.addButton( self.applyButton, QDialogButtonBox.YesRole)
        self.buttons.addButton( self.cancelButton , QDialogButtonBox.RejectRole)
        self.buttons.clicked.connect(self.buttonClicked)
       
    def buttonClicked(self, btn ):
        if btn.text() == self.btnTxtIgnore:
            self.changes={}
            self.accept()
        elif btn.text() == self.btnTxtCancel:
            self.changes={}
            self.reject()
        else:
            self.accept()
    
    def isReject(self)->bool:
        return (self.result() == self.Rejected )
    
    def isSkip(self)->bool:
        return( self.result()==self.Accepted and len(self.changes) == 0 )

    def isApply( self )->bool:
        return( self.result()==self.Accepted and len(self.changes) > 0 )

    def _formatPageItem(self, label:str, itemValue, isMutable:bool):
        headerW = QTableWidgetItem( str( label ))
        pageW = QTableWidgetItem(str(itemValue)) 
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
        apply = (len( self.changes ) > 0 )
        self.applyButton.setDefault(apply)
        self.applyButton.setEnabled( apply )
        self.skipButton.setDefault( ( not apply ) )

    def changedName(self, value):
        self.changes[ BOOK.name ] = self._cleanupName( value )
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
        
    def changedComposer(self, value):
        self.changes[ BOOK.composer ] = value.strip()
        self.defaultButton()

    def changedGenre( self, value ):
        self.changes[ BOOK.genre ] = value.strip()
        self.defaultButton()

    def _cleanupName(self, bookName:str )->str:
        ## first ALWAYS replace invalid characters
        bookName = re.sub(r'[\n\t\r]+', '', bookName )          # No newline, returns or tabs
        bookName = re.sub(r'[#%{}<>*?$!\'":@+\\|=/]+', ' ' , bookName)      ## bad characters
        bookName = re.sub(r'\s+',       ' ' , bookName)         ## Only one space when multiples
        bookName = re.sub(r'^[^a-zA-Z\d]+', '' , bookName)      ## Leading char must be Alphanumeric
        
        if self.cleanupLevel == DbKeys.VALUE_NAME_IMPORT_FILE_1:
            bookName = re.sub( r'[_]*', ' ', bookName )
        if self.cleanupLevel == DbKeys.VALUE_NAME_IMPORT_FILE_2:
            bookName = re.sub( r'[_]*', ' ', bookName )
            bookName = bookName.title()

        return bookName.strip()

    def _nameProperty( self , label:str, musicbook:dict , valueKey:str, onChange, isInt:bool=False ):
        name = QLineEdit()
        if isInt:
            value = str(musicbook[valueKey] if valueKey in musicbook else 1)
        else:
            value = self._cleanupName( str(musicbook[valueKey]) )
        name.setText( value )
        if isInt:
            name.setValidator( QIntValidator( 0, 999, self ) )
        else:
            name.setValidator( simpleValidator() )
        name.setObjectName( valueKey )
        name.textEdited.connect( onChange )
        self._insertPropertyEntry( [QTableWidgetItem( label ) , name] )
        
    def _comboProperty( self, label:str, dbentry,  musicbook:dict, valueKey:str, changeFunction ):
        combo = UiGenericCombo()
        currentEntry = ( str(musicbook[valueKey] ) if valueKey in musicbook else 'Unknown' )
        combo.fillTable( dbentry , currentEntry )
        combo.currentTextChanged.connect( changeFunction )
        self._insertPropertyEntry( [ QTableWidgetItem( label ) , combo ])

    def setPropertyList(self, musicbook:dict ):
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
        self._nameProperty( 'Last page number', musicbook, BOOK.numberEnds,   self.changedEnd , isInt = True )
  
        for prop in self.staticBookInformation:
            data = musicbook[ prop[ self.bpData] ] if prop[self.bpData] in musicbook else "(no data)"
            tableEntry = self._formatPageItem(
                prop[ self.bpLabel ], 
                data,
                False,
            )
            self._insertPropertyEntry(tableEntry)

        self.propertiesTable.resizeColumnsToContents()

        #self.adjustSize(  )

