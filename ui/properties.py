# This Python file uses the following encoding: utf-8
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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, 
    QTableWidget, QAbstractItemView, QTableWidgetItem)



class UiProperties(QDialog):
    '''
    This creates a simple grid and populates it with info from musicfile.py

    Changes can be made and data will be returned if a change is made.
    '''

    def __init__(self, parent=None):
        super(UiProperties, self).__init__(parent)
        self.createPropertiesTable()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.propertiesTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)

        self.resize(600, 500)

    def clear(self):
        """ clear will remove all content from the QTable and reset counters"""
        self.propertiesTable.clear()
        self.propertiesTable.horizontalHeader().hide()
        self.selectedProperty = None
        self.selectedPage = None
        self.propertiesTable.setRowCount(0)

        self.flagChanged = False

    def createPropertiesTable(self):
        self.propertiesTable = QTableWidget()
        self.propertiesTable.setColumnCount(1)
        self.propertiesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.propertiesTable.setShowGrid(True)
        self.propertiesTable.setDisabled( False )
    

    def createButtons(self):
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttons.clicked.connect(self.buttonClicked)
    
    def checkItem( self, row ):
        if self.changes[ row ] != self.propertiesTable.item( row, 0 ).text():
            self.changes[ row ] = self.propertiesTable.item( row, 0 ).text()
            self.flagChanged = True
        return self.flagChanged

    def isChanged(self):
        for row in range( 0, len( self.changes )):
            self.checkItem( row )
        return self.flagChanged

    def editCell( self, row, column ):
        self.checkItem( row )

    def editItem( self, item ):
        self.propertiesTable.blockSignals(True)
        if self.changes[item.row()] != item.text() :
            self.changes[item.row()] = item.text()
            self.flagChanged = True
        self.propertiesTable.blockSignals(False)

    def buttonClicked(self, btn ):
        if btn.text() == "Cancel":
            self.reject()
        else:
            if self.flagChanged or self.isChanged() :
                self.accept()
            else:
                self.reject()

    def _formatPageItem(self, header, name, isMutable):
        headerW = QTableWidgetItem( str( header ))
        pageW = QTableWidgetItem(str(name)) 
        if isMutable:  
            pageW.setFlags(  Qt.ItemIsEditable|Qt.ItemIsEnabled)
        else:
            pageW.setFlags(Qt.NoItemFlags)
        return ( headerW, pageW )

    def _insertPropertyEntry(self, property):
        ''' Insert a row into the book's property table
        
        Pass in a list of values: name and property value'''
        row = self.propertiesTable.rowCount()
        self.propertiesTable.insertRow(row)
        self.propertiesTable.setVerticalHeaderItem( row , property[0] )
        self.propertiesTable.setItem(row, 0, property[1])


    def setPropertyList(self, music_file):
        self.setModal(True)
        self.setWindowTitle("Book properties for " + music_file.getBookTitle())
        
        properties = music_file.getProperties()
        self.clear()

        self.changes = []

        for name, bookProperty in properties.items():
            tableEntry = self._formatPageItem(name, bookProperty[0], bookProperty[1] )
            self._insertPropertyEntry(tableEntry)
            if bookProperty[1]: ## Mutable
                self.changes.append( bookProperty[0] )
            if bookProperty[2]: ## enable scroll
                self.propertiesTable.scrollToItem( tableEntry[1])

        self.propertiesTable.resizeColumnsToContents()
        self.propertiesTable.itemChanged.connect( self.editItem )
        self.propertiesTable.cellChanged.connect( self.editCell )
