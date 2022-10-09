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


###
# EditItem is a combo box that allows inserts/selection from a table.
# the table needs to have one field: name.
# It must inherit from DbGeneric in order to work (or have same signature)
#
# This will normally allow inserts

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore    import Qt

class UiGenericCombo( QComboBox ):

    def __init__(self , isEditable:bool=True, fill:any=None, currentValue:str=None, name:str=None):
        super().__init__()
        self.setEditable( isEditable )
        if name is not None:
            self.setObjectName( name )
        if fill is not None:
            if isinstance( fill, dict ):
                self.fillDict( fill , currentValue )
            elif isinstance( fill, list ):
                self.fillList( fill, currentValue )
            else:
                self.fillTable( fill, currentValue )
        

    def _finishSetup( self ):
        self.setMinimumWidth(200)
        self.setDuplicatesEnabled( False )

    def findData( self, currentValue )->int:
        for i in range( 0, self.count() ) :
            if currentValue == self.itemData( i ):
                return i
        return -1

    def setCurrentItem( self, currentValue:str=None, add=False):
        if currentValue is not None and currentValue != '':
            if add :
                super().setCurrentText( currentValue )
            else:
                idx = self.findText( currentValue )
                if idx < 0:
                    idx = self.findData( currentValue )
                if idx >= 0:
                    self.setCurrentIndex( idx )

    def fillDict( self, values:dict, currentValue:None ):
        """
            Fill the dropdown box with key/value from dictionary
        """
        for key, value in values.items() :
            self.addItem( str(key), userData=value )
        self.setCurrentItem( currentValue)
        self._finishSetup()

            
    def fillList( self, values:list , currentValue:None ):
        """
            Fill the dropdown box with values from a list
        """
        self.addItems( values )
        self.setCurrentItem( currentValue )
        self._finishSetup()

    def fillTable(self, dbObject, currentValue:str=None):
        """
            Fill the dropdown box with values from the database.
            The input should be the results of an 'execute(...)'
        """
        self.clear()
        rows = dbObject.getall()
        if rows is not None and len(rows) > 0 :
            if isinstance( rows, list ):
                self.addItems( rows )
            else:
                self.addItems( [row['name'] for row in rows])
        self.setCurrentItem( currentValue )
        self._finishSetup()
        

    

    
