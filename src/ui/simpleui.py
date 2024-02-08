"""
 User Interface : SimpleUI utility functions

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

 This will display MusicSettings and allow them to be changed. It does not
 open, or save, settings. The caller can get the information by calling
 get_changes() which will return either None or a dictionary/list of changes

 22-Sep-2022: Convert to use database
"""

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Signal, Property, Slot
from PySide6.QtWidgets import (
    QComboBox, QLineEdit, QLabel,
    QHBoxLayout, QPushButton, QFileDialog
)
from qdil.preferences import DilPreferences
from ui.edititem import UiGenericCombo

class UiSimpleBase():
    """ UiSimpleBase holds a few routines that are used
        throughout the preference routines.
        it will also hold the DilPref handle used for lookups
    """
    _dilpref = None

    def __init__(self, onchange:str):
        super().__init__()
        self._changed = False
        self._connect = None
        self._name = onchange

    @property
    def dilpref(self)->DilPreferences:
        """ Return a DilPreferences instance.
            If the current one isn't open, create one
        """
        if self._dilpref is None:
            self._dilpref = DilPreferences()
        return self._dilpref

    @property
    def ischanged(self)->bool:
        """ Return true if the change was detected """
        return self._changed

    def set_callback(self, callroutine : Callable[[str,str],None] ):
        """ Save callback routine

        Args:
            callroutine (Callable[[str,str],None]): Routine to call
        """
        self._connect = callroutine

    def callback( self, newvalue: str|bool|int ):
        """Perform callback to user routine

        Args:
            newvalue (str | bool | int): Value we are setting
        """
        if self._connect is not None:
            self._connect( self._name , newvalue )

@dataclass
class UiTrackEntry():
    """ UiTrackEntry holds an object used for
        tracking changes. It can currently store
        either a QLineEdit or a QComboBox
    """

    ENTRY_COMBO = 1
    ENTRY_TEXT = 2
    ENTRY_RADIO = 3
    ENTRY_CHECK = 4

    def __init__( self , eobject: QLineEdit|QComboBox|UiGenericCombo):
        """ Store the initial object and it's value
        For this to work, you must store the DbKey name
        as the object name.
        """

        if isinstance( eobject , QLineEdit ):
            self.etype = self.ENTRY_TEXT
        elif isinstance( eobject, ( QComboBox , UiGenericCombo )):
            self.etype = self.ENTRY_COMBO
        else:
            raise ValueError(f'Unknown type: {type(eobject )}')
        self.eobject = eobject
        self.evalue = self.current

    def iscombo(self)->bool:
        """ Is this a combo item?"""
        return isinstance( self.eobject, ( QComboBox , UiGenericCombo ) )

    def istext(self)->bool:
        """ Is this item a text item?"""
        return isinstance( self.eobject, QLineEdit )

    @property
    def current(self)->str:
        """ Return the current objects value """
        if self.istext() :
            return self.eobject.text()
        if self.iscombo():
            return self.eobject.currentData()
        return None

    @property
    def initial(self)->str:
        """ Get the initial stored value"""
        return self.evalue

    @property
    def changed( self )->bool:
        """ Return True if current value is different than stored"""
        return self.evalue != self.current

    @property
    def name(self)->str:
        """ Return the object name """
        return self.eobject.objectName()

    def trackobject(self)->QLineEdit|UiGenericCombo|QComboBox:
        """ Return the tracking object """
        return self.eobject

class UiTrackChange():
    """ Wrap Track entries in a list """
    entries = []
    _changes = {}

    def add( self, new_entry: UiTrackEntry|UiGenericCombo|QComboBox|QLineEdit ):
        """ Add new entry to list """
        if not isinstance( new_entry, UiTrackEntry):
            new_entry = UiTrackEntry( new_entry)
        self.entries.append( new_entry )

        if new_entry.istext():
            new_entry.trackobject().editingFinished.connect(
                                lambda: self._trackentry( new_entry ))
        elif new_entry.iscombo():
            new_entry.trackobject().currentIndexChanged.connect(
                                lambda: self._trackentry( new_entry ))

    def addtrack( self, objectname:str , value: str|bool )->None:
        """Track an external item and keep it's state in list
            This does not track if you change a value back.

        Args:
            objectname (str): Used to store the value in array
            value (str | bool): value to store
        """
        self._changes[ objectname ] = value

    def _trackentry( self, obj: UiTrackEntry ):
        key = obj.name
        if obj.changed :
            self._changes[obj.name ] = obj.current
        elif key in self._changes:
            del self._changes[ key ]

    def changes(self)->dict:
        """Return the changes that have been tracked

        Returns:
            dict: [str : str ]
                The objectname and value of the changes
        """
        return self._changes

    def haschanged(self)->bool:
        """ Return flag that there has been a change"""
        return len( self._changes ) > 0 or len( self.changes() ) > 0

    def clear(self)->None:
        """ Reset the entry list """
        self.entries = []
        self._changes = {}

class UiDirButton( QPushButton):
    """Generate a button for directory

        Connect to the button using 'callback.connect'

    Args:
        QPushButton
    """

    def __init__( self,
                 dirname:str,
                 objname:str=None ):
        """Create the directory change buttton

        Args:
            objname (str): Name for pushbutton
            currentdir (str): Set the current value of the directory
            callback (Callable[[str,str],None]): Optional callback routine
        """
        super().__init__()
        self.setText( 'Change...')
        self._directory = dirname
        self.clicked.connect( self._action_changedir )
        if objname is None:
            objname = 'change-' + \
                "".join([ c if c.isalnum() else "_" for c in dirname ])
        self.setObjectName( objname )


    def _action_changedir( self ):
        """ Pop up dialog box and get new directory """
        newdir = QFileDialog.getExistingDirectory(
            None,
            caption="Select Directory",
            dir=self._directory,
            options=QFileDialog.Option.ShowDirsOnly)

        self.setDown(False)
        self.directory = newdir

    def _dir(self):
        """ Return the directory. Internal call"""
        return self._directory

    def _set_dir(self, newdir:str ):
        if newdir != self._directory :
            self._directory = newdir
            self.callback.emit( self.objectName(), newdir )

    #define the setter/getter and callback funcion
    callback = Signal( str, str , name='callback')
    directory = Property(str, _dir, _set_dir, notify=callback)

class UiReset( QPushButton):
    """This will store and issue a reset event'
    Connect to the button using 'callback.connect'
    Args:
        QPushButton (QObejct):

    """
    callback = Signal( str, str )
    def __init__(self,
                 resetvalue:str,
                 objname:str=None ):
        super().__init__()
        self.setText( 'Reset')
        self._resetvalue = resetvalue
        self.clicked.connect( self._action_reset )
        if objname is None:
            objname = 'reset-' + \
                "".join([ c if c.isalnum() else "_" for c in resetvalue ])
        self.setObjectName( objname )

    def _action_reset(self):
        self._set_reset(self.resetvalue )

    def _reset(self):
        """ Return the directory. Internal call"""
        return self._resetvalue

    def _set_reset(self, newalue:str ):
        self._resetvalue = newalue
        self.callback.emit( self.objectName(), newalue )

    #define the setter/getter and callback funcion
    resetvalue = Property(str, _reset, _set_reset, notify=callback)

class UiDirLabel(  ):
    """Create a layout group that consists of:
        Label [text input ] [btn change] [btn reset]
        On change, the label will call the change routine
    """
    def __init__(self,  objname:str, default:str ) -> None:
        """Initialise the Directory widget

        Args:
            objname (str): Object name for label
            default (str): initial, and default, directory string
        """
        self._default = default
        self.lbl_dir = QLabel(default)
        self.lbl_dir.setObjectName( objname )

        self.layout = QHBoxLayout()
        self.layout.setObjectName( f"layout-{objname}" )

        self.btn_change = UiDirButton( dirname=default, objname=f'change-{objname}')
        self.btn_reset  = UiReset( resetvalue=default, objname=f'reset-{objname}')

        self.btn_change.callback.connect( self.changed_dir )
        self.btn_reset.callback.connect( self.changed_dir )

        self.layout.addWidget(self.lbl_dir)
        self.layout.addWidget( self.btn_change )
        self.layout.addWidget( self.btn_reset )

        self._changed = False

    @Slot(str, str)
    def changed_dir( self, _:str, newdir:str ):
        """ change """
        self.lbl_dir.setText(  newdir )
        self.lbl_dir.show()
        self._changed = True
