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

from PySide6.QtWidgets  import QFileDialog, QMessageBox
from qdil.book          import DilBook
from qdil.preferences   import DilPreferences
from qdb.keys           import DbKeys, BOOK
from qdb.mixin.tomlbook  import MixinTomlBook
from ui.properties      import UiPropertiesImages

class UiAddBook( MixinTomlBook ):
    def __init__(self):
        pass


    def import_book( self )->bool:
        """ Prompt user for a book directory and import into the system
        
            This will also write out a TOML file with properties, in case
            they want to re-import the file
        """
        book = DilBook()
        book_dir = UiAddBook.prompt_import_directory('Existing Book')
        ( book_info , error ) = book.import_one_book( book_dir )
        if error:
            UiAddBook.error_message( error )
            return False
        
        book.open( book_info[ BOOK.book ])
        property_editor = UiPropertiesImages()
        property_editor.set_properties(book.get_properties())
        if property_editor.exec():
            book.update_properties( property_editor.changes )
        if property_editor.save_toml_file():
            self.write_toml_properties( book_dir , book.get_properties() )

    def import_directory(self, newdir ):
        """
        Import a directory of directories holding PNG images into the database
            
        This will interface with:
            import_directory:   get the directory to check out
            prompt_add_detail:  Confirm they want to add detail
            Prompt to see if they want us to correct new entries.
            Get all the book information
        """
        book = DilBook()
        ( status , books_added , msg ) = book.import_directory( UiAddBook.prompt_import_directory() )
        if len( books_added ) > 0:
            if UiAddBook.prompt_add_detail( 'Added {} books'.format( len( books_added )) ):
                for book_info in books_added:
                    book.open( book_info[ BOOK.book ])
                    property_editor = UiProperties()
                    property_editor.set_properties(book.get_properties())
                    if property_editor.exec():
                        self.book.update_properties( property_editor.changes )
        else:
            if not status:
                UiAddBook.error_message( msg )


    @staticmethod
    def prompt_import_directory( header='Scan Directory for Music')->str:
        """
            Prompt the user for a directory to scan for new/recover books
            Returns directory name
        """
        defaultMusic = DilPreferences().getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        type = DilPreferences().getValue(DbKeys.SETTING_FILE_TYPE, 'png')
        new_directory_name = QFileDialog.getExistingDirectory(
            None,
            "Scan Directory for Music",
            dir=defaultMusic ,
            options=QFileDialog.Option.ShowDirsOnly)
        return new_directory_name
    
    @staticmethod
    def error_message( message:str , info:str=None, retry=False, error=False)->int:
        qmsg = QMessageBox()
        qmsg.setText( message )

        if error:
            qmsg.setIcon(QMessageBox.Critical)
        else:
            qmsg.setIcon(QMessageBox.Warning)
        if info:
            qmsg.setInformativeText( info )
        qmsg.addButton( QMessageBox.Cancel )
        if retry:
            qmsg.addButton( QMessageBox.Retry)
        return qmsg.exec()


    @staticmethod
    def prompt_add_detail( message:str )->bool:
        """
            Prompt the user to see if he wants to add detail
        """
        msg = "{}\nUpdate properties?".format( message )
        return (
            QMessageBox.Yes == QMessageBox.question(
                None,
                "",
                msg,
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No)
        )

    def getDetail( self, newBookList ):
        pass

