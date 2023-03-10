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
from util.library import Library
from ui.util import centerWidgetOnScreen
class UiOutputMixin():

    def _setSize( self , h, w ):
        self.dlg.setMinimumSize( h, w )
        self.dlg.show()
        centerWidgetOnScreen( self.dlg )

    def _create_dialog(self, title='')->QDialog:
        self.dlg = QDialog()
        self.dlg.setWindowTitle(title)
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
        
        return self.dlg

    def _button_pressed( self, btn ):
        self.dlg.accept()

class UiLibraryConsolidate( UiOutputMixin):
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


    def process_copy(self)->None:
        
        not_in_lib = Library.books_not_in_library()
        if len( not_in_lib ) == 0 :
            QMessageBox.information(
                None,
                u'Consolidate Library',
                u"All entries are stored in sheetmusic directory.\nNothing to do.",
                QMessageBox.Ok
            )
            return
        
        self._create_dialog('Consolidate Music Library')
        self.dlg._setSize( 800, 800 )
        
        dbbook = DbBook()
        
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
        return self.dlg.exec()
        
    def track_copy( self, event, args   ):
        if event == "shutil.copytree" :
            self.status.append( """\n\tFILE: {}\n\tDEST: {}""".format( args[0], args[1]))


class UiLibraryCheck():
    DELETE = 0
    LEAVE  = 1
    def _create_dialog(self)->QDialog:
        self.dlg = QDialog()
        self.dlg.setWindowTitle('Consolidate Music Library')
        layout = QVBoxLayout()

        self.status = QTextEdit()
        self.status.setReadOnly(True)

        self.btns = QDialogButtonBox()
        self.btns.addButton( 'Delete', QDialogButtonBox.RejectRole )
        self.btns.addButton( 'Ignore', QDialogButtonBox.AcceptRole)
        self.btns.clicked.connect( self._button_pressed )

        layout.addWidget( self.status )
        layout.addWidget( self.btns )
        self.dlg.setLayout( layout )
        self.dlg.setMinimumSize( 800, 400 )
        return self.dlg
    
    def _button_pressed( self, btn ):
        sig = ( UiLibraryCheck.LEAVE if btn.text() != 'Delete' else UiLibraryCheck.DELETE )
        self.dlg.done( sig )
    
    def handle_bad_lib_entries( self, in_lib_no_folder:list, shelved:list )->None:
        if len( in_lib_no_folder ) == 0 :
            QMessageBox.information(
                None,
                'Check Library',
                'Books in library are all good',
                QMessageBox.Ok)
            return
        
        self._create_dialog()
        self.status.clear()
        self.status.insertHtml( "<h2>Library entries with no matching folders</h2><br/>")
        for book in in_lib_no_folder:
            self.status.insertHtml( "<p><b>BOOK: </b>{}<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Folder: {}</p><br/>".format( book[BOOK.book], book[BOOK.location]))
        self.status.insertHtml( "<br/>Total library entries: {}<br/>Total problem entries: {}<br/>Delete library entries?".format( 
            len( shelved), len(in_lib_no_folder)))
        if UiLibraryCheck.DELETE == self.dlg.exec():
            dbbook = DbBook()
            for book in in_lib_no_folder:
                dbbook.delBook( book[ BOOK.book ])
            
    def handle_extra_folders( self, folder_not_in_lib:list , all_folders:list ):
        if len( folder_not_in_lib ) == 0 :
            QMessageBox.information(
                None,
                'Check Library',
                'No mismatched folders found',
                QMessageBox.Ok)
            return  
        
        self._create_dialog()
        self.status.clear()
        self.status.insertHtml( "<h2>SheetMusic folders do not match library</h2><br/>")
        for folder in folder_not_in_lib:
            self.status.insertHtml( "<p><b>Folder: </b>{}</p><br/>".format( folder))
        self.status.insertHtml( "<br/>Total folder entries: {}<br/>Total problem foldres: {}<br/>Delete folders?".format( 
            len( all_folders), len(folder_not_in_lib)))
            
        if UiLibraryCheck.DELETE == self.dlg.exec():
            for folder in folder_not_in_lib:
                shutil.rmtree( folder )
                
    def exec(self):
        (shelved, off_side) = Library.books_locations()
        all_folders = Library.folders()

        #find differences
        in_lib_no_folder = [] 
        folder_not_in_lib = [] # FOLDER, Not in lib

        book_folders = [ book[ BOOK.location ] for book in shelved ]
        
        for book in shelved:
            if not book[ BOOK.location ] in all_folders :
                in_lib_no_folder.append( book )

        for book in off_side :
            if not os.path.isdir( book[ BOOK.location ]):
                in_lib_no_folder.append( book )

        for folder in all_folders:
            if not folder in book_folders :
                folder_not_in_lib.append( folder )

        if len( in_lib_no_folder ) == 0 and len( folder_not_in_lib ) == 0 :
            QMessageBox.information(
                None,
                'Check Library',
                'Books in library and folders are good.',
                QMessageBox.Ok
            )
            return
        
        self.handle_bad_lib_entries( in_lib_no_folder ,shelved )
        
        self.handle_extra_folders( folder_not_in_lib, all_folders )
    
class UiLibraryStats(UiOutputMixin):

    def __init__(self):
        self.genre = {}
        self.composer = {}
        self.book_no_genre = []
        self.book_no_composer = []
        self._fmt_totals = """<table>
            <tr><th colspan='2'>Summary</th></tr>
            <tr><th colspan='2'>========================</th></tr>
            <tr><td>Total books                      &nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Books stored in sheetmusic folder&nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Books stored in other folders    &nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Composers                        &nbsp;&nbsp;</td><td>{}</td></tr>
            <tr><td>Genres                           &nbsp;&nbsp;</td><td>{}</td><tr>
            </table><br/>"""
        
        self._hdr_comp_genre="""<table 'width:100%'>
            <tr><th>Composers</th><th>Genres</th></tr>
            <tr><th>========================</th><th>========================</</th></tr>"""
        self._fmt_comp_genre="""<tr><td>{}&nbsp;&nbsp;{}</td><td>{}&nbsp;&nbsp;{}</td></tr>"""
        self._end_comp_genre="</table><br/><br/>"

        self._hdr_missing="""<table 'width:100%'>
            <tr><th>Books with no {}.</th></tr>
            <tr><th>========================</th>"""
        self._fmt_missing="""<tr><td>{}</td></tr>"""
        self._end_missing="</table><br/><br/>"

    def _tally_subcat( self, catalog:dict ):
        for book in catalog :
            c = book[ BOOK.composer ]
            g = book[ BOOK.genre ]

            if not c :
                self.book_no_composer.append( book[BOOK.book ])
                c = '(not set)'
            
            if not g:
                self.book_no_genre.append( book[BOOK.book])
                g = '(not set)'
            
            self.composer[c] = self.composer[c] + 1 if c in self.composer else 1
            self.genre[g]    = self.genre[g]    + 1 if g in self.genre    else 1

    def _tally_categories(self, shelved:dict, on_loan:dict):
        self._tally_subcat( shelved )
        self._tally_subcat( on_loan )
        

    def exec(self):
        self._create_dialog('Library Records')
        self._setSize( 600,800)
        self.status.setStyleSheet("font-family: Arial, 'Lucinda Sans', monospaced")
        self.status.setPlainText('')
        
        (shelved, on_loan) = Library.books_locations()
        
        self._tally_categories( shelved, on_loan )

        msg = self._fmt_totals.format(
            len( shelved)+len(on_loan),
            len( shelved),
            len( on_loan ),
            len( self.composer),
            len( self.genre )
        )
        
        
        msg = msg + self._hdr_comp_genre
        composer_keys = sorted( self.composer.keys() )
        genre_keys = sorted( self.genre.keys() )
        loopmax = max( len( composer_keys ), len( genre_keys ))
        for i in range( 0, loopmax ):
            c = composer_keys.pop(0) if len( composer_keys ) else ''
            c_size = "({})".format( self.composer[ c ] ) if c  else ''
            g = genre_keys.pop(0) if len( genre_keys ) else ''
            g_size = "({})".format( self.genre[ g ] ) if  g else ""
            msg = msg +  self._fmt_comp_genre.format( c, c_size, g , g_size )
        msg = msg + self._end_comp_genre

        
        if len( self.book_no_composer ):
            msg += self._hdr_missing.format('Composer')
            for key in self.book_no_composer :
                msg += self._fmt_missing.format( key )
            msg += self._end_missing

        if len( self.book_no_genre ):
            msg += self._hdr_missing.format('Genre')
            for key in self.book_no_genre :
                msg += self._fmt_missing.format( key )
            msg += self._end_missing

        self.status.setHtml( msg )

        self.btns.setEnabled( True )
        self.dlg.exec()