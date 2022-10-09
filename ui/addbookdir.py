from PySide6.QtWidgets import QFileDialog, QMessageBox
from db.dbsystem       import DbSystem
from dil.preferences   import DilPreferences
from db.keys           import DbKeys

class AddBookDirectory( ):
    def __init__(self):
        pass

    def promptForDirectoryToScan(self)->str:
        """
            Prompt the user for a directory to scan for new/recovver books
            Returns directory name
        """
        defaultMusic = DilPreferences().getValue( DbKeys.SETTING_DEFAULT_PATH_MUSIC )
        type = DilPreferences().getValue(DbKeys.SETTING_FILE_TYPE, 'png')
        newDirName = QFileDialog.getExistingDirectory(
            None,
            "Scan Directory for Music",
            dir=defaultMusic ,
            options=QFileDialog.Option.ShowDirsOnly)
        return newDirName
    
    def questionAddDetail(self, message:str )->bool:
        """
            Prompt the user to see if he wants to add detail
        """
        msg = "{}\nDo you want to add information to the added books?".format( message )
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

