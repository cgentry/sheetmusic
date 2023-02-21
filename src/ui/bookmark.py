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
import sys

from PySide6.QtWidgets import (
    QApplication, QDialog, QGridLayout, QDialogButtonBox, QTableWidget, QLineEdit, QCheckBox,QVBoxLayout,
    QHeaderView, QAbstractItemView, QTableWidgetItem, QLabel,QPushButton,QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QIntValidator

from qdb.keys     import BOOKMARK
from util.convert import toInt

class TableItem( QTableWidgetItem):
    def __init__(self, name , protected:bool=False):
        super().__init__(name)
        self.setProtected( protected) 
    def setProtected(self, state:bool=False):
        self.protectData = state

    def isProtected(self):
        return self.protectData

class UiBookmarkBase(QDialog):

    HDR_COL_0 = "Bookmark Name"
    HDR_COL_1 = "Page Shown"
    HDR_COL_2 = "Book Page"
    COL_NAME = 0
    COL_PAGE_SHOWN = 1
    COL_PAGE_BOOK = 2
    def __init__(self):
        super().__init__()

    def createBookmarkTable(self, columns=3):
        self.bookmarkTable = QTableWidget(1, columns )
        self.bookmarkTable.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.bookmarkTable.clear()
        
        self.bookmarkTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmarkTable.verticalHeader().hide()
        self.bookmarkTable.setShowGrid(True)

        self.bookmarkName = QTableWidgetItem()
        self.bookPage     = QTableWidgetItem()
        self.pageShown    = QTableWidgetItem()

        self.bookPage.setToolTip("This is the absolute page numer in the book, not the page number displayed")
        self.pageShown.setToolTip("The page number displayed. This is usually not the absolute page number in the book.")

        self.bookmarkName.setTextAlignment( Qt.AlignLeft | Qt.AlignVCenter)
        self.bookPage.setTextAlignment(     Qt.AlignRight | Qt.AlignVCenter)
        self.pageShown.setTextAlignment(    Qt.AlignRight| Qt.AlignVCenter )

        self.bookmarkName.setFlags(Qt.ItemIsEditable|Qt.ItemIsEnabled)
        self.bookPage.setFlags(    Qt.ItemIsEditable|Qt.ItemIsEnabled )
        self.pageShown.setFlags(   Qt.ItemIsEditable|Qt.ItemIsEnabled )
        
        self.bookmarkTable.setItem(0, self.COL_NAME, self.bookmarkName)
        self.bookmarkTable.setItem(0, self.COL_PAGE_BOOK, self.bookPage)
        self.bookmarkTable.setItem(0, self.COL_PAGE_SHOWN, self.pageShown)
        self.bookmarkTable.adjustSize()

        self.bookmarkTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bookmarkTable.verticalHeader().hide()
        self.bookmarkTable.setShowGrid(False)

    def setValues(self, name:str, page:int, relative:int):
        self.bookmarkName.setText( name )
        self.bookPage.setText( page )
        self.pageShown.setText( relative )

    def clear(self):
        self.bookmarkTable.clear()
        self.bookmarkTable.setHorizontalHeaderLabels(
            (self.HDR_COL_0, self.HDR_COL_1, self.HDR_COL_2 ))

class UiBookmarkSingle(QDialog):
    bookPageLabelChecked   = 'Book Page Number Shown'
    bookPageLabelUnchecked = 'Book Page Number      '
    BtnCancel = 'Cancel'
    BtnSave   = 'Save'

    def __init__(self, parent=None, heading:str=None, totalPages:int=None, numberingOffset:int=None):
        super().__init__()

        self.setup( )
        self.setTotalPages( totalPages )
        self.setNumberingOffset( numberingOffset )

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.createHeading())
        mainLayout.addLayout(self.createGridLayout())
        mainLayout.addWidget(self.createButtons())
        self.setLayout(mainLayout)
        self.setSizeGripEnabled(True)

        self.setHeading( heading )
        
        self.resize(500,200)
        self.changes ={}

    def setup(self):
        self.changes = {}
        self.numberingOffset = None
        self.pageValid = QIntValidator( 1, 999 , self)

    def setTotalPages(self, totalPages:int=None ):
        if totalPages is not None:
            self.pageValid.setTop( totalPages )

    def setNumberingOffset(self, pageOffset:int=None):
        if pageOffset is not None:
            self.numberingOffset = pageOffset

    def setFields( self, name:str , page:int, isRelative:bool=False):
        self.bookmarkName.setText( name )
        if self.numberingOffset is not None:
            self.pageShown.setChecked( isRelative )
            self.pageShown.setEnabled( True )
        else:
            self.pageShown.setChecked( False )
            self.pageShown.setEnabled( False )
        self.bookPage.setText( str(page) )

    def createHeading(self)->QLabel:
        self.heading = QLabel()
        return self.heading

    def createGridLayout(self)->QGridLayout:
        gridLayout = QGridLayout()
        row = 0
        row = self.createName(  gridLayout, row )
        row = self.createPage(  gridLayout, row )
        row = self.createShown( gridLayout, row )
        row = self.createError( gridLayout, row )
        return gridLayout

    def createName(self,  grid:QGridLayout, row)->int:
        self.bookmarkName = QLineEdit()
        grid.addWidget( QLabel("Bookmark Name"), row, 0 )
        grid.addWidget( self.bookmarkName , row, 1)
        return row+1

    def createPage(self ,grid:QGridLayout, row)->int:
        self.bookPage = QLineEdit()
        self.bookPage.setValidator( self.pageValid )
        self.bookPage.textChanged.connect( self.pageNumberChanged )
        self.bookPageLabel = QLabel( self.bookPageLabelUnchecked )
        grid.addWidget( self.bookPageLabel, row, 0 )
        grid.addWidget( self.bookPage , row, 1 )
        return row+1

    def createShown(self,grid:QGridLayout, row)->int:
        self.pageShown = QCheckBox()
        self.pageShown.setText("Page number is page shown.")
        self.pageShown.setCheckable( self.numberingOffset is not None )
        if self.numberingOffset is not None:
            self.pageShown.setFocusPolicy( Qt.StrongFocus )
        self.pageShown.stateChanged.connect( self.checkboxStateChanged )
        grid.addWidget( self.pageShown, row, 1 )
        return row+1

    def createError(self, grid:QGridLayout, row:int)->int:
        self.errorMessage = QLabel()
        grid.addWidget( self.errorMessage , row, 1 )
        return row+1

    def error( self, message:str=None):
        if message is None:
            self.errorMessage.clear()
        else:
            self.errorMessage.setText( message )
    
    def setHeading( self, heading:str=None):
        if heading is None:
            self.heading.clear()
        else:
            self.heading.setText( heading )

    def getChanges(self)->dict:
        self.changes = { BOOKMARK.name  : self.bookmarkName.text().strip() }
        page_number = toInt( self.bookPage.text().strip() , 0 )
        
        ## now fix up page depending on if they checked the box
        ## (They can't check it if there is no page offset)
        if self.pageShown.checkState() == Qt.Checked:
            page_number += self.numberingOffset -1 
        if page_number > self.pageValid.top():
            page_number = self.pageValid.top()
        self.changes[ BOOKMARK.page ] = page_number
        return self.changes

    def clear(self):
        self.changes={}
        self.pageShown.setChecked( False )
        self.bookmarkName.clear()
        self.bookPage.clear()

    def hasAcceptableInput(self)->bool:
        if not self.bookPage.hasAcceptableInput():
            self.error("ERROR: Page must be between 1 and {}".format( self.pageValid.top() ))
            return False
        self.getChanges()
        if len( self.changes[ BOOKMARK.name ]) <= 0 :
            self.error("ERROR: Name must be entered")
            return False
        self.error()
        return True

    def checkboxStateChanged( self, state ):
        if state == Qt.Checked:
            self.bookPageLabel.setText(self.bookPageLabelChecked)
            self.pageNumberChanged( self.bookPage.text() )
        else:
            self.bookPageLabel.setText( self.bookPageLabelUnchecked )
            self.error()

    def pageNumberChanged( self , pageStr:str):
        if self.pageShown.checkState() == Qt.Checked :
            page = toInt( pageStr, 1 ) + self.numberingOffset-1
            self.error( "(Book page is {})".format(page  ))

    def actionButtonClicked(self, button ):
        if self.button.text() == 'Cancel' :
            self.changes = {}
            self.reject()

        if self.hasAcceptableInput():
            self.accept()
    
    ## VIRTUAL FUNCTIONS
    def createButtons(self)->QDialogButtonBox:
        raise NotImplementedError()

    def setupData(self):
        raise NotImplementedError()

class UiBookmarkEdit( UiBookmarkSingle ):
    """
        UiBookmarkEdit will edit one entry """
    def __init__(self, totalPages:int=None, numberingOffset:int=None, parent=None):
        super().__init__( totalPages=totalPages, numberingOffset=numberingOffset, parent=parent)

    def setupData( self, bookmarkEntry:dict ):
        ## figure out if this could be a relative page
        page = bookmarkEntry[ BOOKMARK.page ]
        isRelative = False
        if self.numberingOffset is not None:
            if page >= self.numberingOffset:
                page = page - self.numberingOffset + 1
                isRelative = True
        self.setFields( bookmarkEntry[BOOKMARK.name] ,page , isRelative )
        
    def createButtons(self)->QDialogButtonBox:
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.buttons.clicked.connect( self.actionButtonClicked )
        return self.buttons

class UiBookmarkAdd(UiBookmarkSingle):
    """
        Add bookmark(s) for any page
    """
    labelTextNoPage = "Enter the <b>Bookmark Name</b>, and the <b>Book Page</b>."
    BtnSaveContinue="Save and add more..."

    def __init__(self, heading:str=None, totalPages:int=None, numberingOffset:int=None):
        super().__init__(totalPages=totalPages, numberingOffset=numberingOffset )

    def createButtons(self, )->QDialogButtonBox :
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self.BtnSaveContinue, QDialogButtonBox.ApplyRole )
        self.buttons.addButton(QDialogButtonBox.Save   )
        self.buttons.addButton( QDialogButtonBox.Cancel )
        self.buttons.clicked.connect(self.actionButtonClicked )
        return self.buttons

    def setupData(self, currentPage:int, isPageRelative:bool=False):
        self.bookPage.setText( toInt( currentPage , 1 ) )
        if isPageRelative and self.numberingOffset is not None:
            self.pageShown.setChecked( True )

    def setupFields(self, name:str , page:int=None):
        self.bookmarkName.setText( name )
        if page is not None:
            self.bookPage.setText( str( page ))
            self.bookmarkName.setFocus()
        else:
            self.bookPage.setFocus( Qt.OtherFocusReason )

class UiBookmark( UiBookmarkBase):
    '''
    This is a disposable class (don't keep instances of it alive). This handles goto and destroy
    '''
    action_file_delete = 'delete'
    actionGo = 'go'
    actionEdit = 'edit'

    def __init__(self, heading:str=None, bookmark_list:list=None, numberingOffset:int=None):
        super().__init__()
        self.createBookmarkTable()
        self.createButtons()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.bookmarkTable, 3, 0, 1, 3)
        mainLayout.addWidget(self.buttons)
        self.setLayout(mainLayout)
        self.selected = {}
        self.action = ''
        self.setWindowTitle( heading )
        self.setupData( bookmark_list, numberingOffset )
        self.resize(500, 400)

    def createBookmarkTable(self):
        super().createBookmarkTable( columns=3)

        self.bookmarkTable.cellClicked.connect(self.clickedBookmark)
        self.bookmarkTable.cellDoubleClicked.connect(
                self.doubleClickedBookmark)

    def clickedBookmark(self, row, column):
        self.selectedRow = row
        self.deleteButton.setEnabled( True )
        self.goButton.setEnabled( True )
        self.editButton.setEnabled( True )
        self.selected[ BOOKMARK.page] = toInt(self.bookmarkTable.item(row, self.COL_PAGE_BOOK).text())
        self.selected[ BOOKMARK.name] = self.bookmarkTable.item(row, self.COL_NAME).text()

    def doubleClickedBookmark(self, row, column):
        self.clickedBookmark(row, column)
        self.acceptBookmarkSelect()

    def createButtons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Open | QDialogButtonBox.Cancel| QDialogButtonBox.Discard | QDialogButtonBox.Apply
        )
        self.buttons.clicked.connect( self.actionButtonClicked )
        self.buttons.accepted.connect(self.acceptBookmarkSelect)
        self.buttons.rejected.connect(self.cancelBookmarkSelect)

        self.goButton = self.buttons.button(QDialogButtonBox.Open)
        self.goButton.setText( 'Go')
        self.goButton.setEnabled( False )

        self.deleteButton = self.buttons.button(QDialogButtonBox.Discard)
        self.deleteButton.setText("Delete")
        self.deleteButton.setObjectName('Delete')
        self.deleteButton.setEnabled( False )

        self.editButton = self.buttons.button(QDialogButtonBox.Apply)
        self.editButton.setText("Edit")
        self.editButton.setObjectName("Edit")
        self.editButton.setEnabled( False )

    def actionButtonClicked(self, button ):
        if button.objectName() == 'Delete' :
            self.action = self.action_file_delete
            self.returnSelect()
        if button.objectName() == 'Edit':
            self.action = self.actionEdit
            self.returnSelect()

    def cancelBookmarkSelect(self):
        self.selected[ BOOKMARK.page] = None
        self.reject()

    def acceptBookmarkSelect(self):
        self.action = self.actionGo
        self.returnSelect()

    def returnSelect(self):
        if self.selected[ BOOKMARK.page]:
            self.accept()
        self.reject()

    def _formatPageItem(self, bookmarkName, bookmarkPage, bookmarkRelative=None, protectItem:bool=False):
        name = TableItem(bookmarkName, protectItem)
        name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        page = TableItem("{:>6}".format(bookmarkPage), protectItem)
        page.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        if bookmarkRelative is not None and bookmarkRelative > 0 :
            relative = TableItem("{:>6}".format(bookmarkRelative))
        else:
            relative = TableItem("{:>6}".format("-"))
        relative.setProtected( protectItem )
        relative.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return (name, page, relative)

    def _insertBookmarkEntry(self, bookmarkItem:list):
        row = self.bookmarkTable.rowCount()
        self.bookmarkTable.insertRow(row)

        self.bookmarkTable.setItem(row, self.COL_NAME, bookmarkItem[0])
        self.bookmarkTable.setItem(row, self.COL_PAGE_BOOK, bookmarkItem[1])
        self.bookmarkTable.setItem(row, self.COL_PAGE_SHOWN, bookmarkItem[2])

    def setupData( self, bookmarkList:list , relativeOffset:int=0 )->bool:
        if bookmarkList is None or len( bookmarkList ) == 0:
            self.reject()
            return
        self.clear()
        for bookmark in bookmarkList:
            self._insertBookmarkEntry(  
                self._formatPageItem( 
                    bookmark[ BOOKMARK.name ], 
                    bookmark[ BOOKMARK.page ],
                    ( None if relativeOffset is None else bookmark[BOOKMARK.page]-relativeOffset+1 )
                )
            )
        return True

    def clear(self):
        super().clear()
        self.selected[ BOOKMARK.page]= None
        self.bookmarkTable.setRowCount(0)

    def onBookmarkSelected( self):
        pass

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