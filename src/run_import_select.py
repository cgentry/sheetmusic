""" Just a program to test functions"""

from PySide6.QtWidgets  import ( QApplication )

from util.toolconvert import UiImportSetting
from qdb.dbconn import DbConn
from qdil.preferences import SystemPreferences

if __name__ == "__main__":
    syspref = SystemPreferences()
    dbLocation = syspref.dbpath          # Fetch the system settings
    mainDirectory = syspref.dbdir       # Get directory

    app = QApplication([])
    DbConn.open_db(dbLocation)

    tst = UiImportSetting()
    tst.pick_import()
