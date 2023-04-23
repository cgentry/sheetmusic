
import sys
from util.toolconvert import UiImportSetting
from qdil.book import DilBook
from PySide6.QtWidgets import QApplication
from qdil.preferences import SystemPreferences
from qdb.dbconn import DbConn
if __name__ == "__main__":
    sy = SystemPreferences()
    dbLocation = sy.getPathDB()          # Fetch the system settings
    mainDirectory = sy.getDirectory()       # Get directory
    DbConn.openDB(dbLocation)

    app = QApplication()
    converter = DilBook()
    converter.import_book()
    app.quit()
    sys.exit(0)