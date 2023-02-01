from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget


def centerWidgetOnScreen( widget:QWidget):
    centerPoint = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    fg = widget.frameGeometry()
    fg.moveCenter(centerPoint)
    widget.move(fg.topLeft())
    ##
    widget.show()