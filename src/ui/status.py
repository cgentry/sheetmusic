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

from PySide6.QtWidgets import (
    QPushButton, QDialog, QGridLayout, QVBoxLayout, QLayout, QDialogButtonBox, QApplication, QLabel, QProgressBar)
from PySide6.QtCore import Qt


class UiStatus(QDialog):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(75)
        self.setMinimumWidth(500)
        self._cancel = False

        mainLayout = QGridLayout()
        self._create_widgets(mainLayout)
        self._create_buttons(mainLayout)

        self.setLayout(mainLayout)
        self.modal = True
        self.show()

    def _create_widgets(self, layout: QLayout):
        self.lblHeading = QLabel()
        self.lblHeading.setStyleSheet(
            'font-weight: bolder;text-align: center;')
        self.lblHeading.setTextFormat(Qt.TextFormat.PlainText)
        self.lblInformation = QLabel()
        self.lblInformation.setStyleSheet(
            'font-weight: bolder;text-align: center;')
        self.lblInformation.setTextFormat(Qt.TextFormat.PlainText)
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setValue(0)

        layout.addWidget(self.lblHeading)
        layout.addWidget(self.lblInformation)
        layout.addWidget(self.progress)

    def _create_buttons(self, layout: QLayout) -> None:
        self.buttons = QDialogButtonBox()
        self.button = QPushButton('Cancel' )
        self.buttons.addButton(self.button, QDialogButtonBox.RejectRole) 
        self.buttons.clicked.connect(self._close)
        layout.addWidget(self.buttons)

    @property
    def title(self) -> str:
        return self.lblHeading.text()

    @title.setter
    def title(self, title: str) -> None:
        self.lblHeading.setText(title)
        QApplication.processEvents()

    @property
    def information(self) -> str:
        self.lblInformation.text()

    @information.setter
    def information(self, information: str) -> None:
        self.lblInformation.setText(information)
        QApplication.processEvents()

    @property
    def minimum(self) -> int:
        return self.progress.minimum()

    @property
    def maximum(self) -> int:
        return self.progress.maximum

    @minimum.setter
    def minimum(self, minimum: int = 0) -> None:
        self.progress.setMinimum(minimum)
        QApplication.processEvents()

    @maximum.setter
    def maximum(self, maximum: int) -> None:
        maximum = maximum if self.progress.minimum() <= maximum else self.progress.minimum()
        self.progress.setMaximum(maximum)
        QApplication.processEvents()

    @property
    def buttonText(self) -> str:
        return self.button.text()

    @buttonText.setter
    def buttonText(self, text: str):
        self.button.setText(text)

    def setRange(self, minimum: int, maximum: int) -> None:
        self.progress.setMinimum(minimum)
        self.progress.setMaximum(maximum)

    def setValue(self, value: int) -> None:
        self.progress.setValue(value)

    def clear(self) -> None:
        self.lblHeading.clear()
        self.lblInformation.clear()
        self.progress.setValue(0)
        QApplication.processEvents()

    def wasCanceled(self) -> bool:
        return self._cancel

    def _close(self, button):
        self._cancel = True
        if self.button.text() == 'Close':
            self.rejected
            self.close()


class UsingStatusDialog:
    def __init__(self, title='Import Books', maxfiles: int = 0):
        self.title = title
        self.maxfiles = 0

    def __enter__(self):
        self._dlg = UiStatus()
        self._dlg.title = self.title
        self._dlg.maximum = self.maxfiles
        self._dlg.show()
        return self._dlg

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._dlg.close()
