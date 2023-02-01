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
import sys
from util.convert import toInt

from PySide6.QtWidgets import (
    QAbstractButton, QApplication, QCheckBox,
    QComboBox, QDialog, QDialogButtonBox, 
    QFileDialog, QGridLayout, QHBoxLayout, 
    QLabel, QLineEdit, QMessageBox, 
    QPushButton, QRadioButton, QTabWidget, 
    QTextEdit, QVBoxLayout, QWidget )   
from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader,QFont

class PageNumber(QDialog):
    """
        PageNumber will display a 'go to page' window, prompting the
        user to enter a page number (absolute or relative)
    """
    def __init__(self, page=None, relative=True, parent=None):
        super(PageNumber, self).__init__(parent)
        self.setWindowTitle("Go To Page")

        layout = QVBoxLayout()
        layout.addWidget( self._createGrid(page,relative) )
        layout.addWidget( self.createButtons() )
        self.setLayout( layout )

        self.page = page
        self.relative = relative


    def _createGrid( self, page:int, relative:bool) -> QGridLayout:
        widg = QWidget()
        grid = QGridLayout()

        lbl = QLabel()
        lbl.setText("Page number")
        grid.addWidget(lbl, 0, 0)

        self.pageNumber = QLineEdit()
        if page is not None:
            self.pageNumber.setText( str(page))
        grid.addWidget(self.pageNumber, 0,1)

        self.pageMarker = QLabel()
        grid.addWidget(self.pageMarker, 0, 2 )

        self.relativePage = QCheckBox()
        self.relativePage.setText("Use page numbering shown in book")
        self.relativePage.setChecked(relative)
        grid.addWidget( self.relativePage , 1,1)

        self.errorlabel = QLabel()
        grid.addWidget( self.errorlabel, 2,1)

        widg.setLayout( grid )

        return widg

    def verify( self ):
        self.errorlabel.clear()
        self.pageMarker.clear()
        self.pageNumber.setText( self.pageNumber.text().strip() )
        if self.pageNumber.text() == "" :
            self.errorlabel.setText("<b>Page number cannot be blank</b>")
        elif self.pageNumber.text().isnumeric() :
                self.accept()
                self.page = toInt( self.pageNumber.text(), self.page )
                self.relative = self.relativePage.isChecked()
        else:
            self.errorlabel.setText("<b>Page number must be numeric</b>")
        return

    def actionButtonClicked(self, button:QAbstractButton ):
        if button.text() =='Cancel':
            self.reject()
        self.verify()

    def createButtons(self) -> QDialogButtonBox:
        self.buttons = QDialogButtonBox()
        self.buttons.addButton( QDialogButtonBox.Cancel )
        self.buttons.addButton( QDialogButtonBox.Ok )
        #self.buttons.addButton( "Go", QDialogButtonBox.OkRole)
        self.buttons.clicked.connect(self.actionButtonClicked)

        return self.buttons

if __name__ == "__main__":
    app = QApplication()
    window = PageNumber( )
    rtn = window.exec()
    
    print( "....rtn is", rtn )
    sys.exit(app.exec())