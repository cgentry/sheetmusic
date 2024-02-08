"""
User Interface : library info and cleanup routines

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import shutil
import os
import sys

from PySide6.QtWidgets import (
    QDialog,       QDialogButtonBox,
    QVBoxLayout,   QTextEdit,
    QMessageBox
)
from PySide6.QtCore import QSize

from qdb.fields.book import BookField
from qdb.dbbook import  DbBook
from qdil.preferences import DilPreferences
from util.library import Library
from ui.util import center_on_screen

class UiOutputMixin():
    """ Simple mixin that Creates a dialog box
    sets a size, text and simple buttons (OK)"""

    def set_size( self , h:int, w:int ):
        """Set the dize of the dialog window

        Args:
            h (int): minimum height
            w (int): minimum width
        """
        self.dlg.setMinimumSize( h, w )
        self.dlg.show()
        center_on_screen( self.dlg )

    def size( self )->QSize:
        """Get current size of dialog box

        Returns:
            QSize: Standard QT size
        """
        return self.dlg.size()

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

    def _button_pressed( self, _ ):
        self.dlg.accept()

class UiLibraryConsolidate( UiOutputMixin):
    """Handle Consolidate contents of other directories
    into sheetmusic library(directory)

    Args:
        UiOutputMixin (object): Base dialog
    """
    def __init__(self):
        self.sheetmusic_dir = DilPreferences().dbdirectory

    def exec(self):
        """confirm operation, then execute the copy
        """
        if QMessageBox.Cancel == QMessageBox.question(
            None,
            'Consolidate Library',
            'This will copy content from other directories ' +
            f'into the sheetmusic directory:\n{self.sheetmusic_dir}.',
            QMessageBox.Cancel, QMessageBox.Ok
        ):
            return
        self.process_copy()


    def process_copy(self)->int:
        """ Consolidate one library into another """
        not_in_lib = Library.books_not_in_library()
        if len( not_in_lib ) == 0 :
            QMessageBox.information(
                None,
                'Consolidate Library',
                "All entries are stored in sheetmusic directory.\nNothing to do.",
                QMessageBox.Ok
            )
            return None

        self._create_dialog('Consolidate Music Library')
        self.dlg.set_size( 800, 800 )

        dbbook = DbBook()

        sys.addaudithook( self.track_copy )
        for book in not_in_lib:
            book_name = book[ BookField.BOOK ]
            self.status.append( f"""\nBOOK: {book_name}""" )

            lib_book = dbbook.getbook( book_name)
            if lib_book is None:
                #msg = f"""\n\tBook not found in library. Skipping.\n"""
                continue

            loc = book[BookField.LOCATION]
            loc_target_dir = os.path.basename( os.path.basename( loc ))
            sheetmusic = os.path.join( self.sheetmusic_dir , loc_target_dir )

            shutil.copytree( loc ,  sheetmusic  )
            if os.path.isdir( sheetmusic ):
                dbbook.update( book=book_name , location=sheetmusic )
                self.status.append("""\tLibrary updated.""")
            else:
                self.status.append(
                    """\tERROR: Directory doesn't exist. Copy failed. Not updating library.""" )
        self.btns.setEnabled( True )
        return self.dlg.exec()

    def track_copy( self, event, args   ):
        """Called by the sys.audithook during a copy operation

        Args:
            event (str): Name of trigger
            args (list):
                arg[0]: source file
                arg[1]: destination file
        """
        if event == "shutil.copytree" :
            self.status.append(
                f"\n\tFILE: {args[0]}\n\tDEST: {args[1]}")


class UiLibraryCheck():
    """Perform a check of the library to see if all
    books are within the library or if they are 'lost'

    """
    DELETE = 0
    LEAVE  = 1

    def __init__(self) -> None:
        self.dlg = QDialog()
        self.status = QTextEdit()
        self.btns = QDialogButtonBox()

    def _create_dialog(self)->QDialog:
        layout = QVBoxLayout()

        self.dlg.setWindowTitle('Consolidate Music Library')

        self.status.setReadOnly(True)

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

    def handle_bad_lib_entries( self,
            in_lib_no_folder:list[dict],
            shelved:list )->None:
        """Loop through the list and handle books
        that don't have a folder. Determine if they should
        be deleted or not

        Args:
            in_lib_no_folder (list[dict]):
                List of dictionaries with BookField keys
            shelved (list): List of books in database
        """
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
            self.status.insertHtml(
                f"<p><b>BOOK: </b>{book[BookField.BOOK]}<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+
                f"Folder: {book[BookField.LOCATION]}</p><br/>")
        self.status.insertHtml(
                f"<br/>Total library entries: {len( shelved)}<br/>"+
                f"Total problem entries: {len(in_lib_no_folder)}<br/>Delete library entries?")
        if UiLibraryCheck.DELETE == self.dlg.exec():
            dbbook = DbBook()
            for book in in_lib_no_folder:
                dbbook.del_book( book[ BookField.BOOK ])

    def handle_extra_folders( self,
            folder_not_in_lib:list ,
            all_folders:list ):
        """Handle folders that aren't located in library

        Args:
            folder_not_in_lib (list): Folders not in db library
            all_folders (list): All folders
        """
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
            self.status.insertHtml( f"<p><b>Folder: </b>folder{folder}</p><br/>")
        self.status.insertHtml(
                f"<br/>Total folder entries: {len(all_folders)}<br/>" +
                f"Total problem foldres: {len(folder_not_in_lib)}<br/>Delete folders?")

        if UiLibraryCheck.DELETE == self.dlg.exec():
            for folder in folder_not_in_lib:
                shutil.rmtree( folder )

    def exec(self):
        """Find differences and prompt user for action
        """
        (shelved, off_side) = Library.books_locations()
        all_folders = Library.folders()

        #find differences
        in_lib_no_folder = []
        folder_not_in_lib = [] # FOLDER, Not in lib

        book_folders = [ book[ BookField.LOCATION ] for book in shelved ]

        for book in shelved:
            if not book[ BookField.LOCATION ] in all_folders :
                in_lib_no_folder.append( book )

        for book in off_side :
            if not os.path.isdir( book[ BookField.LOCATION ]):
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
    """ Show library statistics to user in dialog box:
            Total books
            Books in other folders than library folders
            Composers
            Genres"""

    FMT_TOTALS= """<table>
            <tr><th colspan='2'>Summary</th></tr>
            <tr><th colspan='2'>========================</th></tr>
            <tr><td>Total books                      &nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Books stored in sheetmusic folder&nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Books stored in other folders    &nbsp;&nbsp;</td><td>{:4d}</td></tr>
            <tr><td>Composers                        &nbsp;&nbsp;</td><td>{}</td></tr>
            <tr><td>Genres                           &nbsp;&nbsp;</td><td>{}</td><tr>
            </table><br/>"""
    HDR_COMP_GENRE="""<table 'width:100%'>
            <tr><th>Composers</th><th>Genres</th></tr>
            <tr><th>========================</th><th>========================</</th></tr>"""
    FMT_COMP_GENRE="""<tr><td>{}&nbsp;&nbsp;{}</td><td>{}&nbsp;&nbsp;{}</td></tr>"""
    END_COMP_GENRE="</table><br/><br/>"

    HDR_MISSING="""<table 'width:100%'>
            <tr><th>Books with no {}.</th></tr>
            <tr><th>========================</th>"""
    FMT_MISSING="""<tr><td>{}</td></tr>"""
    END_MISSING="</table><br/><br/>"

    def __init__(self):
        self.genre = {}
        self.composer = {}
        self.book_no_genre = []
        self.book_no_composer = []

    def _tally_subcat( self, catalog:dict ):
        for book in catalog :
            c = book[ BookField.COMPOSER ]
            g = book[ BookField.GENRE ]

            if not c :
                self.book_no_composer.append( book[BookField.BOOK ])
                c = '(not set)'

            if not g:
                self.book_no_genre.append( book[BookField.BOOK])
                g = '(not set)'

            self.composer[c] = self.composer[c] + 1 if c in self.composer else 1
            self.genre[g]    = self.genre[g]    + 1 if g in self.genre    else 1

    def _tally_categories(self, shelved:dict, on_loan:dict):
        self._tally_subcat( shelved )
        self._tally_subcat( on_loan )


    def exec(self):
        """ Execute the dialog and display the results """
        self._create_dialog('Library Records')
        self.set_size( 600,800)
        self.status.setStyleSheet("font-family: Arial, 'Lucinda Sans', monospaced")
        self.status.setPlainText('')

        (shelved, on_loan) = Library.books_locations()

        self._tally_categories( shelved, on_loan )

        msg = self.FMT_TOTALS.format(
            len( shelved)+len(on_loan),
            len( shelved),
            len( on_loan ),
            len( self.composer),
            len( self.genre )
        )


        msg = msg + self.HDR_COMP_GENRE
        composer_keys = sorted( self.composer.keys() )
        genre_keys = sorted( self.genre.keys() )
        loopmax = max( len( composer_keys ), len( genre_keys ))
        for _ in range( 0, loopmax ):
            c = composer_keys.pop(0) if len( composer_keys ) else ''
            c_size = f"({self.composer[ c ]})"  if c  else ''
            g = genre_keys.pop(0) if len( genre_keys ) else ''
            g_size = "({self.genre[ g ]})" if  g else ""
            msg = msg +  self.FMT_COMP_GENRE.format( c, c_size, g , g_size )
        msg = msg + self.END_COMP_GENRE


        if self.book_no_composer :
            msg += self.HDR_MISSING.format('Composer')
            for key in self.book_no_composer :
                msg += self.FMT_MISSING.format( key )
            msg += self.END_MISSING
        if self.book_no_genre :
            msg += self.HDR_MISSING.format('Genre')
            for key in self.book_no_genre :
                msg += self.FMT_MISSING.format( key )
            msg += self.END_MISSING

        self.status.setHtml( msg )

        self.btns.setEnabled( True )
        self.dlg.exec()
