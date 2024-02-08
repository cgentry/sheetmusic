"""
User Interface : About

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import os
import platform
from   PySide6.QtGui     import QPixmapCache
from   PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextEdit, QPushButton
import PySide6
from constants import ProgramConstants

class UiAbout(QDialog):
    """ Present a dialog with information about the program """
    __about="""<center><h1><u>Sheetmusic</u></h1>
    <table>
    <tr><td>Author</td><td>Charles Gentry</td></tr>
    <tr><td>Sheetmusic version&nbsp;&nbsp;</td><td>{}</td></tr>
    <tr><td>Python version</td><td>{}</td></tr>
    <tr><td>PySide version</td><td>{}</td></tr>
    <tr><td>QT Version</td><td>{}</td></tr>
    <tr><td>Image Cache Size</td><td>{} KB</td></tr>
    </table>
    </center>
    <p>
    Sheetmusic is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    </p><p>
    Sheetmusic is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    </p><p>
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.
    </p>
    <br/><br/><br/><br/>
    <p style="text-align: right;">{}</p>
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget( self.information() )
        layout.addWidget( self.buttonbox() )
        self.setLayout( layout )
        self.resize( 500,600 )

    def format_about(self)->str:
        """ Format the 'about' information"""
        return self.__about.format(
            ProgramConstants.VERSION,
            platform.python_version(),
            PySide6.__version__,
            PySide6.QtCore.qVersion() ,
            QPixmapCache.cacheLimit(),
            ProgramConstants.COPYRIGHT
        )

    def information(self)->QTextEdit:
        """ Create and fill a RO text edit box"""
        self.infobox = QTextEdit()
        self.infobox.setReadOnly( True )
        self.infobox.insertHtml( self.format_about()  )
        return self.infobox

    def buttonbox(self)->QDialogButtonBox:
        """ Create a box and add all the buttons """
        self.buttons = QDialogButtonBox()
        self.btn_license = QPushButton('License')
        self.buttons.addButton(self.btn_license, QDialogButtonBox.ApplyRole )
        self.buttons.addButton(QDialogButtonBox.Ok   )
        self.buttons.clicked.connect( self.close )
        return self.buttons

    def close(self, button ):
        """ Close the dialog box """
        if button.text() == 'OK':
            self.accept()
        else:
            if self.btn_license.text() == 'License':
                fdir = os.path.dirname( os.path.dirname( __file__ ) ) +\
                    "/docs/license.html"
                with open( fdir ,"rt", encoding='utf-8') as fh:
                    self.infobox.clear()
                    self.infobox.insertHtml( fh.read() )
                self.btn_license.setText('About')
            else:
                self.infobox.clear()
                self.infobox.insertHtml( self.format_about() )
                self.btn_license.setText('License')
