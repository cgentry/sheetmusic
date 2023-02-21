from ui.simpledialog import SimpleDialog
from util.toollist import GenerateImportList
from util.toolconvert import UiImportSetting
from PySide6.QtWidgets  import ( QApplication )

from qdb.dbconn import DbConn
from qdil.preferences import SystemPreferences

if __name__ == "__main__":
    sy = SystemPreferences()
    dbLocation = sy.getPathDB()          # Fetch the system settings
    mainDirectory = sy.getDirectory()       # Get directory

    app = QApplication([])
    DbConn.openDB(dbLocation)

    tst = UiImportSetting()
    tst.pick_import()
