"""
User Interface : File open and delete dialogs

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import shutil
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

from qdb.dbbook import DbGenre, DbComposer, DbBook
from qdb.fields.book import BookField
from ui.qbox    import QBox



class FileBase(QDialog):
    """ This is a file base used for dialogs / filters """
    bookFilterLabel = 'Filter book name'
    def __init__(self):
        super().__init__()

        self._btn_select = None
        self.book = None
        self.book_name = None
        self.buttons = None
        self.cmb_composer = None
        self.cmb_genre = None
        self.file_list = None
        self.filter_name = None
        self.item_composer = None
        self.item_genre = None
        self.item_name = None
        self.name_filter = None
        self.tree_selection = None
        self.dbbook = DbBook()

        self.last_sort_order = ""
        self._selected_label('Name')
        self.sort_order = 'ASC'

        self.create_windows_layout()
        self.all_books_loaded = False
        self.load_genre()
        self.load_composer()
        self.load_bookfilter()
        self.load_book()
        self.setModal( True )

    def load_bookfilter(self):
        """ Set the book filter """
        item = QTreeWidgetItem(self.item_name, [ self.bookFilterLabel ])
        item.setFlags( Qt.ItemIsEnabled|Qt.ItemIsSelectable)

    def load_genre(self):
        """ Load the Tree widget with genres"""
        for name in DbGenre().getactive():
            QTreeWidgetItem( self.item_genre , [name])

    def load_composer(self):
        """ Load the Tree widget with composer names """
        for name in DbComposer().getactive():
            QTreeWidgetItem( self.item_composer , [name])

    def create_tablewidget(self,name:str )->QTableWidgetItem:
        """Create a table widget for books

        Args:
            name (str): Optional text title

        Returns:
            QTableWidgetItem: _description_
        """
        item = QTableWidgetItem()
        if not name:
            name = ''
        item.setText( name )
        item.setFlags( Qt.ItemIsEnabled|Qt.ItemIsSelectable)
        return item

    def fill_table( self, books ):
        """ Clear the file list and generate rows for propeerties"""
        self.book_name = None
        self.file_list.clear()
        self.file_list.setHorizontalHeaderLabels(["Name","Genre","Composer"])
        row = 0
        for book in books:
            self.file_list.insertRow(row)
            self.file_list.setItem( row , 0 , self.create_tablewidget( book[BookField.NAME]))
            self.file_list.setItem( row , 1 , self.create_tablewidget( book[BookField.GENRE]))
            self.file_list.setItem( row , 2 , self.create_tablewidget( book[BookField.COMPOSER]))
            self.file_list.setItem( row , 3 , self.create_tablewidget( book[BookField.LOCATION]))

            row += 1

    def button_accepted(self):
        """ button accepted pushed"""
        if self.book_name is not None:
            self.reject()
        self.accept()

    def button_rejected(self):
        """ button rejected pushed"""
        self.book_name = None
        self.reject()

    def load_book_order(self, column:str, value:str, sort_order:list):
        """ Load books by sort order """
        self.all_books_loaded = False
        self.book_name = None
        self.fill_table( self.dbbook.getbooks_filtered( column, value, sort_order ) )

    def load_book(self):
        """ Load all books into table """
        self.book_name = None
        if not self.all_books_loaded:
            self.all_books_loaded = True
            self.fill_table( self.dbbook.get_all() )

    def translate_class( self, class_name:str )->str :
        """ Translate external name to internal """
        if class_name == 'Book names':
            return 'book'
        if class_name == 'Genre' :
            return 'genre'
        return 'composer'

    def translate_order( self, class_name:str )->list:
        """ Order by genre or composer """
        if class_name == 'genre':
            return ['genre', 'book', 'composer']
        return ['composer', 'book', 'genre']

    def input_filter_name(self):
        """Fetch filter from user in dialog then fill table
        with files of similar name
        """
        txt,rtn = QInputDialog.getText( self, "Filter names", "Enter name" )
        if rtn :
            self.all_books_loaded = False
            self.fill_table( self.dbbook.similar_titles( txt ) )

    def tree_selection_changed(self):
        """Tree changed so filter load/process book titles

        Returns:
            None
        """
        item = self.tree_selection.currentItem()

        # Filter by name input
        if item.text(0) == self.bookFilterLabel:
            return self.input_filter_name()

        # Load all the books
        if item.text(0) == 'Book names' or item.childCount() > 0 :
            self.filter_name.clear()
            return self.load_book()

        # Load only filter books
        column = self.translate_class( item.parent().text(0))
        value = item.text(0)
        sort_order = self.translate_order( column )
        return self.load_bookOrder( column, value, sort_order )

    def section_clicked( self, index )->None:
        """ Section clicked """
        del index

    def file_selected(self , item:QTableWidgetItem )->None:
        """ File name selected """
        self._btn_select.setDisabled( False )
        self.book_name     = self.file_list.item( item.row(), 0 ).text()

    def file_open( self, item:QTableWidgetItem ):
        """ File open requested (double click )"""
        self.file_selected( item )
        self.accept()

    def action_line_filter( self , value:str ):
        """ name was chanaged """
        if len( value ) == 0 :
            self.load_book()
        if len(value) > 3:
            sort_order = ['book','genre','composer']
            self.load_bookOrder( 'book', value , sort_order )

    def create_treeview( self ):
        """ Create the initial tree view widget """
        self.tree_selection = QTreeWidget()
        self.tree_selection.setItemsExpandable(True)
        self.tree_selection.setColumnCount(1)
        self.tree_selection.setHeaderLabels(['Filters'])
        self.item_name = QTreeWidgetItem(self.tree_selection,['Book names'])
        self.item_genre = QTreeWidgetItem(self.tree_selection,['Genre'])
        self.item_composer = QTreeWidgetItem(self.tree_selection,['Composer'])

        self.tree_selection.itemSelectionChanged.connect(self.tree_selection_changed )
        return self.tree_selection

    def create_filelist( self ):
        """ Create filelist for display"""
        self.file_list = QTableWidget()
        self.file_list.setColumnCount( 4 )
        self.file_list.setSortingEnabled(True)

        head = self.file_list.horizontalHeader()
        head.setSectionHidden( 3 , True )
        head.setSectionResizeMode(0, QHeaderView.Stretch)

        head.setSortIndicator( 0 , Qt.AscendingOrder)
        head.setSortIndicatorShown(True)
        head.setHighlightSections(False)

        head.sectionClicked.connect(self.section_clicked )
        self.file_list.itemClicked.connect(self.file_selected )
        self.file_list.itemDoubleClicked.connect( self.file_open )
        return self.file_list

    def _create_name_filter( self )->QWidget:
        box = QHBoxLayout()
        lbl = QLabel()
        lbl.setText('Filter book names')
        self.name_filter = QLineEdit()
        self.name_filter.textChanged( self.action_line_filter )
        box.addWidget( lbl )
        box.addWidget( self.name_filter )

        return box

    def create_windows_layout(self):
        """Create the window layout
        """
        window_layout = QVBoxLayout(self)

        left_right = QSplitter(Qt.Horizontal)
        top_bottom = QSplitter(Qt.Vertical)

        left_right.addWidget(self.create_treeview())
        left_right.addWidget(self.create_filelist())
        left_right.setSizes([200,800])

        top_bottom.addWidget(left_right)
        top_bottom.addWidget( self._create_name_filter() )
        #top_bottom.addWidget(self.createInfoView())
        top_bottom.setSizes([600])

        window_layout.addWidget(top_bottom)
        window_layout.addWidget( self.create_buttons() )
        self._btn_select.setDisabled( True )

        self.setMinimumSize(900, 600)
        self.setLayout( window_layout )

    def _selected_label(self, sort_order:str ):
        if self.last_sort_order == sort_order:
            self.sort_order = ( 'DESC' if self.sort_order == 'ASC' else 'ASC')
        self.last_sort_order = sort_order
        if sort_order == 'Name':
            self._sort_fields = [
                BookField.NAME,
                BookField.DATE_READ,
                BookField.GENRE,
                BookField.COMPOSER]
        elif sort_order == 'Genre':
            self._sort_fields = [
                BookField.GENRE,
                BookField.NAME,
                BookField.DATE_READ,
                BookField.COMPOSER]
        elif sort_order == 'Composer':
            self._sort_fields = [
                BookField.COMPOSER,
                BookField.NAME,
                BookField.DATE_READ,
                BookField.GENRE]

    def _create_link_label(self, name:str )->QLabel:
        lbl = QLabel( f"<a href='{name}'>{name}</a>" )
        lbl.setTextInteraction_Flags( Qt.LinksAccessibleByMouse )
        lbl.setToolTip(f"Click to sort by {name}" )
        lbl.linkActivated.connect( self.selectedLabel )
        return lbl

    def _create_grid_layout( self)->QGridLayout:
        grid_layout = QGridLayout()
        grid_layout.addWidget( self._create_link_label('Name'),     0 , 0 )
        grid_layout.addWidget( self._create_link_label('Genre'),    0 , 1 )
        grid_layout.addWidget( self._create_link_label('Composer'), 0 , 2 )
        grid_layout.addWidget( self._create_link_label(''),         0 , 3 )
        grid_layout.addWidget( self._create_name_filter(),    1, 0 )
        grid_layout.addWidget( self.create_combo_genre(),    1, 1 )
        grid_layout.addWidget( self.create_combo_composer(), 1, 2)
        return grid_layout

    def create_combo_genre(self)->QComboBox:
        """ Create the combo box for genre category"""
        self.cmb_genre = QComboBox()
        self.cmb_genre.addItem( '*All', userData="*")
        for entry in DbGenre().get_all():
            self.cmb_genre.addItem( entry, userData=entry )
        self.cmb_genre.setCurrentIndex(0)
        return self.cmb_genre

    def create_combo_composer(self)->QComboBox:
        """ Create combobox for composers """
        self.cmb_composer = QComboBox()
        self.cmb_composer.addItem( '*All', userData="*")
        for entry in DbComposer().get_all():
            self.cmb_composer.addItem( entry, userData=entry )
        self.cmb_composer.setCurrentIndex(0)
        return self.cmb_composer

    def _create_name_filter(self):
        self.filter_name = QLineEdit()
        return self.filter_name

class Openfile( FileBase ):
    """ Prompt the use user to open a file from a list"""
    def __init__(self, title:str = 'Open Book'):
        super().__init__()
        self.setWindowTitle( title )

    def create_buttons(self):
        """ create the open/cancle buttons """
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Open   )
        self.buttons.addButton( QDialogButtonBox.Cancel )
        self._btn_select = self.buttons.button( QDialogButtonBox.Open )

        self.buttons.accepted.connect( self.button_accepted )
        self.buttons.rejected.connect( self.button_rejected )
        return self.buttons

    def info(self):
        """ info should be overloaded """
        return None

class Deletefile:
    """ Prompt the user for what files to delete
    """
    class PromptFile(FileBase):
        """ Hidden class to prompt for a file """
        def __init__(self):
            super().__init__()
            self.book_name = None
            self.dbbook = None
            self.setWindowTitle("Delete Book")

        def create_buttons(self)->QDialogButtonBox:
            """Create the buttons Cancel / Delete

            Returns:
                QDialogButtonBox: Button box
            """
            self.buttons = QDialogButtonBox()
            self._btn_select = QPushButton()
            self._btn_select.setText('Delete')
            self.buttons.addButton( self._btn_select, QDialogButtonBox.AcceptRole  )
            self.buttons.addButton( QDialogButtonBox.Cancel )

            self.buttons.accepted.connect( self.button_accepted )
            self.buttons.rejected.connect( self.button_rejected )
            return self.buttons

    def __init__(self, parent=None):
        self._parent = parent
        self.book_name = None
        self.book = None
        self.dbbook = None
        self.q = QBox(  )
        self.q.setIcon( QMessageBox.Question )
        self.q.setWindowTitle('Sheetmusic Delete')
        self.q.setStandardButtons(QMessageBox.Yes | QMessageBox.No )

    def _set_text(self, msg:str):
        # NOTE: This should compute based on width of character not length
        flen = int( max( len(msg) , 1.75*len(self.q.informativeText()) ) )
        fmt = f'{{0:{flen}s}} '
        self.q.setText( fmt.format( msg ))

    def _getbookname( self )->bool:
        """retrieve the text name of the book

        Returns:
            bool: True if book found and name set, False if not
        """
        self.book_name = None
        fname = Deletefile.PromptFile()
        if fname.exec() == QMessageBox.Accepted:
            self.book_name = fname.book_name
        return self.book_name is not None

    def _getbook(self )->bool:
        self.dbbook = DbBook()
        self.book = self.dbbook.getbook( self.book_name )
        return self.book is not None and BookField.NAME in self.book

    def delete(self, show_status:bool=True)->bool:
        """_summary_

        Args:
            show_status (bool, optional): _description_. Defaults to True.

        Returns:
            bool: _description_
        """
        if not self._getbookname() or not self._getbook():
            self.show_error( None, self.book_name, f'Could not find book {self.book_name}')
            return False
        self.q.setInformativeText( self.book_name )
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
                return self.dbbook.del_book( self.book_name) > 0
            except Exception as err:
                self.show_error( None, self.book_name, err )
        return False

    def _delete_all_files(self  )->bool:
        """ Delete all the associated image files attached to the book
            If the source and location are the same, it will not delete the files
            (This is usually the case for PDFs)
        """
        if self.book[BookField.LOCATION] == self.book[BookField.SOURCE ]:
            return True
        self.q.setText( "Delete all music files?")
        if self.book is not None and QMessageBox.Yes == self.q.exec():
            shutil.rmtree( self.book[ BookField.LOCATION ], onerror=self.show_error )
            return True
        return False

    def show_error( self , func, path, errinfo:Exception|str|int ):
        """ Error occured, show message"""
        del func
        if isinstance( errinfo, tuple ):
            emsg = str( errinfo[1] )
        else:
            emsg = str(errinfo)
        QMessageBox.critical(
            None,
            "File Deletion Error",
            f"Error deleting {path}\n{emsg}",
            QMessageBox.Cancel
        )



class Reimportfile( FileBase ):
    """ reimport a file that has been in imported before """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Book for Reimport")

    def create_buttons(self)->QDialogButtonBox:
        """ Create a button box"""
        self.buttons = QDialogButtonBox()
        self._btn_select = QPushButton()
        self._btn_select.setText('Reimport')
        self.buttons.addButton( self._btn_select, QDialogButtonBox.AcceptRole  )
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(self._btn_select, QDialogButtonBox.AcceptRole  )
        self.buttons.addButton( QDialogButtonBox.Cancel )

        self.buttons.accepted.connect( self.button_accepted )
        self.buttons.rejected.connect( self.button_rejected )
        return self.buttons

class DeletefileAction:
    """ Delete the file """
    def delete_file( self, name:str )->bool:
        """ Perform the delete of 'name' """
        dbbook = DbBook()
        book = dbbook.getbook( book=name)
        if book is None or BookField.NAME not in book:
            self.show_error( None, name, f'Could not find {name}')
            return False
        return self._delete_db_entry( dbbook , book ) and self._delete_all_files( dbbook , book )


    def _delete_db_entry( self , dbbook:DbBook, book:dict )->bool:
        """ Delete the DB entry for a file

        Args:
            dbbook (DbBook): Class for database book
            book (dict): Databae characteristics

        Returns:
            bool: _description_
        """
        rtn = QMessageBox.question(
                None,
                "Sheetmusic Delete",
                f"Delete library entry '{book[BookField.BOOK]}'?" ,
                QMessageBox.Yes | QMessageBox.No )
        if QMessageBox.Yes == rtn:
            try:
                return dbbook.del_book( book[BookField.BOOK]) > 0
            except Exception as err:
                self.show_error( None, book[BookField.BOOK], err )
        return False

    def _delete_all_files(self , dbbook:DbBook, book:dict )->bool:
        """ Delete all files """
        del dbbook
        if book is not None and QMessageBox.Yes == QMessageBox.question(
            None,
            "Sheetmusic Delete",
            f"Delete all music files for '{book[BookField.BOOK]}'?",
            QMessageBox.Yes | QMessageBox.No
        ):
            shutil.rmtree( book[ BookField.LOCATION ], onerror=self.show_error )
            return True
        return False

    def show_error( self , func, path, errinfo:Exception|str|int ):
        """Show the error that occured in a nice box

        Args:
            func (any): unused
            path (str): File path
            errinfo (Exception | str | int): Error code
        """
        del func
        if isinstance( errinfo, tuple ):
            emsg = str( errinfo[1] )
        else:
            emsg = str(errinfo)
        QMessageBox.critical(
            None,
            "File Deletion Error",
            f"Error deleting {path}\n{emsg}",
            QMessageBox.Cancel
        )
