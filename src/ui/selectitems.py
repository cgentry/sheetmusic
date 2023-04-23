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

from PySide6.QtWidgets import (
        QDialog, 
        QDialogButtonBox ,  QPushButton, QLabel,
        QListWidget ,       QListWidgetItem,  QVBoxLayout
    )
from PySide6.QtCore import Qt

class SelectItems( QDialog ):
    def __init__(self, title:str=None, heading:str=None):
        super().__init__()
        self.dataList = {}
        self._ignoreCheckedItems = False
        self.totalSelected = 0
        self.setDialog(
            self.createTitle(title) ,
            self.createList() ,
            self.createButtonBox() )

        if title is not None:
            self.setWindowTitle( title )
        self.setHeading(heading)
        self.resize( 600,500)


    def setDialog( self, *args ):
        self._dialog_layout = QVBoxLayout()
        for element in args:
            self._dialog_layout.addWidget( element )
        self.setLayout( self._dialog_layout )

    def createTitle(self, heading:str=None)->QLabel:
        self.lblHeading =  QLabel()
        self.setHeading( heading )
        return self.lblHeading

    def createList(self)->QListWidget:
        self.checkList = QListWidget()
        self.checkList.itemClicked.connect( self.actionSelected )
        return self.checkList

    def createButtonBox(self)->QDialogButtonBox:
        self.buttonBox = QDialogButtonBox()
        self.btn_yes = QPushButton('Yes')
        self.btn_no  = QPushButton('No')
        self.btn_toggle = QPushButton('Select All')
        
        self.buttonBox.addButton( self.btn_yes, QDialogButtonBox.AcceptRole )
        self.buttonBox.addButton( self.btn_no , QDialogButtonBox.RejectRole )
        self.buttonBox.addButton( self.btn_toggle , QDialogButtonBox.HelpRole)
        self.buttonBox.accepted.connect( self.actionAccepted )
        self.buttonBox.rejected.connect( self.actionRejected )
        self.buttonBox.helpRequested.connect( self.action_toggle )
        return self.buttonBox

    def setHeading( self, heading:str ):
        if heading:
            self.lblHeading.setText( heading )

    def setButtonText( self, btn_yes:str='Yes', btn_no:str='No' ):
        self.btn_yes.setText( btn_yes)
        self.btn_no.setText( btn_no)
        self.btn_yes.setEnabled(False)

    def _widgetFromDatum( self, label )->QListWidgetItem:
        lim = QListWidgetItem()
        lim.setText(label)
        lim.setFlags( Qt.ItemIsUserCheckable |Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        lim.setCheckState(Qt.Unchecked)
        
        return lim

    def _fromList(self, data:list ):
        for index, datum in enumerate( data,0 ):
            self.data[index]=datum
            self.checkList.addItem( self._widgetFromDatum( datum))

    def _fromDict( self,dictionary:dict ):
        index = 0
        for key,value in dictionary.items():
            self.data[index]=value
            self.checkList.addItem( self._widgetFromDatum( key))
            index = index+1

    def setData(self, data):
        """
            Fill in the combo box from either a dictionary or a simple list
            Data that is checked will be returned in 'dataList' as both key 
            and data
            Dictionaries are { display_data : return_value }
        """
        self.data = {}
        if isinstance( data , dict ):
            self._fromDict( data )
        else:
            self._fromList( data )

    def _fillInCheckedItems(self, selectionType ):
        dataList= {}
        for i in range(0, self.checkList.count() ):
            item = self.checkList.item(i)
            if item.checkState() == selectionType :
                dataList[ item.text() ] = self.data[i]
        return dataList

    def getDataList( self )->dict:
        dataList= {}
        for i in range(0, self.checkList.count() ):
            dataList[ self.checkList.item(i).text() ] = self.data[i]
        return dataList

    def getCheckedList(self)->dict:
        """ Return the dictionary of checked items """
        return ( {} if self._ignoreCheckedItems else self._fillInCheckedItems( Qt.Checked ) )
    
    def setCheckedList( self , value:bool):
        state = Qt.Checked if value else Qt.UnChecked
        for row in range( self.checkList.count() ):
            self.checkList.item( row ).setCheckState( state )
    
    def getUncheckedList(self)->dict:
        return ( self.getDataList() if self._ignoreCheckedItems else self._fillInCheckedItems( Qt.Unchecked ) )
    
    def getCheckedListValues(self)->list:
        """ This returns just the values - the full paths - of items selected"""
        checked = self.getCheckedList()
        return list( self._fillInCheckedItems( Qt.Checked ).values() )

    def actionAccepted(self):
        self._ignoreCheckedItems = False
        self.accept()

    def actionRejected(self):
        self._ignoreCheckedItems = True
        self.reject()

    def action_toggle(self):
        have_checked = False
        for row in range(0, self.checkList.count() ):
            ischeck = self.checkList.item(row).checkState()
            if ischeck == Qt.Checked:
                self.checkList.item(row).setCheckState( Qt.Unchecked )
            else:
                self.checkList.item(row).setCheckState( Qt.Checked )
                have_checked = True

        self.btn_yes.setEnabled( have_checked )

    def actionSelected(self, item:QListWidgetItem ):
        if item.checkState() == Qt.Checked :
            item.setCheckState( Qt.Unchecked)
            self.totalSelected += -1
        else:
            item.setCheckState( Qt.Checked )
            self.totalSelected += 1
        self.btn_yes.setEnabled( self.totalSelected > 0 )
        item.setSelected( False )
