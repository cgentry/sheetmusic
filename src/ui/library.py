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

import shutil
import os
import sys
from qdb.dbbook import DbGenre, DbComposer, DbBook
from qdb.keys   import BOOK
from qdil.preferences import DilPreferences
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,    QDialog,       QDialogButtonBox,
    QGridLayout,  QHBoxLayout,   QVBoxLayout,
    QWidget,      QSplitter,     QTextEdit, 
    QTableWidget, QTreeWidgetItem, QLabel,             
    QTableWidgetItem, QHeaderView, QInputDialog,
    QMessageBox, QLineEdit
)
from util.library import LibraryConsolidate
from ui.util import centerWidgetOnScreen

class UiLibraryConsolidate():
    def __init__(self):
        self.sheetmusic_dir = DilPreferences().getDirectoryDB()
        pass

    def exec(self):
        if QMessageBox.Cancel == QMessageBox.question(
            None,
            u'Consolidate Library',
            u'This will copy content from other directories into the sheetmusic directory:\n{}.'.format( self.sheetmusic_dir ),
            QMessageBox.Cancel, QMessageBox.Ok
        ):
            return
        self.process_copy()

    def _create_dialog(self)->QDialog:
        self.dlg = QDialog()
        self.dlg.setWindowTitle('Consolidate Music Library')
        layout = QVBoxLayout()

        self.status = QTextEdit()
        self.status.setReadOnly(True)

        self.btns = QDialogButtonBox()
        self.btns.addButton( QDialogButtonBox.Ok )
        self.btns.setDisabled(True)
        self.btns.clicked.connect( self._button_pressed )

        layout.addWidget( self.status )
        layout.addWidget( self.btns )
        self.dlg.setLayout( layout )
        self.dlg.setMinimumSize( 800, 400 )
        return self.dlg

    def _button_pressed( self, btn ):
        self.dlg.accept()

    def process_copy(self)->None:
        
        not_in_lib = LibraryConsolidate.books_not_in_library()
        if len( not_in_lib ) == 0 :
            QMessageBox.information(
                None,
                u'Consolidate Library',
                u"All entries are stored in sheetmusic directory.\nNothing to do.",
                QMessageBox.Ok
            )
            return
        
        dlg = self._create_dialog()
        dlg.show()
        dbbook = DbBook()
        centerWidgetOnScreen( dlg )
        sys.addaudithook( self.track_copy )
        for book in not_in_lib:
            book_name = book[ BOOK.book ]
            self.status.append( """\nBOOK: {}""".format( book_name ) )

            lib_book = dbbook.getBook( book_name)
            if lib_book is None:
                msg = """\n\tBook not found in library. Skipping.\n""".format( book_name )
                continue

            loc = book[BOOK.location]
            loc_target_dir = os.path.basename( os.path.basename( loc ))
            sheetmusic = os.path.join( self.sheetmusic_dir , loc_target_dir )
            
            shutil.copytree( loc ,  sheetmusic  )
            if os.path.isdir( sheetmusic ):
                dbbook.update( book=book_name , location=sheetmusic )
                self.status.append("""\tLibrary updated.""")
            else:
                self.status.append("""\tERROR: Directory doesn't exist. Copy failed. Not updating library.""" )
        self.btns.setEnabled( True )
        return dlg.exec()
        
    def track_copy( self, event, args   ):
        if event == "shutil.copytree" :
            self.status.append( """\n\tFILE: {}\n\tDEST: {}""".format( args[0], args[1]))

class UiLibraryCheck():
    def __init__(self):
        QMessageBox.information(
            None,
            "Check Library",
            "Sorry, this isn't implemented yet.",
            QMessageBox.Ok
        )