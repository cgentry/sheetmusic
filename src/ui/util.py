# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file is part of Sheetmusic. 

# Sheetmusic is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox


def centerWidgetOnScreen( widget:QWidget):
    centerPoint = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    fg = widget.frameGeometry()
    fg.moveCenter(centerPoint)
    widget.move(fg.topLeft())
    ##
    widget.show()

def not_yet_implemented( **kwargs ):
    QMessageBox.information(
        None,
        'Not implemented',
        "Sorry, but that feature has not yet been implemented",
        QMessageBox.Ok
    )