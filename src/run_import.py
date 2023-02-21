from ui.simpledialog import SimpleDialog
from util.toollist import GenerateImportList
from PySide6.QtWidgets  import ( QApplication )
import sys

if __name__ == "__main__":
    app = QApplication([])

    gel = GenerateImportList()
    for key, tool in gel.list().items():
        print( 'Title: {}'.format( key ) )
        for tool_key , entry in tool.todict().items():
            print( '\tID: {:15s} Value: {}'.format( tool_key , entry))
