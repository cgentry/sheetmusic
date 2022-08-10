# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from configfile import ConfigFile
from musicutils import toInt
from PySide6.QtWidgets import (
    QApplication, QDialog, QGridLayout, QDialogButtonBox, QTableWidget, 
    QHeaderView, QAbstractItemView, QTableWidgetItem, QLabel,QPushButton,QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QBrush

class TableItem( QTableWidgetItem):
    def __init__(self, name , protected:bool=False):
        super().__init__(name)
        self.setProtected( protected) 
    def setProtected(self, state:bool=False):
        self.protectData = state

    def isProtected(self):
        return self.protectData

class UiBookmarkAdd(QDialog):
    applyContinueText = "Save and add more..."
    labelText = "Enter the <b>Bookmark Name</b>, and either the <b>Book Page</b> or the <b>Page Shown</b>."
    labelTextNoPage = "Enter the <b>Bookmark Name</b>, and the <b>Book Page</b>."

    CANCEL = 0
    SAVE = 1
    SAVE_CONTINUE=2

    def __init__(self, maximumPage=0, pageShownOffset=0, parent=None):
        super(UiBookmarkAdd, self).__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.createBookmarkTable()
        self.createButtons()
        mainLayout = QGridLayout()
        self.label = QLabel()
        mainLayout.addWidget(self.label,0,0)
        mainLayout.addWidget(self.bookmarkTable, 3, 0, 1, 3)
        self.bookmarkTable.setCurrentCell(0,0)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.setSizeGripEnabled(True)

        self.setRange( maximumPage, pageShownOffset )
        self.clear()
        self.adjustSize()

        self.resize(500, 100)

    def clear(self):
        self.values={}
        self.setValues("","","")

    def setRange(self, maximumPage=0, pageShownOffset=0) -> bool:
        if pageShownOffset < 0 or maximumPage <0 or pageShownOffset >= maximumPage:
            return False
        if maximumPage == 0:
            maximumPage = 999
        self.pageShownOffset = pageShownOffset
        self.maximumPage = maximumPage
        self.maxPageShown = self.maximumPage - self.pageShownOffset
        if pageShownOffset == 0:
            self.pageShown.setText("")
            self.pageShown.setFlags(Qt.NoItemFlags)
            self.label.setText(self.labelTextNoPage)
            self.bookmarkTable.setHorizontalHeaderLabels(
                ("Bookmark Name", "Book Page", ""))
        else:
            self.pageShown.setFlags( Qt.ItemIsEditable|Qt.ItemIsEnabled )
            self.label.setText( self.labelText)
            self.bookmarkTable.setHorizontalHeaderLabels(
                ("Bookmark Name", "Book Page", "PageShown"))
        return True


    def createBookmarkTable(self):
        self.bookmarkTable = QTableWidget(1, 3)
        self.bookmarkTable.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.bookmarkTable.clear()
        

        self.bookmarkTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmarkTable.verticalHeader().hide()
        self.bookmarkTable.setShowGrid(True)

        self.bookmarkName = QTableWidgetItem()
        self.bookPage = QTableWidgetItem()
        self.pageShown = QTableWidgetItem()

        self.bookPage.setToolTip("This is the absolute page numer in the book, not the page number displayed")
        self.pageShown.setToolTip("The page number displayed. This is usually not the absolute page number in the book.")

        self.bookmarkName.setTextAlignment( Qt.AlignLeft | Qt.AlignVCenter)
        self.bookPage.setTextAlignment( Qt.AlignRight | Qt.AlignVCenter)
        self.pageShown.setTextAlignment( Qt.AlignRight| Qt.AlignVCenter )

        self.bookmarkName.setFlags(Qt.ItemIsEditable|Qt.ItemIsEnabled)
        self.bookPage.setFlags( Qt.ItemIsEditable|Qt.ItemIsEnabled )
        self.pageShown.setFlags( Qt.ItemIsEditable|Qt.ItemIsEnabled )
        
        self.bookmarkTable.setItem(0, 0, self.bookmarkName)
        self.bookmarkTable.setItem(0, 1, self.bookPage)
        self.bookmarkTable.setItem(0, 2, self.pageShown)
        self.bookmarkTable.adjustSize()

    def setValues(self, name, page, relative):
        self.bookmarkName.setText( name )
        self.bookPage.setText( page )
        self.pageShown.setText( relative )

    def createButtons(self):
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.applyContinueText, QDialogButtonBox.ApplyRole )
        self.buttons.addButton(QDialogButtonBox.Save   )
        self.buttons.addButton( QDialogButtonBox.Cancel )
        
        self.buttons.clicked.connect(self.buttonClicked )

    
    def buttonClicked(self, button:QPushButton ):
        rtnCode = self.CANCEL     
        if button.text() != 'Cancel':
            rtn = self.checkInput()
            if rtn == 0: ## Retry
                self.bookmarkTable.setCurrentCell(0,0)
                return
            if rtn > 0: ## Edit was OK!
                ## 2: save and re-load, 1: save and exit
                rtnCode = ( self.SAVE_CONTINUE if button.text() == self.applyContinueText else self.SAVE)
        self.done(rtnCode)

    def clearBackground(self):
        self.bookmarkName.setBackground( Qt.white)
        self.bookPage.setBackground( Qt.white)
        self.pageShown.setBackground(Qt.white)

    def checkInput(self):
        errors = []
        self.values['bookmark'] = self.bookmarkName.text().strip()
        self.values['bookpage'] = toInt(self.bookPage.text().strip() )
        self.values['pageshown'] = toInt(self.pageShown.text().strip() )
        errorBrush = QBrush()
        errorBrush.setColor( Qt.darkBlue )
        errorBrush.setStyle(Qt.Dense7Pattern)

        self.clearBackground()

        if len(self.values['bookmark']) == 0:
            errors.append("<b>Bookmark Name</b> cannot be blank")
            self.bookmarkName.setBackground(errorBrush)
        
        if self.values['bookpage'] <= 0 and self.values['pageshown'] <=0 :
            errors.append("<b>Book Page</b> or <b>Page Shown</b> must be entered and positive")
            self.bookPage.setBackground(errorBrush)
            self.pageShown.setBackground(errorBrush)
        elif self.values['bookpage'] > 0 and self.values['pageshown'] > 0 :
            errors.append("Enter either <b>Book Page</b> or <b>Page Shown</b>, not both")
            self.bookPage.setBackground(errorBrush)
            self.pageShown.setBackground(errorBrush)
        elif self.values['bookpage'] > self.maximumPage and self.maximumPage > 0:
            errors.append("<b>Book Page</b> is greater than maximum number of pages ({:d})".format(self.maximumPage))
            self.bookPage.setBackground(errorBrush)
        elif self.values['pageshown'] > self.maxPageShown:
            errors.append("<b>Page Shown</b> is beyond the end of the last page of the book ({:d})".format(self.maxPageShown))
            self.pageShown.setBackground(errorBrush)

        if len(errors) > 0:
            mlen = 0
            for msg in errors:
                mlen = max( mlen, len(msg ))
            dlg = QMessageBox()
            dlg.setIcon(QMessageBox.Warning)
            dlg.setText("Invalid values entered.                                              ")
            dlg.setInformativeText("<br/>".join( errors ) )
            dlg.setCheckBox(None)
            dlg.setStandardButtons( QMessageBox.Cancel | QMessageBox.Retry)
            dlg.setDefaultButton(QMessageBox.Retry)
            dlg.findChild(QGridLayout).setColumnMinimumWidth(2, mlen * dlg.fontMetrics().averageCharWidth())
            rtn = dlg.exec()
            if rtn == QMessageBox.Retry:
                return 0 ## Retry
            return -1    ## Cancel
        return 1         ## Edit was OK!


class UiBookmark(QDialog):
    '''
    This is a disposable class (don't keep instances of it alive). This handles goto and destroy
    '''

    COL_NAME = 0
    COL_PAGE_BOOK = 2
    COL_PAGE_SHOWN = 1
    HDR_COL_0 = "Bookmark Name"
    HDR_COL_2 = "Book Page"
    HDR_COL_1 = "Page Shown"

    def __init__(self, parent=None):
        super(UiBookmark, self).__init__(parent)
        self.createBookmarkTable()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.bookmarkTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)

        self.resize(500, 300)

    def clear(self):
        self.bookmarkTable.clear()
        self.bookmarkTable.setHorizontalHeaderLabels(
            (self.HDR_COL_0, self.HDR_COL_1, self.HDR_COL_2))
        self.selectedBookmark = None
        self.selectedPage = None
        self.bookmarkTable.setRowCount(0)

    def createBookmarkTable(self):
        self.bookmarkTable = QTableWidget(0, 3)
        self.bookmarkTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.bookmarkTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmarkTable.verticalHeader().hide()
        self.bookmarkTable.setShowGrid(False)

        self.bookmarkTable.cellClicked.connect(self.clickedBookmark)
        self.bookmarkTable.cellDoubleClicked.connect(
                self.doubleClickedBookmark)

    def clickedBookmark(self, row, column):
        self.selectedRow = row
        item = self.bookmarkTable.item( row,column)
        self.deleteButton.setDisabled( item.isProtected() )
        self.selectedBookmark = self.bookmarkTable.item(row, self.COL_NAME).text()
        self.selectedPage = toInt(self.bookmarkTable.item(row, self.COL_PAGE_BOOK).text())
        self.relativePage = toInt( self.bookmarkTable.item(row,self.COL_PAGE_SHOWN).text())

    def doubleClickedBookmark(self, row, column):
        self.clickedBookmark(row, column)
        self.acceptBookmarkSelect()

    def createButtons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Open | QDialogButtonBox.Cancel| QDialogButtonBox.Discard
        )
        self.buttons.clicked.connect( self.buttonClicked )
        self.buttons.accepted.connect(self.acceptBookmarkSelect)
        self.buttons.rejected.connect(self.cancelBookmarkSelect)
        self.deleteButton = self.buttons.button(QDialogButtonBox.Discard)
        self.deleteButton.setText("Delete")
        self.deleteButton.setObjectName('Delete')

    def buttonClicked(self, button ):
        if button.objectName() == 'Delete' :
            self.action = 'delete'
            self.returnSelect()

    def cancelBookmarkSelect(self):
        self.selectedBookmark = None
        self.selectedPage = None
        self.reject()

    def acceptBookmarkSelect(self):
        self.action = 'go'
        self.returnSelect()

    def returnSelect(self):
        if self.selectedPage:
            self.accept()
        else:
            rtn = QMessageBox.warning(
                None, 
                "",
                "No bookmark selected", 
                QMessageBox.StandardButton.Retry,
                QMessageBox.StandardButton.Cancel
            )
            if rtn == QMessageBox.Cancel:
                self.reject()
            else:
                return

    def _formatPageItem(self, bookmarkName, bookmarkPage, bookmarkRelative=None, protectItem:bool=False):
        name = TableItem(bookmarkName, protectItem)
        name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        page = TableItem("{:>6}".format(bookmarkPage), protectItem)
        page.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        if bookmarkRelative:
            relative = TableItem("{:>6}".format(bookmarkRelative))
        else:
            relative = TableItem("{:>6}".format("-"))
        relative.setProtected( protectItem )
        relative.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return (name, page, relative)

    def _insertBookmarkEntry(self, bookmarkItem):
        row = self.bookmarkTable.rowCount()
        self.bookmarkTable.insertRow(row)
        self.bookmarkTable.setItem(row, self.COL_NAME, bookmarkItem[0])
        self.bookmarkTable.setItem(row, self.COL_PAGE_BOOK, bookmarkItem[1])
        self.bookmarkTable.setItem(row, self.COL_PAGE_SHOWN, bookmarkItem[2])

    def onBookmarkSelected( self):
        pass


    def setBookmarkList(self, fileObject):
        self.setModal(True)
        self.clear()
        self.setWindowTitle("Select Bookmark for " +  fileObject.getBookTitle())

        bookmarkItem = self._formatPageItem(
                "First Page", 
                str(fileObject.getContentStartingPage()), 
                protectItem=True
        )
        self._insertBookmarkEntry(bookmarkItem)

        if fileObject.getContentStartingPage() != fileObject.getRelativePageOffset():
            bookmarkItem = self._formatPageItem(
                    "Book Numbering Starts", str(fileObject.getRelativePageOffset()),
                    "1", 
                    protectItem=True
                )
            self._insertBookmarkEntry(bookmarkItem)
    
        bookmarks = fileObject.getAllBookmarks()
        for bookmark in bookmarks:
            bookmarkItem = self._formatPageItem(
                bookmark[ConfigFile.KEY_PNAME], 
                bookmark[ConfigFile.KEY_PAGE_CONTENT],
                bookmark[ConfigFile.KEY_PAGES_START])
            self._insertBookmarkEntry(bookmarkItem)
        self.bookmarkTable.sortItems(self.COL_PAGE_SHOWN)

if __name__ == "__main__":
    app = QApplication()
    window = UiBookmarkAdd()
    window.setValues("","10","")
    window.setRange(100,10)
    window.show()
    app.exec()
    rtn = window.result()
    if rtn == UiBookmarkAdd.SAVE:
        print("... SAVE")
    if rtn == UiBookmarkAdd.SAVE_CONTINUE:
        print("... SAVE and CONTINUE")
    if rtn == UiBookmarkAdd.CANCEL:
        print("... CANCEL")
    sys.exit(0)