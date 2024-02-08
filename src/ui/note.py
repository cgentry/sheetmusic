"""
User Interface : Display and edit notes

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtCore    import QSize, QRect, Qt
from PySide6.QtWidgets import (
    QDialog, QGridLayout, QDialogButtonBox,
    QAbstractButton, QPushButton, QTextEdit,
    QMessageBox , QMenu)
from qdb.util   import DbHelper


class UiNote(QDialog):
    '''
    This will populate a simple text box from the 'notes' field
    '''

    btn_text_clear  = 'Clear'
    btn_text_cancel = 'Cancel'
    btn_text_save   = 'Save'
    btn_text_delete = 'Delete'

    action_Cancel = 0
    action_Save   = 1
    action_file_delete = 2

    def __init__(self):
        super().__init__()
        self._markdown      = True
        self._delete_entry  = False
        self._action        = self.action_Cancel
        self._hide          = True
        self._id            = None
        self._text_changed  = False

        self._create_text_field()
        self._create_buttons()
        main_layout = QGridLayout()
        main_layout.addWidget(self.text_field)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)
        self.setMinimumHeight(300)
        self.setMinimumWidth( 500 )

    def set_size( self, size:QSize , scale=.5)->None:
        """ Set window size """
        self.resize( int(size.width() *scale), int(size.height()* scale) )

    def _create_text_field(self):
        self.text_field = QTextEdit()
        self.text_field.setAcceptRichText(True)
        self._text_changed = False
        self.text_field.textChanged.connect( self.set_changed )

    def clear(self)->None:
        """ Clear the text field """
        self.text_field.clear()

    def _create_buttons(self)->None:
        self.btn_clear = QPushButton(  self.btn_text_clear )
        self.btn_save = QPushButton(   self.btn_text_save )
        self.btn_cancel = QPushButton( self.btn_text_cancel)
        self.btn_delete = QPushButton( self.btn_text_delete )

        self.btn_clear.setObjectName('clear')
        self.btn_save.setObjectName( 'save')
        self.btn_cancel.setObjectName('cancel')
        self.btn_delete.setObjectName('delete')
        self.btn_save.setDefault(True)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton( self.btn_save,    QDialogButtonBox.YesRole)
        self.buttons.addButton( self.btn_cancel , QDialogButtonBox.RejectRole)
        self.buttons.addButton( self.btn_clear,   QDialogButtonBox.ResetRole)
        self.buttons.addButton( self.btn_delete,  QDialogButtonBox.DestructiveRole)

        self.buttons.accepted.connect(self.accept() )
        self.buttons.rejected.connect(self.reject() )
        self.buttons.clicked.connect(self._action_clicked)

    def _action_clicked(self, btn:QAbstractButton ):
        """ Button clicked """
        if btn.text() == self.btn_text_clear :
            self.clear()

        if btn.text() == self.btn_text_save:
            self._action = self.action_Save
            self.accept()
        if btn.text() == self.btn_text_cancel :
            self._action = self.action_Cancel
            self.reject()
        if btn.text() == self.btn_text_delete:
            self.confirm_delete()

    def confirm_delete(self):
        """ Pop up delete confirmation """
        if QMessageBox.Yes == QMessageBox.warning(
            None, "",
            "Delete note for page?",
            QMessageBox.No | QMessageBox.Yes
        ) :
            self._action = self.action_file_delete
            self.accept()

    def set_id( self, noteid:int ):
        """ Set the note id """
        self._id = noteid
        self.btn_delete.setEnabled( not self._id is None)

    def get_id(self)->int:
        """ Return the ID """
        return self._id

    def set_text(self, txt:str)->None:
        """ Set value of note text with markdown """
        if not isinstance( txt , str ):
            raise ValueError("Invalid text passed: {type(txt)}")
        self.text_field.setMarkdown( txt )
        self._text_changed = False

    def text( self )->str:
        """ Return markdown text field """
        return self.text_field.toMarkdown()

    def set_changed(self)->None:
        """ Indicate text has changed """
        self._text_changed = True

    def delete(self)->bool:
        """ Delete action"""
        return self._action == self.action_file_delete

    def action( self ):
        """ Return what action occured"""
        return self._action

    def text_changed(self)->bool:
        """ Return true if the note text changed"""
        return self._text_changed

    def event_resize(self, _):
        """ Resize event occured"""
        self._text_changed = True

    def moveEvent(self, event ):
        """ Window moved - save flag"""
        super().moveEvent( event )
        self._text_changed = True

    def set_location( self, loc ):
        """ Restore location from either a QPoint or an encoded string """
        if isinstance( loc , QRect ) :
            self.setGeometry( loc )
        elif isinstance( loc , str ) and len( loc ) > 0 :
            self.setGeometry( DbHelper.decode( loc ))

    def location( self )->str:
        """ Get the current location of the note"""
        return DbHelper.encode( self.geometry() )

class UiNoteView(QTextEdit):
    '''
    This will populate a simple text box from the 'notes' field
    This is a 'viewer', not an editor
    '''
    def __init__(self):
        super().__init__()
        self._markdown      = True
        self._delete_entry  = False
        self._id            = None
        self._hide          = True
        self._setup_txtfield()
        self._setup_popup_menu()
        #self.addWidget(self.text_field)

        self.setMinimumHeight(300)
        self.setMinimumWidth( 500 )

    def set_size( self, size:QSize , scale=.5)->None:
        """ Set window size """
        self.resize( int(size.width() *scale), int(size.height()* scale) )

    def _setup_txtfield(self):
        self._hide = True
        self.setAcceptRichText(True)
        self.setWindowFlag( Qt.FramelessWindowHint )
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.setWindowOpacity( .9 )
        self.setReadOnly(True)

    def _setup_popup_menu(self)->None:
        self.menu_ = QMenu()
        self.menu_.addAction('Close')
        self.menu_.addAction('Transparent')
        self.menu_.addAction('Copy')
        self.menu_.triggered.connect( self.menu_Triggered )

    def menu_triggered(self, action_ ):
        """ Menu triggered """
        if action_.text() == 'Close':
            self.close()

    def mouse_press_event(self, e) -> None:
        """_summary_

        Args:
            e (QEvent): Event for mouse pressed

        Returns:
            _type_: _description_
        """
        txt = self.toPlainText()
        #rel_pos = self.pos()
        #pos = self.mapToGlobal(rel_pos)
        if e.button() == Qt.RightButton:
            self.set_text( txt + "\nRIGHT")
            self.menu_.exec( e.globalPosition().toPoint())
            return

        self.set_text( txt + "\nPress")
        super().mouse_press_event(e)

    def enterEvent(self, event) -> None:
        # if self._hide :
        #     self._hide = False
        #     self.setWindowFlag( Qt.FramelessWindowHint, False)
        #     self.show()
        return super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._hide :
            self._hide = True
            self.setWindowFlag( Qt.FramelessWindowHint )
            self.show()
        return super().leaveEvent(event)



if "__main__" == __name__ :
    #pylint: disable=C0412
    import os
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    mainFile = os.path.abspath(sys.modules['__main__'].__file__)

    tmod = UiNoteView( )
    tmod.set_text("Hello __World__!\nThis is <b>Chuck</b>")
    tmod.show()

    tmod2 = UiNoteView( )
    tmod2.set_text("window2")
    tmod2.move( 0,0)
    tmod2.show()


    sys.exit( app.exec() )
