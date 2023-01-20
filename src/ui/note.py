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

from PySide6.QtCore    import QSize, QRect, Qt
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox, QAbstractButton, QPushButton, QTextEdit,QMessageBox , QMenu)
from qdb.util   import DbHelper


class UiNote(QDialog):
    '''
    This will populate a simple text box from the 'notes' field
    '''

    btnTxtClear  = u'Clear'
    btnTxtCancel = u'Cancel'
    btnTxtSave   = u'Save'
    btnTxtDelete = u'Delete'

    actionCancel = 0
    actionSave   = 1
    actionDelete = 2

    def __init__(self):
        super().__init__()
        self._markdown      = True
        self._delete_entry  = False
        self._action        = self.actionCancel
        self._id            = None
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
        self.btnDelete = QPushButton( self.btnTxtDelete )

        self.btnClear.setObjectName('clear')
        self.btnSave.setObjectName( 'save')
        self.btnCancel.setObjectName('cancel')
        self.btnDelete.setObjectName('delete')
        self.btnSave.setDefault(True)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton( self.btnSave,    QDialogButtonBox.YesRole)
        self.buttons.addButton( self.btnCancel , QDialogButtonBox.RejectRole)
        self.buttons.addButton( self.btnClear,   QDialogButtonBox.ResetRole)
        self.buttons.addButton( self.btnDelete,  QDialogButtonBox.DestructiveRole)
        
        self.buttons.accepted.connect(self.accept() )
        self.buttons.rejected.connect(self.reject() )
        self.buttons.clicked.connect(self.buttonClicked)

    def buttonClicked(self, btn:QAbstractButton ):
        if btn.text() == self.btnTxtClear :
            self.clear()

        if btn.text() == self.btnTxtSave:
            self._action = self.actionSave
            self.accept()
        if btn.text() == self.btnTxtCancel :
            self._action = self.actionCancel
            self.reject()
        if btn.text() == self.btnTxtDelete:
            self.confirmDelete()

    def confirmDelete(self):
        if QMessageBox.Yes == QMessageBox.warning(
            None, "",
            "Delete note for page?",
            QMessageBox.No | QMessageBox.Yes 
        ) :
            self._action = self.actionDelete
            self.accept()

    def setID( self, id:int ):
        self._id = id
        self.btnDelete.setEnabled( not self._id is None)

    def ID(self)->int:
        return self._id

    def setText(self, txt:str)->None:
        if not isinstance( txt , str ):
            raise ValueError("Invalid text passed: {}".format( type(txt )))
        self.textField.setMarkdown( txt )
        self._textChanged = False

    def text( self )->str:
        return self.textField.toMarkdown()

    def setChanged(self)->None:
        self._textChanged = True
    
    def delete(self)->bool:
        return self._action == self.actionDelete

    def action( self ):
        return self._action

    def textChanged(self)->bool:
        return self._textChanged

    def resizeEvent(self, event):
        self._textChanged = True

    def moveEvent(self, event ):
        super().moveEvent( event )
        self._textChanged = True

    def setLocation( self, loc ):
        """ Restore location from either a QPoint or an encoded string """
        if isinstance( loc , QRect ) :
            self.setGeometry( loc )
        elif isinstance( loc , str ) and len( loc ) > 0 :   
            self.setGeometry( DbHelper.decode( loc ))
        
    def location( self )->str:
        return DbHelper.encode( self.geometry() )

class UiNoteView(QTextEdit):
    '''
    This will populate a simple text box from the 'notes' field
    This is a 'viewer', not an editor
    '''
    def __init__(self):
        super().__init__()
        self._markdown      = True
        self._delete_entry  = False
        self._id            = None
        self.setupTextField()
        self.setupPopupMenu()
        #self.addWidget(self.textField)
        
        self.setMinimumHeight(300)
        self.setMinimumWidth( 500 )

    def setSize( self, size:QSize , scale=.5)->None:
        self.resize( int(size.width() *scale), int(size.height()* scale) ) 

    def setupTextField(self):
        self._hide = True
        self.setAcceptRichText(True)
        self.setWindowFlag( Qt.FramelessWindowHint )
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.setWindowOpacity( .9 )
        self.setReadOnly(True)

    def setupPopupMenu(self)->None:
        self.menu = QMenu()
        self.menu.addAction('Close')
        self.menu.addAction('Transparent')
        self.menu.addAction('Copy')
        self.menu.triggered.connect( self.menuTriggered )
        pass

    def menuTriggered(self, action ):
        if action.text() == 'Close':
            self.close()

    def mousePressEvent(self, e) -> None:
        txt = self.toPlainText()
        rel_pos = self.pos()
        pos = self.mapToGlobal(rel_pos)
        if e.button() == Qt.RightButton:
            self.setText( txt + "\nRIGHT")
            self.menu.exec( e.globalPosition().toPoint())
            return True 
        
        self.setText( txt + "\nPress")
        super().mousePressEvent(e)

    def enterEvent(self, event) -> None:
        # if self._hide :
        #     self._hide = False
        #     self.setWindowFlag( Qt.FramelessWindowHint, False)
        #     self.show()
        return super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._hide :
            self._hide = True
            self.setWindowFlag( Qt.FramelessWindowHint )
            self.show()
        return super().leaveEvent(event)
    


if "__main__" == __name__ :
    from PySide6.QtWidgets import QApplication
    import os, sys
    app = QApplication([])

    mainFile = os.path.abspath(sys.modules['__main__'].__file__)

    tmod = UiNoteView( )
    tmod.setText("Hello __World__!\nThis is <b>Chuck</b>")
    tmod.show()

    tmod2 = UiNoteView( )
    tmod2.setText("window2")
    tmod2.move( 0,0)
    tmod2.show()


    sys.exit( app.exec() )
    