from PySide6.QtWidgets  import QFileDialog, QMessageBox
from qdb.dbsystem       import DbSystem
from qdil.preferences   import DilPreferences
from qdb.keys           import DbKeys

class AddBookDirectory( ):
    def __init__(self):
        pass
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
        msg = "{}\nDo you want to add information to the added book?".format( message )
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

