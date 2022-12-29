####
#### TEST BED APPLICATION - doesn't really do anything
####
import sys
from qdb.keys import BOOK, DbKeys
from qdb.setup import Setup
from qdb.dbconn import DbConn
from PySide6.QtWidgets import QApplication
from ui.file import Openfile
from qdil.preferences import SystemPreferences

if __name__ == "__main__":
    """ Give it a try"""
    location = SystemPreferences().getPathDB()              # Fetch the system settings
    DbConn().openDB( location )                             # Open up the link to the database
    s = Setup(location)                                     # Make sure the database is initialised
    s.createTables()
    s.initData()  
    
    app = QApplication()
    window = Openfile()
    window.exec()
    print("\nshow")
    print( window.bookSelected )
    app.quit()
    sys.exit(app.exec())