""" Simple program that for running scriptfiles.

Not meant for general usage, but more for testing

"""

from PySide6.QtWidgets  import ( QApplication )
from util.toollist import GenerateImportList

if __name__ == "__main__":
    app = QApplication([])

    gel = GenerateImportList()
    for key, tool in gel.list().items():
        print( 'Title: {key}'  )
        for tool_key , entry in tool.todict().items():
            print( f'\tID: {tool_key:15s} Value: {entry}')
