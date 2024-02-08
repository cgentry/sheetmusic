"""
User Interface : Adding books

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtWidgets  import QFileDialog, QMessageBox
from qdil.book          import DilBook
from qdil.preferences   import DilPreferences
from qdb.keys           import DbKeys
from qdb.fields.book import BookField
from qdb.mixin.tomlbook import MixinTomlBook
from ui.properties      import UiPropertiesImages, UiProperties

class UiAddBook( MixinTomlBook ):
    """ Handle all the QT interface requirements for books

    Args:
        MixinTomlBook (class): Interface to TOML file handler
    """

    def import_book( self )->bool:
        """Prompt user for a book directory and import into the system

            This will also write out a TOML file with properties, in case
            they want to re-import the file

        Returns:
            bool: True if imported, False if not
        """
        dlbook = DilBook()
        book_dir = UiAddBook.prompt_import_directory('Existing Book')
        ( book_info , error ) = dlbook.import_one_book( book_dir )
        if error:
            UiAddBook.error_message( error )
            return False

        dlbook.open( book_info[ BookField.BOOK ])
        property_editor = UiPropertiesImages()
        property_editor.set_properties(dlbook.get_properties())
        if property_editor.exec():
            dlbook.update_properties( property_editor.changes )
        if property_editor.save_toml_file():
            self.write_toml_properties( book_dir , dlbook.get_properties() )
        return True

    def import_directory(self ):
        """
        Import a directory of directories holding PNG images into the database

        This will interface with:
            import_directory:   get the directory to check out
            prompt_add_detail:  Confirm they want to add detail
            Prompt to see if they want us to correct new entries.
            Get all the book information
        """
        dlbook = DilBook()
        ( status , books_added , msg ) = dlbook.import_directory(
                    UiAddBook.prompt_import_directory() )
        if len( books_added ) > 0:
            if UiAddBook.prompt_add_detail( f'Added {len( books_added )} books' ):
                for book_info in books_added:
                    dlbook.open( book_info[ BookField.BOOK ])
                    property_editor = UiProperties()
                    property_editor.set_properties(dlbook.get_properties())
                    if property_editor.exec():
                        dlbook.update_properties( property_editor.changes )
        else:
            if not status:
                UiAddBook.error_message( msg )


    @staticmethod
    def prompt_import_directory( header='Scan Directory for Music')->str:
        """
            Prompt the user for a directory to scan for new/recover books
            Returns directory name
        """
        default_music_path = DilPreferences().get_value( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        return QFileDialog.getExistingDirectory(
            None,
            header,
            dir=default_music_path ,
            options=QFileDialog.Option.ShowDirsOnly )

    @staticmethod
    def error_message( message:str , info:str=None, retry=False, error=False)->int:
        """ Format a general error message text box on the screen"""
        qmsg_box = QMessageBox()
        qmsg_box.setText( message )

        if error:
            qmsg_box.setIcon(QMessageBox.Critical)
        else:
            qmsg_box.setIcon(QMessageBox.Warning)
        if info:
            qmsg_box.setInformativeText( info )
        qmsg_box.addButton( QMessageBox.Cancel )
        if retry:
            qmsg_box.addButton( QMessageBox.Retry)
        return qmsg_box.exec()


    @staticmethod
    def prompt_add_detail( message:str )->bool:
        """
            Prompt the user to see if he wants to add detail
        """
        return (
            QMessageBox.Yes == QMessageBox.question(
                None,
                "",
                f"{message}\nUpdate properties?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No)
        )

    # def get_detail( self, new_book_list ):
    #     """ dummy function"""
    #     new_book_list = new_book_list
    #     pass
