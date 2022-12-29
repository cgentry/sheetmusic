
from PySide6.QtWidgets  import QApplication
from ui.selectitems     import SelectItems
import sys

if __name__ == "__main__":
    lst = { "Entry one": "value1", "Entry two": "value2"}
    app = QApplication()
    items = SelectItems("Books already processed","Select books you want to re-process")
    items.setData( lst )
    items.setButtonText("OK","Ignore")
    items.exec()
    print( "Checked:"   ,items.getCheckedList() )
    print( "Unchecked:", items.getUncheckedList() )
    app.quit()
    sys.exit(0)