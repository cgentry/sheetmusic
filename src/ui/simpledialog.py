# This Python file uses the following encoding: utf-8
# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#

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

from os import path
from PySide6.QtCore    import Qt, QDir
from PySide6.QtWidgets import ( 
        QCheckBox,        QComboBox,    QDialog,
        QDialogButtonBox, QFileDialog,  QGridLayout,
        QLabel,           QLineEdit,     QMessageBox,
        QPushButton,      QVBoxLayout,
)
from ui.util          import centerWidgetOnScreen
from util.simpleparse import SDOption, SDButton, SDEntry, SDEntriesMixin
from util.convert     import toInt

class SimpleDialog( QDialog , SDEntriesMixin):
    """ 
    Create a simple, dynamic dialog interaction for use with shell scripts
    
    verion 0.2 now uses keywords:
        type='file' options='.....' init='/file/path.sh' tag='return-tag'

    NOTE: version 0.1 used parms split by a ';' for dialogs. Those options are
    now obsolete. 

    All parsing has been split off to the 'simpleparse' class.
    SDEntriesMixin: parse the text lines to get all of the entries
    SDEntry: defines what every entry looks like and contains
    SDButton: handles button generation
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
            SDOption.TYPE_TITLE    : self.add_element_Title,
            
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
        self.button_map={ 'accept': QDialogButtonBox.AcceptRole , 'reject':QDialogButtonBox.RejectRole}
        self.buttons = []
        self.fields = []
        self.elements = []
        self.data = []

    def create_basic_widgets(self):
        self._dialog_layout = QVBoxLayout()
        self._grid_layout = QGridLayout()
        self._dialog_layout.addLayout( self._grid_layout )
        
        self.bbox = QDialogButtonBox()
        self.bbox.accepted.connect( self.action_button_accept )
        self.bbox.rejected.connect( self.action_button_reject )
        self._dialog_layout.addWidget( self.bbox )

    def create_label_widget( self, element:SDEntry , feedback:bool=False ):
        """ Take a standard element dictionary and create a label from it."""
        if element.is_option( SDOption.OPTION_READONLY) :
            new_label = QLabel()
            new_label.setStyleSheet( """border-style: outset;border-width: 1px;border-color: blue;""")
        else:
            new_label = QLineEdit()
            new_label.setDragEnabled( True )
        
        new_label.setObjectName(  element.format_unique_name() )
        new_label.setMinimumWidth( int( element.value(  SDOption.KEY_WIDTH , '75' )))
        return new_label

    def btn_choose_filename( self , element:SDEntry , feedback=None) :
        # the filter field is in options and looks like 'filter[ .... ]' We have to search options for it
        filter=element.value( SDOption.KEY_FILTER , '')
        label=element.value( SDOption.KEY_LABEL)

        (filename,_) = QFileDialog.getOpenFileName(
            None,
            label ,
            "" , 
            filter=filter )
        if filename :
            element.setValue( SDOption.KEY_VALUE, filename )
            element.set_changed(True)
            if feedback is not None:
                feedback.setText( filename )
        return True

    def btn_choose_directory( self , button, element:SDEntry , feedback=None) :
        # the filter field is in options and looks like 'filter[ .... ]' We have to search options for it
        button.setEnabled(False)
        txt = button.text()
        button.setText( '...')
        new_directory_name = QFileDialog.getExistingDirectory(None, element.value( SDOption.KEY_LABEL ) )
        button.setText( txt )
        button.setEnabled(True)
        if new_directory_name :
            element.setValue( SDOption.KEY_VALUE, new_directory_name )
            element.set_changed(True)
            if feedback is not None:
                feedback.setText( new_directory_name )
        return True

    def event_text_changed( self, textField:QLineEdit , element:SDEntry ):
        element.setValue( SDOption.KEY_VALUE, textField.text())
        element.set_changed(True)

    def event_dropdown_changed( self, dropitem:QComboBox , element:SDEntry ):
        index =dropitem.currentIndex()
        if index > -1:
            element.setValue( SDOption.KEY_VALUE, element.value( SDOption.KEY_DATA)[ index ] )
            element.set_changed(True)

    def event_checkbox_changed( self, checkboxitem:QCheckBox, element:SDEntry ):
        element.setValue( SDOption.KEY_VALUE , checkboxitem.isChecked() )
        element.set_changed(True)
                                                                     
    def add_element_file( self, row:int, element:SDEntry )->int:
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL) ), row, 0 )
        text_file = self.create_label_widget( element , feedback=True )
        text_file.setMinimumWidth( toInt( element.value( SDOption.KEY_WIDTH, 50 )) )
        text_file.textChanged.connect( lambda: self.event_text_changed( text_file , element ))

        button_file = QPushButton( self.TEXT_CHOOSE_FILE)
        button_file.setObjectName( element.format_unique_name() )
        button_file.clicked.connect( lambda: self.btn_choose_filename( element , feedback=text_file ) )
        button_file.setAutoDefault(False )
        if element.is_option( SDOption.OPTION_READONLY ) :
            self.setRetry( element , button_file )
        else:
            button_file.setAutoDefault(False)
            self.setRetry( element , text_file )

        self._grid_layout.addWidget( text_file , row, 1  )
        self._grid_layout.addWidget( button_file, row , 2 )
        return row+1
    
    def add_element_dir( self, row:int, element:SDEntry )->int:
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL) ), row, 0 )
        text_dir = self.create_label_widget( element , feedback=True )
        text_dir.setMinimumWidth( toInt( element.value( SDOption.KEY_WIDTH, 50 )) )
        text_dir.textChanged.connect( lambda: self.event_text_changed( text_dir , element ))
        
        button_dir = QPushButton( self.TEXT_CHOOSE_DIR)
        button_dir.setObjectName( element.format_unique_name( ) )
        button_dir.clicked.connect( lambda: self.btn_choose_directory( button_dir, element , feedback=text_dir ) )
        if element.is_option(  SDOption.OPTION_READONLY ) :
            self.setRetry( element , button_dir )
        else:
            button_dir.setAutoDefault(False)
            self.setRetry( element , text_dir )

        self._grid_layout.addWidget( text_dir , row, 1  )
        self._grid_layout.addWidget( button_dir, row , 2 )
    
        return row+1
    
    def add_element_text( self, row:int, element:SDEntry )->int:
        self._grid_layout.addWidget( QLabel( element.value( SDOption.KEY_LABEL)) , row, 0 )
        if element.is_option(SDOption.OPTION_READONLY):
            text_label = QLabel( element.value( SDOption.KEY_VALUE))
            text_label.setStyleSheet( """border-style: outset;border-width: 1px;border-color: blue;""")
        else:
            text_label = QLineEdit( element.value( SDOption.KEY_VALUE) )
            text_label.textChanged.connect( lambda: self.event_text_changed( text_label , element ))
            
        text_label.setObjectName( element.format_unique_name() )
        self.setRetry( element , text_label )
        
        self._grid_layout.addWidget( text_label , row , 1)
        return row+1
    
    def add_element_button(self, row:int, element:SDEntry )->int:
        return row
    
    def add_element_error( self, row:int, element:SDEntry )->int:
        return row+1
    
    def add_element_size( self, row:int , element:SDEntry )->int:
        height = toInt( element.value( SDOption.KEY_HEIGHT , None ) , None )
        width = toInt( element.value( SDOption.KEY_WIDTH , None ) , None )
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
        dropdown.currentTextChanged.connect( lambda: self.event_dropdown_changed( dropdown, element ))
        dropdown.setCurrentText( element.value( SDOption.KEY_VALUE ))

        self._grid_layout.addWidget( dropdown , row , 1)

        return row+1

    def add_element_Title( self, row:int, element:SDEntry )->int:
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
                raise ValueError("Invalid element '{}'".format( element_type ))
    
    def add_all_buttons(self):
        accept_button = False
        reject_button = False

        for button in self.findButtons():
            if button.isAccept():
                accept_button = True
            elif button.isReject():
                reject_button = True
            self.bbox.addButton( button.text(), button.role() )
        if not accept_button:
            self.bbox.addButton(QDialogButtonBox.Ok)
        if not reject_button:
            self.bbox.addButton(QDialogButtonBox.Cancel )

    def set_element_Focus( self, element:SDEntry ):
        if element.is_key( SDOption.KEY_RETRY ):
            retry = element.value( SDOption.KEY_RETRY )
            if retry is not None:
                retry.setStyleSheet( """border-style: outset;border-width: 2px;border-color: orange;""")
                retry.setFocus()

    def clear_element_Focus( self, element:SDEntry ):
        if element.is_key( SDOption.KEY_RETRY ):
            retry = element.value( SDOption.KEY_RETRY )
            if retry is not None:
                retry.setStyleSheet("" )

    def validate_required_element( self, element:SDEntry , heading:str='', error:str="Required field not set"):
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
                        "File '{}' does not exist.".format( value ),
                        msgbox_options )
        return rtn

    def validate_element_dir( self, element:SDEntry ):
        rtn = self.validate_required_element( element, 
  '       Directory Error', 
                error="Directory is required")
        if rtn != QMessageBox.Ok :
            return rtn
        
        value = element.value( SDOption.KEY_VALUE )
        # They have entered something, but it may not be correct. If they have set option to IGNORE 
        # We allow them to ignore the entry and accept anything they enter. Not a great idea, really
        msgbox_options = QMessageBox.Cancel | QMessageBox.Retry 
        if element.is_option( SDOption.OPTION_IGNORE ):
            msgbox_options = msgbox_options | QMessageBox.Ignore
            rtn = QMessageBox.warning(
                        None, "Directory not found", 
                        "Directory '{}' does not exist.".format( value ),
                        msgbox_options )
        return rtn

    def validate_element_text( self, element:SDEntry ):
        if not element.changed() and element.is_option( SDOption.OPTION_REQ ):
            return QMessageBox.warning(
                        None, 'Field not entered', 
          '       Text field is required.',
                        QMessageBox.Cancel | QMessageBox.Retry )
        return QMessageBox.Ok

    def validate_element_dropdown( self, element:dict):
        return QMessageBox.Ok
    
    def validate_element_checkbox( self, element:dict ):
        return QMessageBox.Ok
    
    def validate_element_Nothing( self, element:dict ):
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
                        self.set_element_Focus( element )
                        return
                    
                if element.changed() or ( element.value(SDOption.KEY_VALUE) and element.is_option(SDOption.OPTION_INCLUDE ) ):
                    rtnentry = { key: str( element.value( key ) ) for key in SDOption.LIST_RETURN }
                    self.data.append( rtnentry )
        self.accept()

    def action_button_reject( self):
        self.reject()
    
    def exec( self ):
        """ Generate the dialog and display to user """
        self.create_basic_widgets()
        self.replace_keywords()
        self.add_all_elements()
        self.add_all_buttons()
        self.setLayout( self._dialog_layout )
        centerWidgetOnScreen( self )
        #self.defaultbtn.setDefault( True )
        self.setWindowFlag( Qt.WindowStaysOnTopHint, True)
        return super().exec()
