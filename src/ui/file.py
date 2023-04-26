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

import shutil
from qdb.dbbook import DbGenre, DbComposer, DbBook
from qdb.keys   import BOOK
from ui.qbox    import QBox
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QComboBox,    QDialog,       QDialogButtonBox,
    QGridLayout,  QHBoxLayout,   QVBoxLayout,
    QWidget,      QSplitter,     QTreeWidget, 
    QTableWidget, QTreeWidgetItem, QLabel,             
    QTableWidgetItem, QHeaderView, QInputDialog,
    QMessageBox, QLineEdit
)


class FileBase(QDialog):

    bookFilterLabel = 'Filter book name'
    def __init__(self):
        super().__init__()

        self.dbook = DbBook()
        
        self.lastSortOrder = ""
        self.selectedLabel('Name')
        self.sortOrder = 'ASC'
        self.bookName = None

        layout = self.createWindowLayout()
        #layout.addLayout(self.createGridLayout())
        self.allBooksLoaded = False
        self.loadGenre()
        self.loadComposer()
        self.loadBookFilter()
        self.loadBook()
        self.setLayout(layout)
        self.setModal( True )

    def loadBookFilter(self):
        item = QTreeWidgetItem(self.itemName, [ self.bookFilterLabel ])
        item.setFlags( Qt.ItemIsEnabled|Qt.ItemIsSelectable)

    def loadGenre(self):
        for name in DbGenre().getactive():
            item = QTreeWidgetItem( self.itemGenre , [name])
            
    def loadComposer(self):
        for name in DbComposer().getactive():
            item = QTreeWidgetItem( self.itemComposer , [name])

    def bookItem(self,name:str )->QTableWidgetItem:
        item = QTableWidgetItem()
        if not name:
            name = ''
        item.setText( name )
        item.setFlags( Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        return item

    def fillTable( self, books ):
        self.bookName = None
        self.fileList.clear()
        self.fileList.setHorizontalHeaderLabels(["Name","Genre","Composer"])
        row = 0
        for book in books:
            self.fileList.insertRow(row)
            self.fileList.setItem( row , 0 , self.bookItem( book[BOOK.name]))
            self.fileList.setItem( row , 1 , self.bookItem( book[BOOK.genre]))
            self.fileList.setItem( row , 2 , self.bookItem( book[BOOK.composer]))
            self.fileList.setItem( row , 3 , self.bookItem( book[BOOK.location]))
        
            row += 1

    def buttonAccepted(self):
        if self.bookName is not None:
            self.reject()
        self.accept()

    def buttonRejected(self):
        self.bookName = None
        self.reject()

    def loadBookOrder(self, filterName:str, filter:str, sortOrder:list):
        """ Load books by sort order """
        self.allBooksLoaded = False
        self.bookName = None
        self.fillTable( self.dbook.getFilterBooks( filterName, filter, sortOrder ) )

    def loadBook(self):
        """ Load all books into table """
        self.bookName = None
        if not self.allBooksLoaded:
            self.allBooksLoaded = True
            self.fillTable( self.dbook.getAll() )

    def translateClass( self, className:str )->str :
        if className == 'Book names':
            return 'book'
        if className == 'Genre' :
            return 'genre'
        return 'composer'
    
    def translateOrder( self, className:str )->list:
        if className == 'genre':
            return ['genre', 'book', 'composer']
        return ['composer', 'book', 'genre']

    def inputFilterName(self):
        txt,rtn = QInputDialog.getText( self, "Filter names", "Enter name" )
        if rtn :
            self.allBooksLoaded = False
            self.fillTable( self.dbook.getLike( txt ) )

    def treeSelectionChanged(self):
        item = self.treeSelection.currentItem()

        # Filter by name input
        if item.text(0) == self.bookFilterLabel:
            return self.inputFilterName()

        # Load all the books
        if item.text(0) == 'Book names' or item.childCount() > 0 :
            self.filterName.clear()
            return self.loadBook()

        # Load only filter books
        filterName = self.translateClass( item.parent().text(0))
        filter = item.text(0)
        sortOrder = self.translateOrder( filterName )
        self.loadBookOrder( filterName, filter, sortOrder )

    def sectionClicked( self, index ):
        pass

    def fileSelected(self , item:QTableWidgetItem ):
        self._btnSelect.setDisabled( False )
        self.bookName     = self.fileList.item( item.row(), 0 ).text()
    
    def fileOpen( self, item:QTableWidgetItem ):
        self.fileSelected( item )
        self.accept()

    def actionLineFilter( self , value:str ):
        if len( value ) == 0 :
            self.loadBook()
        if len(value) > 3:
            sortOrder = ['book','genre','composer']
            self.loadBookOrder( 'book', value , sortOrder )

    def createTreeView( self ):
        self.treeSelection = QTreeWidget()
        self.treeSelection.setItemsExpandable(True)
        self.treeSelection.setColumnCount(1)
        self.treeSelection.setHeaderLabels(['Filters'])
        self.itemName = QTreeWidgetItem(self.treeSelection,['Book names'])
        self.itemGenre = QTreeWidgetItem(self.treeSelection,['Genre'])
        self.itemComposer = QTreeWidgetItem(self.treeSelection,['Composer'])

        self.treeSelection.itemSelectionChanged.connect(self.treeSelectionChanged )
        return self.treeSelection

    def createFileList( self ):
        self.fileList = QTableWidget()
        self.fileList.setColumnCount( 4 )
        self.fileList.setSortingEnabled(True)

        head = self.fileList.horizontalHeader()
        head.setSectionHidden( 3 , True )
        head.setSectionResizeMode(0, QHeaderView.Stretch)

        head.setSortIndicator( 0 , Qt.AscendingOrder)
        head.setSortIndicatorShown(True)
        head.setHighlightSections(False)

        head.sectionClicked.connect(self.sectionClicked )
        self.fileList.itemClicked.connect(self.fileSelected )
        self.fileList.itemDoubleClicked.connect( self.fileOpen )
        return self.fileList

    def createNameFilter( self )->QWidget:
        box = QHBoxLayout()
        lbl = QLabel()
        lbl.setText('Filter book names')
        self.nameFilter = QLineEdit()
        self.nameFilter.textChanged( self.actionLineFilter )
        box.addWidget( lbl )
        box.addWidget( self.nameFilter )

        return box

    def createWindowLayout(self):
        windowLayout = QVBoxLayout(self)  

        left_right = QSplitter(Qt.Horizontal)
        top_bottom = QSplitter(Qt.Vertical)
      
        left_right.addWidget(self.createTreeView())
        left_right.addWidget(self.createFileList())
        left_right.setSizes([200,800])

        top_bottom.addWidget(left_right)
        top_bottom.addWidget( self.createNameFilter() )
        #top_bottom.addWidget(self.createInfoView())
        top_bottom.setSizes([600])
		
        windowLayout.addWidget(top_bottom)
        windowLayout.addWidget( self.createButtons() )
        self._btnSelect.setDisabled( True )
        
        self.setMinimumSize(900, 600)
        self.setLayout( windowLayout )

    def loadTypes(self):
        self.treeSelection.add

    def selectedLabel(self, sortOrder:str ):
        if self.lastSortOrder == sortOrder:
            self.sortOrder = ( 'DESC' if self.sortOrder == 'ASC' else 'ASC')
        self.lastSortOrder = sortOrder
        if sortOrder == 'Name':
            self.sortFields = [BOOK.name, BOOK.dateRead, BOOK.genre, BOOK.composer]
        elif sortOrder == 'Genre':
            self.sortFields = [BOOK.genre, BOOK.name, BOOK.dateRead, BOOK.composer]
        elif sortOrder == 'Composer':
            self.sortFields = [BOOK.composer, BOOK.name, BOOK.dateRead, BOOK.genre]

    def createLinkLabel(self, name:str )->QLabel:
        lbl = QLabel( "<a href='{}'>{}</a>".format(name,name ) )
        lbl.setTextInteractionFlags( Qt.LinksAccessibleByMouse )
        lbl.setToolTip("Click to sort by {}".format( name ))
        lbl.linkActivated.connect( self.selectedLabel )
        return lbl

    def createGridLayout( self)->QGridLayout:
        grid_layout = QGridLayout()
        grid_layout.addWidget( self.createLinkLabel('Name'),     0 , 0 )
        grid_layout.addWidget( self.createLinkLabel('Genre'),    0 , 1 )
        grid_layout.addWidget( self.createLinkLabel('Composer'), 0 , 2 )
        grid_layout.addWidget( self.createLinkLabel(''),         0 , 3 )
        grid_layout.addWidget( self.createNameFilter(),    1, 0 )
        grid_layout.addWidget( self.createComboGenre(),    1, 1 )
        grid_layout.addWidget( self.createComboComposer(), 1, 2)
        return grid_layout

    def createComboGenre(self)->QComboBox:
        self.comboGenre = QComboBox()
        self.comboGenre.addItem( '*All', userData="*")
        for entry in DbGenre().getAll():
            self.comboGenre.addItem( entry, userData=entry )
        self.comboGenre.setCurrentIndex(0)
        return self.comboGenre

    def createComboComposer(self)->QComboBox:
        self.comboComposer = QComboBox()
        self.comboComposer.addItem( '*All', userData="*")
        for entry in DbComposer().getAllComposers():
            self.comboComposer.addItem( entry, userData=entry )
        self.comboComposer.setCurrentIndex(0)
        return self.comboComposer
    
    def createNameFilter(self):
        self.filterName = QLineEdit()
        return self.filterName


class Openfile( FileBase ):
    def __init__(self, title:str = 'Open Book'):
        super().__init__()
        self.setWindowTitle( title )

    def createButtons(self):
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Open   )
        self.buttons.addButton( QDialogButtonBox.Cancel )
        self._btnSelect = self.buttons.button( QDialogButtonBox.Open )
        
        self.buttons.accepted.connect( self.buttonAccepted )
        self.buttons.rejected.connect( self.buttonRejected )
        return self.buttons

    def info(self):
        pass

class Deletefile:
    class promptFile(FileBase):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Delete Book")

        def createButtons(self):
            self.buttons = QDialogButtonBox()
            self._btnSelect = QPushButton()
            self._btnSelect.setText('Delete')
            self.buttons.addButton( self._btnSelect, QDialogButtonBox.AcceptRole  )
            self.buttons.addButton( QDialogButtonBox.Cancel )
        
            self.buttons.accepted.connect( self.buttonAccepted )
            self.buttons.rejected.connect( self.buttonRejected )
            return self.buttons

    def __init__(self, parent=None):
        self._parent = parent
        self.q = QBox(  )
        self.q.setIcon( QMessageBox.Question )
        self.q.setWindowTitle('Sheetmusic Delete')
        self.q.setStandardButtons(QMessageBox.Yes | QMessageBox.No )
    
    def _setText(self, msg:str):
        # NOTE: This should compute based on width of character not length
        flen = int( max( len(msg) , 1.75*len(self.q.informativeText()) ) )
        fmt = f'{{0:{flen}s}} '
        self.q.setText( fmt.format( msg ))

    def _getbookname( self )->bool:
        self.bookName = None
        fname = Deletefile.promptFile()
        if fname.exec() == QMessageBox.Accepted:
            self.bookName = fname.bookName
        return self.bookName is not None
        
    def _getbook(self )->bool:
        self.dbook = DbBook()
        self.book = self.dbook.getBook( self.bookName ) 
        return self.book is not None and BOOK.name in self.book

    def delete(self, show_status:bool=True)->bool:
        if not self._getbookname() or not self._getbook():
            self.showError( None, self.bookName, f'Could not find book {self.bookName}')
            return False
        self.q.setInformativeText( self.bookName )
        status = self._delete_db_entry( ) and self._delete_all_files(  )
        if status and show_status:
            self.q.setStandardButtons( QMessageBox.Ok)
            self.q.setText('Book deleted')
            self.q.exec()

        return status

    def _delete_db_entry( self  )->bool:
        self.q.setText( "Delete book entry?"  )
        if QMessageBox.Yes == self.q.exec():
            try:
                return (self.dbook.delBook( self.bookName) > 0)
            except Exception as err:
                self.showError( None, self.bookName, err )
        return False

    def _delete_all_files(self  )->bool:
        """ Delete all the associated image files attached to the book 
            If the source and location are the same, it will not delete the files
            (This is usually the case for PDFs)
        """
        if self.book[BOOK.location] == self.book[BOOK.source ]:
            return True
        self.q.setText( "Delete all music files?")
        if self.book is not None and QMessageBox.Yes == self.q.exec():
            shutil.rmtree( self.book[ BOOK.location ], onerror=self.showError )
            return True
        return False

    def showError( self , func, path, errinfo:Exception|str|int ):
        if isinstance( errinfo, tuple ):
            emsg = str( errinfo[1] ) 
        else:
            emsg = str(errinfo)
        QMessageBox.critical( 
            None,
            "File Deletion Error",
            "Error deleting {}\n{}".format( path, emsg ),
            QMessageBox.Cancel
        )



class Reimportfile( FileBase ):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Book for Reimport")

    def createButtons(self):
        self.buttons = QDialogButtonBox()
        self._btnSelect = QPushButton()
        self._btnSelect.setText('Reimport')
        self.buttons.addButton( self._btnSelect, QDialogButtonBox.AcceptRole  )
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self._btnSelect, QDialogButtonBox.AcceptRole  )
        self.buttons.addButton( QDialogButtonBox.Cancel )
        
        self.buttons.accepted.connect( self.buttonAccepted )
        self.buttons.rejected.connect( self.buttonRejected )
        return self.buttons

class DeletefileAction:

    def delete_file( self, name:str )->bool:
        dbb = DbBook()
        book = dbb.getBook( book=name)
        if book is None or BOOK.name not in book:
            self.showError( None, name, f'Could not find {name}')
            return False
        return self._delete_db_entry( dbb , book ) and self._delete_all_files( dbb , book )

    
    def _delete_db_entry( self , dbb:DbBook, book:dict )->bool:
        rtn = QMessageBox.question(
                None,
                "Sheetmusic Delete",
                "Delete library entry '{}'?".format( book[BOOK.book] ),
                QMessageBox.Yes | QMessageBox.No )
        if QMessageBox.Yes == rtn:
            try:
                return (dbb.delBook( book[BOOK.book]) > 0)
            except Exception as err:
                self.showError( None, book[BOOK.book], err )
        return False

    def _delete_all_files(self , dbb:DbBook, book:dict )->bool:
        if book is not None and QMessageBox.Yes == QMessageBox.question(
            None,
            "Sheetmusic Delete",
            "Delete all music files for '{}'?".format( book[BOOK.book] ),
            QMessageBox.Yes | QMessageBox.No 
        ):
            shutil.rmtree( book[ BOOK.location ], onerror=self.showError )
            return True
        return False

    def showError( self , func, path, errinfo:Exception|str|int ):
        if isinstance( errinfo, tuple ):
            emsg = str( errinfo[1] ) 
        else:
            emsg = str(errinfo)
        QMessageBox.critical( 
            None,
            "File Deletion Error",
            "Error deleting {}\n{}".format( path, emsg ),
            QMessageBox.Cancel
        )
