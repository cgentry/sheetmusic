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

from PySide6.QtCore    import QSize
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QAbstractButton, QPushButton, QTextEdit )


class UiNote(QDialog):
    '''
    This will populate a simple text box from the 'notes' field
    '''

    btnTxtClear  = u'Clear'
    btnTxtCancel = u'Cancel'
    btnTxtSave   = u'Save'

    def __init__(self):
        super().__init__()
        self._markdown = True
        self.createTextField()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.textField)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.setMinimumHeight(300)
        self.setMinimumWidth( 500 )

    def setSize( self, size:QSize , scale=.5)->None:
        self.resize( int(size.width() *scale), int(size.height()* scale) ) 

    def createTextField(self):
        self.textField = QTextEdit()
        self.textField.setAcceptRichText(True)
        self._textChanged = False
        self.textField.textChanged.connect( self.setChanged )

    def clear(self)->None:
        self.textField.clear()

    def createButtons(self)->None:
        self.btnClear = QPushButton(  self.btnTxtClear )
        self.btnSave = QPushButton(   self.btnTxtSave )
        self.btnCancel = QPushButton( self.btnTxtCancel)

        self.btnClear.setObjectName('clear')
        self.btnSave.setObjectName('save')
        self.btnCancel.setObjectName('cancel')
        self.btnSave.setDefault(True)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton( self.btnSave,    QDialogButtonBox.YesRole)
        self.buttons.addButton( self.btnCancel , QDialogButtonBox.RejectRole)
        self.buttons.addButton( self.btnClear,   QDialogButtonBox.ResetRole)
        
        self.buttons.accepted.connect(self.accept() )
        self.buttons.rejected.connect(self.reject() )
        self.buttons.clicked.connect(self.buttonClicked)

    def buttonClicked(self, btn:QAbstractButton ):
        if btn.text() == self.btnTxtClear :
            self.clear()
        if btn.text() == self.btnTxtSave :
            self.accept()
        if btn.text() == self.btnTxtCancel :
            self.reject()

    def setText(self, txt:str)->None:
        if not isinstance( txt , str ):
            raise ValueError("Invalid text passed: {}".format( type(txt )))
        self.textField.setMarkdown( txt )
        self._textChanged = False

    def text( self )->str:
        return self.textField.toMarkdown()

    def setChanged(self)->None:
        self._textChanged = True
    
    def textChanged(self)->bool:
        return self._textChanged

if "__main__" == __name__ :
    from PySide6.QtWidgets import QApplication
    import os, sys
    app = QApplication([])
    mainFile = os.path.abspath(sys.modules['__main__'].__file__)
    tmod = UiNote( )
    tmod.setText("Hello __World__!\nThis is <b>Chuck</b>")
    tmod.setWindowTitle("General Notes for book")
    s = QSize()
    s.setHeight( 2048 )
    s.setWidth( 1024 )
    tmod.setSize( s )
    tmod.show()
    rtn = tmod.exec()
    print("Return was ", rtn )
    print( tmod.text() )
    print("\nText changed? {}".format( tmod.textChanged() ))