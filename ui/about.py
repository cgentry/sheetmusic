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

import os
import platform
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextEdit, QPushButton
import PySide6
from db.keys import ProgramConstants

class UiAbout(QDialog):
    __about="""<center><h1>Sheetmusic</h1><h3>Copyright 2022 Charles Gentry</h3>
    <p>
    Sheetmusic version: {}<br>
    Python version    : {}<br>
    PySide version    : {}<br>
    QT Version        : {}
    </p>
    </center>
    <p>
    # Sheetmusic is free software; you can redistribute it and/or modify
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
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget( self.information() )
        layout.addWidget( self.buttonbox() )
        self.setLayout( layout )
        self.resize( 500,600 )

    def formatAbout(self)->str:
        return self.__about.format( 
            ProgramConstants.version, 
            platform.python_version(), 
            PySide6.__version__, 
            PySide6.QtCore.qVersion() )

    def information(self)->QTextEdit:
        global __version__
        self.infobox = QTextEdit()
        self.infobox.setReadOnly( True )
        self.infobox.insertHtml( self.formatAbout()  )
        return self.infobox
    
    def buttonbox(self)->QDialogButtonBox:
        self.buttons = QDialogButtonBox()
        self.btnLicense = QPushButton('License')
        self.buttons.addButton(self.btnLicense, QDialogButtonBox.ApplyRole )
        self.buttons.addButton(QDialogButtonBox.Ok   )
        self.buttons.clicked.connect( self.close )
        return self.buttons

    def close(self, button ):
        buttonClicked = button.text()
        if buttonClicked == 'OK':
            self.accept()
        else:
            if self.btnLicense.text() == 'License':
                dir = os.path.dirname( os.path.dirname( __file__ ) )
                with open( dir + "/documentation/license.html","rt") as fh:
                    self.infobox.clear()
                    self.infobox.insertHtml( fh.read() )
                self.btnLicense.setText('About')
            else:
                self.infobox.clear()
                self.infobox.insertHtml( self.formatAbout() )
                self.btnLicense.setText('License')
