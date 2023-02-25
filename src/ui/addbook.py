from PySide6.QtWidgets  import QFileDialog, QMessageBox
from qdil.book          import DilBook
from qdil.preferences   import DilPreferences
from qdb.keys           import DbKeys, BOOK
from ui.properties      import UiProperties

class UiAddBook( ):
    def __init__(self):
        pass

    def import_book( self )->bool:
        book = DilBook()
        ( book_info , error ) = book.import_one_book( UiAddBook.prompt_import_directory('Existing Book'))
        if error:
            UiAddBook.error_message( error )
            return False
        
        property_editor = UiProperties()
        property_editor.set_properties( self.book.get_properties() )
        if property_editor.exec():
            self.book.update_properties( property_editor.changes )
        
        book.open( book_info[ BOOK.book ])
        property_editor = UiProperties()
        property_editor.set_properties(book.get_properties())
        if property_editor.exec():
            self.book.update_properties( property_editor.changes )

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

