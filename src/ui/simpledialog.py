"""
User Interface : Simpledialog interface

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from os import path
from PySide6.QtCore    import Qt
from PySide6.QtWidgets import (
        QCheckBox,        QComboBox,    QDialog,
        QDialogButtonBox, QFileDialog,  QGridLayout,
        QLabel,           QLineEdit,     QMessageBox,
        QPushButton,      QVBoxLayout,
)
from ui.util          import center_on_screen
from util.simpleparse import SDOption, SDEntry, SDEntriesMixin
from util.convert     import to_int

class SimpleDialog( QDialog , SDEntriesMixin):
    """
    Create a simple, dynamic dialog interaction_ for use with shell scripts

    verion 0.2 now uses keywords:
        type='file' options='.....' init='/file/path.sh' tag='return-tag'

    NOTE: version 0.1 used parms split by a ';' for dialogs. Those options are
    now obsolete.

    All parsing has been split off to the 'simpleparse' class.
    SDEntriesMixin: parse the text lines to get all of the entries
    SDEntry: defines what every entry looks like and contains
    SDOption: holds all of the options parsed.

    If no buttons are set, 'OK' and 'CANCEL' are added
    If no tag is passed, it will get type_# (where # is sequential )
    """
    LIST_TYPES  = SDOption.LIST_TYPES
    FIELD_SEP = ';'

    TEXT_CHOOSE_FILE = 'Select File'
    TEXT_CHOOSE_DIR  = 'Select Directory'

    def __init__( self ):
        super().__init__()
        self.list_add_element = {
            SDOption.TYPE_CHECK    : self.add_element_checkbox ,
            SDOption.TYPE_DIR      : self.add_element_dir,
            SDOption.TYPE_DROPDOWN : self.add_element_dropdown ,
            SDOption.TYPE_FILE     : self.add_element_file ,
            SDOption.TYPE_TEXT     : self.add_element_text ,
            SDOption.TYPE_TITLE    : self.add_element_title,

            SDOption.TYPE_BUTTON   : self.add_element_button ,
            SDOption.TYPE_ERROR    : self.add_element_error ,
            SDOption.TYPE_SIZE     : self.add_element_size  ,
        }
        self.list_validate_element = {
            SDOption.TYPE_CHECK    : self.validate_element_checkbox  ,
            SDOption.TYPE_DIR      : self.validate_element_dir,
            SDOption.TYPE_DROPDOWN : self.validate_element_dropdown  ,
            SDOption.TYPE_FILE     : self.validate_element_file ,
            SDOption.TYPE_TEXT     : self.validate_element_text ,

        }
        self.button_map={
                'accept': QDialogButtonBox.AcceptRole ,
                'reject':QDialogButtonBox.RejectRole}
        self.buttons = []
        self.fields = []
        self.elements = []
        self.data = []
        self._dialog_layout = QVBoxLayout()
        self._grid_layout = QGridLayout()
        self.bbox = QDialogButtonBox()

    def create_basic_widgets(self):
        """ Create all of the basic widgets """

        self._dialog_layout.addLayout( self._grid_layout )

        self.bbox.accepted.connect( self.action_button_accept )
        self.bbox.rejected.connect( self.action_button_reject )
        self._dialog_layout.addWidget( self.bbox )

    def create_label_widget( self, element:SDEntry , feedback:bool=False ):
        """ Take a standard element dictionary and create a label from it."""
        del feedback
        if element.is_option( SDOption.OPTION_READONLY) :
            new_label = QLabel()
            new_label.setStyleSheet(
                    """border-style: outset;border-width: 1px;border-color: blue;"""
            )
        else:
            new_label = QLineEdit()
            new_label.setDragEnabled( True )

        new_label.setObjectName(  element.format_unique_name() )
        new_label.setMinimumWidth(
                int( element.value(  SDOption.KEY_WIDTH , '75' )))
        return new_label

    def btn_choose_filename( self , element:SDEntry , feedback=None) :
        """ the filter field is in options and looks like 'filter[ .... ]'
        We have to search options for it """
        keyfilter=element.value( SDOption.KEY_FILTER , '')
        label=element.value( SDOption.KEY_LABEL)

        (filename,_) = QFileDialog.getOpenFileName(
            None,
            label ,
            "" ,
            filter=keyfilter )
        if filename :
            element.set_value( SDOption.KEY_VALUE, filename )
            element.set_changed(True)
            if feedback is not None:
                feedback.setText( filename )
        return True

    def btn_choose_directory( self , button, element:SDEntry , feedback=None) :
        """ the filter field is in options and looks like 'filter[ .... ]'
        We have to search options for it """
        button.setEnabled(False)
        txt = button.text()
        button.setText( '...')
        new_directory_name = \
            QFileDialog.getExistingDirectory(
                None, element.value( SDOption.KEY_LABEL
                )
        )
        button.setText( txt )
        button.setEnabled(True)
        if new_directory_name :
            element.set_value( SDOption.KEY_VALUE, new_directory_name )
            element.set_changed(True)
            if feedback is not None:
                feedback.setText( new_directory_name )
        return True

    def event_text_changed( self, testfield:QLineEdit , element:SDEntry ):
        """Text field has changed (there are several)

        Args:
            textField (QLineEdit): Which line has changed
            element (SDEntry): Element etry
        """
        element.set_value( SDOption.KEY_VALUE, testfield.text())
        element.set_changed(True)

    def event_dropdown_changed( self, dropitem:QComboBox , element:SDEntry ):
        """ Dropdown box has changed """
        index =dropitem.currentIndex()
        if index > -1:
            element.set_value(
                    SDOption.KEY_VALUE,
                    element.value( SDOption.KEY_DATA)[ index ]
            )
            element.set_changed(True)

    def event_checkbox_changed( self, checkboxitem:QCheckBox, element:SDEntry ):
        """ Checkbox has changed """
        element.set_value( SDOption.KEY_VALUE , checkboxitem.isChecked() )
        element.set_changed(True)

    def add_element_file( self, row:int, element:SDEntry )->int:
        """Add one element at row n

        Args:
            row (int): Row to add entry
            element (SDEntry): Entry to add at 'row'

        Returns:
            int: Next row number
        """
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL) ), row, 0 )
        text_file = self.create_label_widget( element , feedback=True )
        text_file.setMinimumWidth( to_int( element.value( SDOption.KEY_WIDTH, 50 )) )
        text_file.textChanged.connect( lambda: self.event_text_changed( text_file , element ))

        button_file = QPushButton( self.TEXT_CHOOSE_FILE)
        button_file.setObjectName( element.format_unique_name() )
        button_file.clicked.connect( \
            lambda: self.btn_choose_filename( \
                element , feedback=text_file
            )
        )
        button_file.setAutoDefault(False )
        if element.is_option( SDOption.OPTION_READONLY ) :
            self.set_retry( element , button_file )
        else:
            button_file.setAutoDefault(False)
            self.set_retry( element , text_file )

        self._grid_layout.addWidget( text_file , row, 1  )
        self._grid_layout.addWidget( button_file, row , 2 )
        return row+1

    def add_element_dir( self, row:int, element:SDEntry )->int:
        """Add a directory element

        Args:
            row (int): Row to add element to
            element (SDEntry): Directory element to add

        Returns:
            int: Next row
        """
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL) ), row, 0 )
        text_dir = self.create_label_widget( element , feedback=True )
        text_dir.setMinimumWidth( to_int( element.value( SDOption.KEY_WIDTH, 50 )) )
        text_dir.textChanged.connect( lambda: self.event_text_changed( text_dir , element ))

        button_dir = QPushButton( self.TEXT_CHOOSE_DIR)
        button_dir.setObjectName( element.format_unique_name( ) )
        button_dir.clicked.connect( \
            lambda: self.btn_choose_directory( \
                button_dir, element , feedback=text_dir
            )
        )
        if element.is_option(  SDOption.OPTION_READONLY ) :
            self.set_retry( element , button_dir )
        else:
            button_dir.setAutoDefault(False)
            self.set_retry( element , text_dir )

        self._grid_layout.addWidget( text_dir , row, 1  )
        self._grid_layout.addWidget( button_dir, row , 2 )

        return row+1

    def add_element_text( self, row:int, element:SDEntry )->int:
        """ Add textelement to table
        """
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL)) , row, 0 )
        if element.is_option(SDOption.OPTION_READONLY):
            text_label = QLabel( element.value( SDOption.KEY_VALUE))
            text_label.setStyleSheet( \
                """border-style: outset;border-width: 1px;border-color: blue;""")
        else:
            text_label = QLineEdit( element.value( SDOption.KEY_VALUE) )
            text_label.textChanged.connect( lambda: self.event_text_changed( text_label , element ))

        text_label.setObjectName( element.format_unique_name() )
        self.set_retry( element , text_label )

        self._grid_layout.addWidget( text_label , row , 1)
        return row+1

    def add_element_button(self, row:int, _:SDEntry )->int:
        """ Add button - this is for future use"""
        return row

    def add_element_error( self, row:int, _:SDEntry )->int:
        """ Will add a row but won't add anything to it"""
        return row+1

    def add_element_size( self, row:int , element:SDEntry )->int:
        """ Add a size elements for row, height """
        height = to_int( element.value( SDOption.KEY_HEIGHT , None ) , None )
        width = to_int( element.value( SDOption.KEY_WIDTH , None ) , None )
        if height is not None:
            self.setMinimumHeight( height )
        if width is not None:
            self.setMinimumWidth( width )
        return row

    def add_element_checkbox( self, row:int, element:SDEntry )->int:
        """
            Add check box to the grid.
            Value should be translated to boolean value from parser
            """

        check_box = QCheckBox( element.value( SDOption.KEY_LABEL ) )
        check_box.setObjectName( element.format_unique_name() )
        check_box.stateChanged.connect( lambda: self.event_checkbox_changed( check_box, element ))
        check_box.setChecked( bool(element.value( SDOption.KEY_VALUE) ) )
        element.set_changed( True )

        self._grid_layout.addWidget( check_box , row , 1)

        return row+1

    def add_element_dropdown( self, row:int, element:SDEntry )->int:
        """
            Add dropdown box to the grid. Entries defined in options: dropdown entry%entry%...
            INIT will be the initial selection
            The actual field separator can be anything when set by 'split'
            """
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL)) , row, 0 )
        dropdown = QComboBox()
        dropdown.setObjectName( element.format_unique_name() )
        dropdown.setEditable( False )

        dropdown.addItems( element.value( SDOption.KEY_DROP) )
        dropdown.currentTextChanged.connect( \
            lambda: self.event_dropdown_changed( dropdown, element ))
        dropdown.setCurrentText( element.value( SDOption.KEY_VALUE ))

        self._grid_layout.addWidget( dropdown , row , 1)

        return row+1

    def add_element_title( self, row:int, element:SDEntry )->int:
        """ Add a window title elment"""
        self.setWindowTitle( element.value( SDOption.KEY_LABEL ))
        return row

    def add_all_elements( self ):
        """ Loop through all the elements gathered and add them to dialog box """
        row = 0
        for element in self.elements:
            element_type = element.value( SDOption.KEY_TYPE)
            if element_type in self.list_add_element:
                row = self.list_add_element[ element_type ]( row, element )
            else:
                raise ValueError(f"Invalid element '{element_type}'")

    def add_all_buttons(self):
        """ Add all the buttons to the form (OK, Cancel )"""
        accept_button = False
        reject_button = False

        for button in self.find_buttons():
            if button.is_accept():
                accept_button = True
            elif button.is_reject():
                reject_button = True
            self.bbox.addButton( button.text(), button.role() )
        if not accept_button:
            self.bbox.addButton(QDialogButtonBox.Ok)
        if not reject_button:
            self.bbox.addButton(QDialogButtonBox.Cancel )

    def set_element_focus( self, element:SDEntry ):
        """ Set the focus to a specific element"""
        if element.is_key( SDOption.KEY_RETRY ):
            retry = element.value( SDOption.KEY_RETRY )
            if retry is not None:
                retry.setStyleSheet(
                    """border-style: outset;border-width: 2px;border-color: orange;""")
                retry.setFocus()

    def clear_element_focus( self, element:SDEntry ):
        """ Clear the focus from a specfic element"""
        if element.is_key( SDOption.KEY_RETRY ):
            retry = element.value( SDOption.KEY_RETRY )
            if retry is not None:
                retry.setStyleSheet("" )

    def validate_required_element( self,
            element:SDEntry ,
            heading:str='',
            error:str="Required field not set")->int:
        """Validate an element

        Args:
            element (SDEntry): Element to validate
            heading (str, optional): Heading for message.
                Defaults to ''.
            error (str, optional): Error message to display.
                Defaults to "Required field not set".

        Returns:
            int: Cancel or Retry
        """
        rtn = QMessageBox.Ok
        if element.is_option( SDOption.OPTION_REQ  ):
            if not element.value( SDOption.KEY_VALUE ):
                rtn= QMessageBox.warning(
                        None,
                        heading,
                        error,
                        QMessageBox.Cancel | QMessageBox.Retry )
        return rtn

    def validate_element_file( self, element:SDEntry ):
        """ Check the File Element entry to see if required and is valid """

        # This is where they must have entered something (we check for correct later)
        rtn = self.validate_required_element( element,
  '       File Error',
                error="File name is required.")
        if rtn != QMessageBox.Ok :
            return rtn

        value = element.value( SDOption.KEY_VALUE )
        # They have entered something, but it may not be correct. If they have set option to IGNORE
        # We allow them to ignore the entry and accept anything they enter. Not a great idea, really
        msgbox_options = QMessageBox.Cancel | QMessageBox.Retry
        if element.is_option( SDOption.OPTION_IGNORE ):
            msgbox_options = msgbox_options | QMessageBox.Ignore
        if not path.isfile( value ):
            rtn = QMessageBox.warning(
                        None, "File Not Found",
                        "File '{value}' does not exist.",
                        msgbox_options )
        return rtn

    def validate_element_dir( self, element:SDEntry ):
        """Check to make sure the dir name was entered
        and exists.
        Args:
            element (SDEntry): Directory text entry
        """
        rtn = self.validate_required_element( element,
  '         Directory Error',
            error="Directory is required"
        )
        if rtn != QMessageBox.Ok :
            return rtn

        value = element.value( SDOption.KEY_VALUE )

        # They have entered something, but it may not be correct. If they have set option to IGNORE
        # We allow them to ignore the entry and accept anything they enter. Not a great idea, really
        msgbox_options = QMessageBox.Cancel | QMessageBox.Retry
        if element.is_option( SDOption.OPTION_IGNORE ):
            msgbox_options = msgbox_options | QMessageBox.Ignore
            rtn = QMessageBox.warning(
                    None,
                    "Directory not found",
                    f"Directory '{value}' does not exist.",
                    msgbox_options
                )
        return rtn

    def validate_element_text( self, element:SDEntry ):
        """ Validate element passed """
        if not element.changed() \
            and element.is_option( SDOption.OPTION_REQ ):
            return QMessageBox.warning(
                        None, 'Field not entered',
          '       Text field is required.',
                        QMessageBox.Cancel | QMessageBox.Retry )
        return QMessageBox.Ok

    def validate_element_dropdown( self, _:dict):
        """ Placeholder """
        return QMessageBox.Ok

    def validate_element_checkbox( self, _:dict ):
        """ Placeholder """
        return QMessageBox.Ok

    def validate_element_nothing( self, _:dict ):
        """ Just a placeholder that doesn't do anything. Used when developing """
        return QMessageBox.Ok

    def action_button_accept( self):
        """Check all the entries have been set and we have valid data """
        self.data = []
        for element in self.elements:
            element_type = element.value( SDOption.KEY_TYPE)
            if element_type in self.list_validate_element :
                if element.changed() or element.is_option( SDOption.OPTION_REQ  ):
                    rtn = self.list_validate_element[ element_type ]( element )
                    if rtn == QMessageBox.Cancel :
                        self.reject()
                        return
                    if rtn == QMessageBox.Retry:
                        self.set_element_focus( element )
                        return

                if element.changed() or \
                    ( element.value(SDOption.KEY_VALUE) and \
                      element.is_option(SDOption.OPTION_INCLUDE ) ):
                    rtnentry = { key: str( element.value( key ) ) \
                        for key in SDOption.LIST_RETURN }
                    self.data.append( rtnentry )
        self.accept()

    def action_button_reject( self):
        """ Reject button hit """
        self.reject()

    def exec( self ):
        """ Generate the dialog and display to user """
        self.create_basic_widgets()
        self.replace_keywords()
        self.add_all_elements()
        self.add_all_buttons()
        self.setLayout( self._dialog_layout )
        center_on_screen( self )
        #self.defaultbtn.setDefault( True )
        self.setWindowFlag( Qt.WindowStaysOnTopHint, True)
        return super().exec()
