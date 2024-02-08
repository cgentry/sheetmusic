"""
 User interface : Preferences Dialog box

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

from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader, QFont
from PySide6.QtWidgets import (
    QButtonGroup,  QCheckBox,
    QComboBox,    QDialog,      QDialogButtonBox,
    QGridLayout,  QLabel,       QLineEdit,
    QPushButton, QRadioButton,  QHBoxLayout,
    QTabWidget,   QTextEdit,    QVBoxLayout,
    QWidget
)
from keymodifiers import KeyModifiers
from qdil.preferences import DilPreferences
from qdb.dbbook import DbGenre
from qdb.keys import DbKeys, ImportNameSetting
from qdb.log import LOG
from ui.edititem import UiGenericCombo
from ui.simpleui import (
    UiTrackEntry, UiTrackChange, UiDirButton, UiReset, UiSimpleBase
)
from util.toollist import GenerateEditList
from util.convert import decode


@dataclass
class LayoutPage():
    """ LayoutPage defines layouts for preferences """
    ONE_PAGE = 0
    TWO_PAGE = 1
    THREE_PAGE=2
    TWO_STACK = 3
    THREE_STACK = 4

    #Translate Text to index
    XLATE = {
        DbKeys.VALUE_PAGES_SINGLE: ONE_PAGE,
        DbKeys.VALUE_PAGES_SIDE_2: TWO_PAGE,
        DbKeys.VALUE_PAGES_STACK_2: TWO_STACK,
        DbKeys.VALUE_PAGES_SIDE_3: THREE_PAGE,
        DbKeys.VALUE_PAGES_STACK_3: THREE_STACK
    }

    def __init__(self):
        self.buttons = [
            QRadioButton() , QRadioButton(),
            QRadioButton() , QRadioButton(),
            QRadioButton()
        ]
        self.btn_box = QButtonGroup()
        self.btn_layout = QGridLayout()

        self._setup_buttons()
        self._setup_btn_box()
        self._setup_layout()

    def _setup_buttons(self)->None:
        self.buttons[ self.ONE_PAGE ].setText("1 page")
        self.buttons[ self.ONE_PAGE ].setObjectName(DbKeys.VALUE_PAGES_SINGLE)

        self.buttons[ self.TWO_PAGE ].setText("2 pages, side-by-side")
        self.buttons[ self.TWO_PAGE ].setObjectName(DbKeys.VALUE_PAGES_SIDE_2)

        self.buttons[ self.TWO_STACK ].setText("2 pages, stacked")
        self.buttons[ self.TWO_STACK ].setObjectName(DbKeys.VALUE_PAGES_STACK_2)

        self.buttons[ self.THREE_PAGE ].setText("3 pages, side-by-side")
        self.buttons[ self.THREE_PAGE ].setObjectName(DbKeys.VALUE_PAGES_SIDE_3)

        self.buttons[ self.THREE_STACK ].setText("3 pages, stacked")
        self.buttons[ self.THREE_STACK ].setObjectName(DbKeys.VALUE_PAGES_STACK_3)

    def _setup_btn_box(self)->None:
        for btn in self.XLATE.values():
            self.btn_box.addButton(self.buttons[ btn ])
        self.btn_box.setExclusive(True)

    def _setup_layout(self)->None:
        self.btn_layout.addWidget(
            self.buttons[self.ONE_PAGE],
            0, 0)
        self.btn_layout.addWidget(
            self.buttons[self.TWO_PAGE],
            1, 0)
        self.btn_layout.addWidget(
            self.buttons[self.TWO_STACK],
            1, 1)
        self.btn_layout.addWidget(
            self.buttons[self.THREE_PAGE],
            2, 0)
        self.btn_layout.addWidget(
            self.buttons[self.THREE_STACK],
            2, 1)

    def setbutton( self , page_layout:str )->None:
        """Translate what page layout is to a button check value

        Args:
            page_layout (str): text from preference store
        """
        if page_layout in self.XLATE :
            self.buttons[ self.XLATE[ page_layout ] ].setChecked(True )
        else:
            self.buttons[ self.ONE_PAGE ].setChecked( True )


class PreferenceCheckbox( UiSimpleBase ):
    """ Generate a checkbox for Preference Options
        This will have a lookup key in preferences,
        and a default value"""

    def __init__(self ,
                 objname:str,
                 label:str,
                 lookup:str=None,
                 default:bool=False) -> None:
        """Create the checkbox object

        This is based on UiSimpleBase which will do the callbacks


        Args:
            objname (str): Object name returned on change
            label (str): Label to display for checkbox
            lookup (str): Preference db key
                Default: None, use objname for key
            default (bool): what is the default value
                Default: False, not checked
        """
        super().__init__( objname )
        self.checkbox =  QCheckBox()
        self.checkbox.setObjectName(objname)
        self.checkbox.setText(label)
        self.checkbox.setCheckable(True)
        if lookup is None:
            lookup = objname
        if lookup is not None:
            self.checkbox.setChecked(decode(self.dilpref.get_value(
                lookup),
                code=DbKeys.ENCODE_BOOL,
                default=default))
        self.checkbox.stateChanged.connect(self._action_changed )

    def _action_changed( self ):
        """Set the changed flag and perform callback
        """
        self._changed = True
        self.callback( self.checkbox.isChecked() )

    @property
    def widget(self)->QCheckBox:
        """Get the underlying widget

        Returns:
            QCheckBox: Qt Checkbox Widget
        """
        return self.checkbox

    @property
    def checked(self)->bool:
        """ Return current checkbox state"""
        return self.checkbox.isChecked()

    @checked.setter
    def checked( self, newstate:bool )->None:
        """ Set the state of the checkbox """
        self.checkbox.setChecked( newstate )

class UiPreferences(QDialog):
    '''
    This creates a simple grid and populates it with info from the qdil/preferences.
    '''

    _device_settings = {
        'png': {'png16m': "24-bit RGB color",
                'pnggray': "Grayscale"},
        'jpg': {'jpeg': "Standard JPEG",
                'jpeggray': "Grayscale JPEG"},
        'bmp': {'bmp16m': '24-bit RGB color',
                'bmpgray': 'Grayscale'},
        'tif': {'tiff24nc': '24-bit RGB color',
                'tiffgray': 'Grayscale'},
    }
    _typeDesc = {
        "bmp":  "Bitmap image",
        "jpg":  "JPG Image",
        "tif":  "Tagged Information Format",
        "png":  "Portable Network Graphic",
    }
    _resolution = {
        "600":  "Very high resolution: This may be too large to load images",
        "300":  "High resolution; largest size and best resolution (may cause display errors)",
        "200":  "Medium resolution; good size and resolution",
        "150":  "Lowest resolution; smallest size and average resolution"
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dilpref = DilPreferences()
        self.layoutpg = LayoutPage()

        self.btn_use_label_viewer = None
        self.btn_use_pdf_viewer = None

        self.btn_box = QButtonGroup()
        self.cmb_device = None
        self.gcmb_editor = None
        self.cmb_genre = None
        self.gcmb_logging = None
        self.gcmb_name_import = None
        self.cmb_next_bookmark = None
        self.gcmb_page_back = None
        self.gcmb_page_forward = None
        self.gcmb_previous_bookmark = None
        self.gcmb_recent_files = None
        self.cmb_res = None
        self.cmb_type = None
        self.gcmb_first_page_shown = None
        self.gcmb_last_page_shown = None

        self.layout_book = None
        self.layout_file = None
        self.layout_keyboard = None
        self.layout_shellscript = None

        self.txt_script_shell = None
        self.txt_script_vars = None
        self.widget_book = None
        self.widget_file = None
        self.widget_keyboard = None
        self.widget_shellscript = None

        self._flag_changed = False

        self._device_settings['tiff'] = self._device_settings['tif']
        self._device_settings['jpeg'] = self._device_settings['jpg']
        self._typeDesc["jpeg"] = self._typeDesc["jpg"]
        self._typeDesc["tiff"] = self._typeDesc["tif"]

        self.setWindowTitle("Sheetmusic Preferences")

        main_layout = QVBoxLayout()

        self.fixed_font = QFont()
        self.fixed_font.setFixedPitch(True)
        self.fixed_font.setStyleHint(QFont.TypeWriter)
        self.fixed_font.setFamily("Courier New")

        self._create_tab_layout()
        self._create_main_buttons()

        main_layout.addWidget(self.tab_layout)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)
        self.clear()
        self.change_list = UiTrackChange()

    def clear(self):
        '''
        Setup and clear any variables used by modules
        '''
        self._flag_changed = False
        self.states = {}

    def _check_text_change(self, linefield: QLineEdit, key):
        if linefield.text() != self.dilpref.get_value(key):
            self.states[key] = linefield.text()

    def _check_combo_change(self, combobox: QComboBox, key: str):
        if key not in self.states or combobox.currentData() != self.states[key]:
            self.states[key] = combobox.currentData()

    def get_changes(self) -> dict:
        """Check all the fields on the form for changes
        If there is a change, the dictionary self.states
        will have a key/value set.

        Returns:
            dict: Key (DbKeys) : value entered
        """
        self.states |= self.change_list.changes()

        self._check_combo_change(self.gcmb_page_back,
                                 DbKeys.SETTING_PAGE_PREVIOUS)
        self._check_combo_change(self.gcmb_page_forward,
                                 DbKeys.SETTING_PAGE_NEXT)
        self._check_combo_change(self.gcmb_previous_bookmark,
                                 DbKeys.SETTING_BOOKMARK_PREVIOUS)
        self._check_combo_change(self.cmb_next_bookmark,
                                 DbKeys.SETTING_BOOKMARK_NEXT)
        self._check_combo_change(self.gcmb_first_page_shown,
                                 DbKeys.SETTING_FIRST_PAGE_SHOWN)
        self._check_combo_change(self.gcmb_last_page_shown,
                                 DbKeys.SETTING_LAST_PAGE_SHOWN)
        return self.states

    def _set_keys(self):
        self.gcmb_page_back.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_PAGE_PREVIOUS))
        self.gcmb_page_forward.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_PAGE_NEXT))
        self.gcmb_previous_bookmark.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_BOOKMARK_PREVIOUS))
        self.cmb_next_bookmark.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_BOOKMARK_NEXT))
        self.gcmb_first_page_shown.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_FIRST_PAGE_SHOWN))
        self.gcmb_last_page_shown.set_current_item(
            self.dilpref.get_value(DbKeys.SETTING_LAST_PAGE_SHOWN))

    def _create_tab_layout(self):
        self.tab_layout = QTabWidget()

        self.tab_layout.addTab(self._create_file_layout(), "File Settings")
        self.tab_layout.addTab(self._create_book_settings(), "Book settings")
        self.tab_layout.addTab(self._create_keyboard_layout(), "Key Modifiers")
        # self.tab_layout.addTab(self.createConvertPdfLayout(), "Script")
        self.tab_layout.addTab(
            self._create_shellscript_layout(), "Script Settings")

        return self.tab_layout

    def _label_grid(self, grid: QGridLayout, labels: list):
        for i, label in enumerate(labels, 0):
            if label is None:
                lbl = QLabel()
                lbl.setText(" ")
                grid.addWidget(lbl, i, 0)
            elif len(label) > 0:
                lbl = QLabel()
                lbl.setText(f"<b>{label}</b>:")
                lbl.setTextFormat(Qt.RichText)
                grid.addWidget(lbl, i, 0)

    def _create_file_layout(self) -> QWidget:
        labels = ['Sheetmusic directory',
                  'Library Directory (database)',
                  'User Script Directory',
                  "Number of recent files",
                  "",
                  "Editor",
                  "Log Level",
                  None]
        self.widget_file = QWidget()
        self.layout_file = QGridLayout()
        self.layout_file.setObjectName('layout_file')
        self._label_grid(self.layout_file, labels)
        self.widget_file.setLayout(self.layout_file)
        return self.widget_file

    def _create_book_settings(self) -> QWidget:
        labels = ["Book page import to format<br/>(Does not apply to PDF documents)",
                  "Configuration",
                  'Default Genre',
                  "Page layout",
                  "Page controls",
                  None,
                  None]
        self.widget_book = QWidget()
        self.layout_book = QGridLayout()
        self._label_grid(self.layout_book, labels)
        self.widget_book.setLayout(self.layout_book)
        return self.widget_book

    def _create_shellscript_layout(self) -> QWidget:
        labels = ["Command to run", "Command line options", None,
                  "Conversion type", "Resolution", "Import name settings", None]
        self.widget_shellscript = QWidget()
        self.layout_shellscript = QGridLayout()
        self._label_grid(self.layout_shellscript, labels)
        self.widget_shellscript.setLayout(self.layout_shellscript)
        return self.widget_shellscript

    def _create_keyboard_layout(self) -> QWidget:
        labels = [
            "",
            "Previous Page",
            "Next Page",
            "First Page",
            "Last Page",
            "",
            "Previous Bookmark",
            "Next Bookmark"
        ]
        self.widget_keyboard = QWidget()
        self.layout_keyboard = QGridLayout()
        self._label_grid(self.layout_keyboard, labels)
        self.widget_keyboard.setLayout(self.layout_keyboard)
        return self.widget_keyboard

    def _dir_line( self, objname:str, defaultdir:str )->QHBoxLayout:

        def callback( objname , value ):
            lbl.setText( value )
            self.change_list.addtrack( objname, value )

        dirlayout = QHBoxLayout()

        dirbtn = UiDirButton(
                    objname=objname,
                    dirname=defaultdir )
        dirbtn.callback.connect( callback)

        rstbtn = UiReset(
            objname=objname,
            resetvalue=defaultdir )
        rstbtn.callback.connect( callback )

        lbl = QLabel()
        lbl.setText( defaultdir )

        dirlayout.addWidget( lbl , alignment=Qt.AlignLeft, stretch=1)
        dirlayout.addWidget( dirbtn )
        dirlayout.addWidget( rstbtn )
        return dirlayout

    def _format_sheetmusic_dir(self, layout: QGridLayout, row: int) -> int:
        '''
            Location of where to store music files
        '''
        defaultdir = self.dilpref.get_value(
                    DbKeys.SETTING_DEFAULT_PATH_MUSIC,
                    DbKeys.VALUE_DEFAULT_DIR)

        layout.addLayout(self._dir_line(
                                DbKeys.SETTING_DEFAULT_PATH_MUSIC,
                                defaultdir),
                        row, 1, alignment=Qt.AlignLeft)
        return row+1

    def _format_user_scriptdir(self, layout: QGridLayout, row: int) -> int:
        '''
            Location of where to store script files
        '''
        defaultdir = self.dilpref.get_value(
            DbKeys.SETTING_PATH_USER_SCRIPT,
            DbKeys.VALUE_DEFAULT_USER_SCRIPT_DIR)

        layout.addLayout(self._dir_line(
                                DbKeys.SETTING_PATH_USER_SCRIPT,
                                defaultdir),
                        row, 1, alignment=Qt.AlignLeft)
        return row+1

    def _format_db_dir(self, layout: QGridLayout, row: int) -> int:
        # dbdir = UiDir(
        #         DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB,
        #         self.dilpref.dbdirectory)
        # dbdir.callback( self.change_list.addtrack)
        # layout.addLayout(dbdir.layout, row, 1, alignment=Qt.AlignLeft)

        layout.addLayout(self._dir_line(
                                DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB,
                                self.dilpref.dbdirectory ),
                        row, 1, alignment=Qt.AlignLeft)
        return row+1

    def _format_recent_files(self, layout: QGridLayout, row: int) -> int:
        values = [str(x) for x in range(
            DbKeys.VALUE_RECENT_SIZE_MIN, DbKeys.VALUE_RECENT_SIZE_MAX+1)]
        current = self.dilpref.get_value(
            DbKeys.SETTING_MAX_RECENT_SIZE, DbKeys.VALUE_RECENT_SIZE_DEFAULT)
        self.gcmb_recent_files = UiGenericCombo(
                isEditable=False,
                fill=values,
                current_value=current,
                name=DbKeys.SETTING_MAX_RECENT_SIZE
            )
        layout.addWidget(self.gcmb_recent_files, row, 1)
        self.change_list.add( UiTrackEntry(  self.gcmb_recent_files  ) )
        return row+1

    def _format_show_filepath(self, layout: QGridLayout, row: int) -> int:
        """Checkbox that determines if we are going to show the filepath with the title"""
        checkbox = PreferenceCheckbox(
            objname=DbKeys.SETTING_SHOW_FILEPATH,
            label="Show book's directory path with title",
            default=DbKeys.VALUE_SHOW_FILEPATH)
        checkbox.callback(self.change_list.addtrack )

        layout.addWidget(checkbox.widget, row, 1)
        return row+1

    def _format_editor(self, layout: QGridLayout, row: int) -> int:
        edlist = GenerateEditList()
        values = edlist.list()
        fill_list = {"None": ""}
        for key, value in values.items():
            fill_list[key] = value.path()

        current = self.dilpref.get_value(
            DbKeys.SETTING_PAGE_EDITOR, default="None")

        self.gcmb_editor = UiGenericCombo(
            isEditable=False,
            fill=fill_list,
            current_value=current,
            name=DbKeys.SETTING_PAGE_EDITOR)
        self.gcmb_editor.currentIndexChanged.connect(
            self._action_editor_changed)
        layout.addWidget(self.gcmb_editor, row, 1)
        return row+1

    def _format_log_level(self, layout: QGridLayout, row: int) -> int:
        fill_list = {
            'Disabled': LOG.disabled,
            'Debug': LOG.debug,
            'Information': LOG.info,
            'Warnings': LOG.warning,
            'Critical': LOG.critical}

        current = decode(
            code=DbKeys.ENCODE_INT,
            value=self.dilpref.get_value(
                DbKeys.SETTING_LOGGING_ENABLED,
                default=0)
        )
        self.gcmb_logging = UiGenericCombo(
            isEditable=False, fill=fill_list,
            current_value=current,
            name=DbKeys.SETTING_LOGGING_ENABLED)
        layout.addWidget(self.gcmb_logging, row, 1)
        self.change_list.add( UiTrackEntry(  self.gcmb_logging  ) )
        return row+1

    def _format_use_pdf(self, layout: QGridLayout, row: int) -> int:
        use_pdf = decode(
            code=DbKeys.ENCODE_BOOL,
            value=self.dilpref.get_value(
                key=DbKeys.SETTING_RENDER_PDF,
                default=DbKeys.VALUE_RENDER_PDF)
        )
        self.btn_use_pdf_viewer = QRadioButton()
        self.btn_use_pdf_viewer.setText("Render PDF pages using PDF Viewer")
        self.btn_use_pdf_viewer.setObjectName('True')

        self.btn_use_label_viewer = QRadioButton()
        self.btn_use_label_viewer.setText("Render PDF pages using images")
        self.btn_use_label_viewer.setObjectName('False')

        self.btn_box.addButton(self.btn_use_pdf_viewer)
        self.btn_box.addButton(self.btn_use_label_viewer)

        btn_layout = QGridLayout()
        btn_layout.addWidget(self.btn_use_pdf_viewer,    0, 0)
        btn_layout.addWidget(self.btn_use_label_viewer,  1, 0)

        if use_pdf:
            self.btn_use_pdf_viewer.setChecked(True)
        else:
            self.btn_use_label_viewer.setChecked(True)

        layout.addLayout(btn_layout, row, 1)
        return row+1

    def _format_filetype(self, layout: QGridLayout, row: int) -> int:
        self.cmb_type = QComboBox()
        self.cmb_type.setObjectName(DbKeys.SETTING_FILE_TYPE)
        ftype = self.dilpref.get_value(DbKeys.SETTING_FILE_TYPE)
        for bvalue in QImageReader.supportedImageFormats():
            key = bvalue.data().decode()
            if key in self._typeDesc:
                self.cmb_type.addItem(
                    f"{key:4s}: {self._typeDesc[key]}",
                    userData=key)
        idx = self.cmb_type.findData(ftype)
        if idx > -1:
            self.cmb_type.setCurrentIndex(idx)
        layout.addWidget(self.cmb_type, row, 1)
        self.cmb_type.currentIndexChanged.connect(self._action_type_changed)
        self.change_list.add( UiTrackEntry(  self.cmb_type  ) )
        return row+1

    def _format_resolution(self, layout: QGridLayout, row: int) -> int:
        self.cmb_res = QComboBox()
        self.cmb_res.setObjectName(DbKeys.SETTING_FILE_RES)
        fres = self.dilpref.get_value(
            DbKeys.SETTING_FILE_RES, default=DbKeys.VALUE_FILE_RES)
        for key, desc in self._resolution.items():
            self.cmb_res.addItem(f"{key:4s}: {desc}", userData=key)
        idx = self.cmb_res.findData(fres)
        if idx > -1:
            self.cmb_res.setCurrentIndex(idx)
        layout.addWidget(self.cmb_res, row, 1)
        self.change_list.add( UiTrackEntry(  self.cmb_res  ) )
        return row+1

    def _format_default_genre(self, layout: QGridLayout, row: int) -> int:
        self.cmb_genre = QComboBox()
        self.cmb_genre.setObjectName(DbKeys.SETTING_BOOK_DEFAULT_GENRE)
        self.cmb_genre.addItems(DbGenre().get_all())
        default = self.dilpref.get_value(
            DbKeys.SETTING_BOOK_DEFAULT_GENRE,
            DbKeys.VALUE_DEFAULT_GENRE)
        idx = self.cmb_genre.findText(default)
        if idx > -1:
            self.cmb_genre.setCurrentIndex(idx)
        else:
            self.cmb_genre.setCurrentIndex(0)
        layout.addWidget(self.cmb_genre, row, 1)
        self.change_list.add( UiTrackEntry(  self.cmb_genre  ) )
        return row+1

    def _format_file_device(self, layout: QGridLayout, row: int) -> int:
        self.cmb_device = QComboBox()
        self.cmb_device.setObjectName(DbKeys.SETTING_DEFAULT_IMGFORMAT)

        ftype = self.dilpref.get_value(
            DbKeys.SETTING_DEFAULT_IMGFORMAT,
            DbKeys.SETTING_DEFAULT_IMGFORMAT)
        data_type = self.cmb_type.currentData()
        self.cmb_device.clear()
        for key, value in self._device_settings[data_type].items():
            self.cmb_device.addItem(f"{key:4s}: {value}", userData=key)
        idx = self.cmb_device.findData(ftype)
        if idx > -1:
            self.cmb_device.setCurrentIndex(idx)
        layout.addWidget(self.cmb_device, row, 1)
        self.change_list.add( UiTrackEntry(  self.cmb_device  ) )
        return row+1

    def _format_import_name(self, layout: QGridLayout, row: int) -> int:
        current_value = self.dilpref.get_value(
            DbKeys.SETTING_NAME_IMPORT, DbKeys.VALUE_NAME_IMPORT_FILE_1)
        self.gcmb_name_import = UiGenericCombo(False, ImportNameSetting(
        ).forImportName, current_value, name=DbKeys.SETTING_NAME_IMPORT)
        layout.addWidget(self.gcmb_name_import, row, 1)
        self.change_list.add( UiTrackEntry(  self.gcmb_name_import  ) )
        return row+1

    def _format_reopen_lastbook(self, layout: QGridLayout, row: int) -> int:
        checkbox = PreferenceCheckbox(
            objname=DbKeys.SETTING_LAST_BOOK_REOPEN,
            label="Reopen last book",
            default=DbKeys.VALUE_REOPEN_LAST)
        checkbox.callback(self.change_list.addtrack )

        layout.addWidget(checkbox.widget , row, 1)
        return row+1

    def _format_save_config(self, layout: QGridLayout, row: int) -> int:
        checkbox = PreferenceCheckbox(
            objname=DbKeys.SETTING_USE_TOML_FILE,
            label="Save configuration file with PDF (.cfg)",
            default=DbKeys.VALUE_USE_TOML_FILE)
        checkbox.callback(self.change_list.addtrack )

        layout.addWidget(checkbox.widget, row, 1)
        return row+1

    def _format_aspect_ratio(self, layout: QGridLayout, row: int) -> int:
        checkbox = PreferenceCheckbox(
            objname=DbKeys.SETTING_KEEP_ASPECT,
            label="Keep aspect ratio for pages",
            default=DbKeys.VALUE_KEEP_ASPECT)
        checkbox.callback(self.change_list.addtrack )

        layout.addWidget(checkbox.widget, row, 1)
        return row+1

    def _format_smart_pages(self, layout: QGridLayout, row: int) -> int:
        checkbox = PreferenceCheckbox(
            objname=DbKeys.SETTING_SMART_PAGES,
            label="Use smart page display( 1,2 -> 3,2 -> 3,4)",
            default=DbKeys.VALUE_SMART_PAGES)
        checkbox.callback(self.change_list.addtrack )

        layout.addWidget(checkbox.widget, row, 1)
        return row+1

    def _format_layout(self, layout: QGridLayout, row: int) -> int:
        page_layout = self.dilpref.get_value(DbKeys.SETTING_PAGE_LAYOUT)
        self.layoutpg.setbutton( page_layout )

        layout.addLayout( self.layoutpg.btn_layout, row, 1 )
        self.layoutpg.btn_box.buttonClicked.connect( self._action_layout )
        return row+1

    def format_script(self, layout: QGridLayout, row: int) -> int:
        """ Format the script for output in GUI """
        initvalue = self.dilpref.get_value(DbKeys.SETTING_DEFAULT_SCRIPT)
        self.txt_script_shell = QLineEdit()
        self.txt_script_shell.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT)
        self.txt_script_shell.setText( initvalue )
        layout.addWidget(self.txt_script_shell, row, 1)
        self.change_list.add( UiTrackEntry(  self.txt_script_shell  ) )
        return row+1

    def format_script_vars(self, layout: QGridLayout, row: int) -> int:
        """ create the inputs for the script runner
        (system shell) and parms to pass to the runner"""
        self.txt_script_vars = QLineEdit()
        self.txt_script_vars.setObjectName(DbKeys.SETTING_DEFAULT_SCRIPT_VAR)
        self.txt_script_vars.setText(self.dilpref.get_value(
            DbKeys.SETTING_DEFAULT_SCRIPT_VAR))
        layout.addWidget(self.txt_script_vars, row, 1)
        lbl_hint_scriptvar = QLabel()
        lbl_hint_scriptvar.setText(
            "Use a semicolon to separate options, e.g. -c;-d;-e")
        layout.addWidget(lbl_hint_scriptvar, row+1, 1)
        self.change_list.add( UiTrackEntry(  self.txt_script_vars  ) )
        return row+2

    def format_data(self):
        """ Format all the directory inputs: music, database, scripts, etc."""
        #
        row = 0
        row = self._format_sheetmusic_dir(self.layout_file, row)
        row = self._format_db_dir(self.layout_file, row)
        row = self._format_user_scriptdir(self.layout_file, row)
        row = self._format_recent_files(self.layout_file, row)
        row = self._format_show_filepath(self.layout_file, row)
        row = self._format_editor(self.layout_file, row)
        row = self._format_log_level(self.layout_file, row)
        #
        row = self._format_filetype(self.layout_book, 0)
        row = self._format_save_config(self.layout_book, row)
        row = self._format_default_genre(self.layout_book, row)
        row = self._format_layout(self.layout_book, row)
        row = self._format_reopen_lastbook(self.layout_book, row)
        row = self._format_aspect_ratio(self.layout_book, row)
        row = self._format_smart_pages(self.layout_book, row)
        row = self._format_use_pdf(self.layout_book, row)
        #
        row = self.format_script(self.layout_shellscript, 0)
        row = self.format_script_vars(self.layout_shellscript, row)
        row = self._format_file_device(self.layout_shellscript, row)
        row = self._format_resolution(self.layout_shellscript, row)
        row = self._format_import_name(self.layout_shellscript, row)
        #row = self._format_user_scriptdir(self.layout_shellscript, row)
        #
        self._format_key_mods(self.layout_keyboard, 0)

    def _format_key_mods(self, layout: QGridLayout, row: int):
        """
            Keymods takes up one tab page
        """
        km = KeyModifiers()
        row = 0
        col = 1

        lbl = QLabel()
        lbl.setText("<h3>Page Number Navigation</h3>")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl, row, 0, 1, 2, alignment=Qt.AlignCenter)

        row += 1
        self.gcmb_page_back = UiGenericCombo(
            isEditable=False, fill=km.page_back(),
            name=DbKeys.SETTING_PAGE_PREVIOUS)
        layout.addWidget(self.gcmb_page_back, row, col)
        self.change_list.add( self.gcmb_page_back )

        row += 1
        self.gcmb_page_forward = UiGenericCombo(
            isEditable=False, fill=km.page_forward(),
            name=DbKeys.SETTING_PAGE_NEXT)
        layout.addWidget(self.gcmb_page_forward, row, col)
        self.change_list.add( UiTrackEntry(  self.gcmb_page_forward  ) )

        row += 1
        self.gcmb_first_page_shown = UiGenericCombo(
            isEditable=False, fill=km.first_page_shown(),
            name=DbKeys.SETTING_FIRST_PAGE_SHOWN)
        layout.addWidget(self.gcmb_first_page_shown, row, col)
        self.change_list.add( UiTrackEntry(  self.gcmb_first_page_shown  ) )

        row += 1
        self.gcmb_last_page_shown = UiGenericCombo(
            isEditable=False, fill=km.last_page_shown(),
            name=DbKeys.SETTING_LAST_PAGE_SHOWN)
        layout.addWidget(self.gcmb_last_page_shown, row, col)
        self.change_list.add( UiTrackEntry(  self.gcmb_last_page_shown  ) )

        row += 1
        lbl = QLabel()
        lbl.setText("<h3>Bookmark Navigation</h3>")
        layout.addWidget(lbl, row, 0, 1, 2, alignment=Qt.AlignCenter)

        row += 1
        self.gcmb_previous_bookmark = UiGenericCombo(
            isEditable=False, fill=km.previous_bookmark(),
            name=DbKeys.SETTING_BOOKMARK_PREVIOUS)
        layout.addWidget(self.gcmb_previous_bookmark, row, col)
        self.change_list.add(   self.gcmb_previous_bookmark   )

        row += 1
        self.cmb_next_bookmark = UiGenericCombo(
            isEditable=False, fill=km.next_bookmark(),
            name=DbKeys.SETTING_BOOKMARK_NEXT)
        layout.addWidget(self.cmb_next_bookmark, row, col)
        self.change_list.add(   self.cmb_next_bookmark   )

        # This will set the keyboard mods to what is stored in the database (if any)
        self._set_keys()

        del km

    def _create_main_buttons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttons.clicked.connect(self._action_main_button_clicked)

    def edit_item(self, item: QWidget):
        """An item has been edited.
        Fetch the object name and save the text value

        Args:
            item (QWidget): object that has changed
        """
        #self.dilpref.Table.blockSignals(True)
        name = item.objectName()
        self.states[name] = item.text().strip()
        #self.dilpref.Table.blockSignals(False)


    def _action_help(self):
        help_layout = QVBoxLayout()
        help_dlg = QDialog()
        help_dlg.setMinimumHeight(500)

        def action_help_close():
            help_dlg.reject()

        help_pdf = QTextEdit()
        help_pdf.setText(self._help_pdfCmd)
        help_pdf.setReadOnly(True)
        help_pdf.setMinimumWidth(500)

        help_layout.addWidget(help_pdf)
        btn_pdf = QPushButton("Close")
        help_layout.addWidget(btn_pdf)
        btn_pdf.clicked.connect(action_help_close)

        help_dlg.setLayout(help_layout)
        help_dlg.exec()

    def _action_editor_changed(self, _):
        self.change_list.addtrack(
            DbKeys.SETTING_PAGE_EDITOR,
            self.gcmb_editor.currentText() )
        self.change_list.addtrack(
            DbKeys.SETTING_PAGE_EDITOR_SCRIPT,
            self.gcmb_editor.currentData() )

    def _action_type_changed(self, value):
        del value
        #self._format_file_device(self.layout_shellscript, 3)

    def _action_layout(self, btn: QButtonGroup):
        """ Connect change to tracking object"""
        self.change_list.addtrack( DbKeys.SETTING_PAGE_LAYOUT , btn.objectName )

    def _action_main_button_clicked(self, btn):
        """ If btn text is 'Save' and we detect changes
            return 'accept()
        """
        if btn.text() == "Save" and self.change_list.haschanged():
            self.accept()
        else:
            self.reject()

    _help_pdfCmd = """<h1>Script</h1>
The script that comes with the system is based on UNIX/LINUX/MacOS rather
than Windows. You may enter a Windows script, and one may be provided in the future.
In the script, you have several 'variables' you can insert:
<ul>
<li>{{source}}}&nbsp;-&nbsp;This is the complete file path to the PDF. You will be prompted before the script is run.</li>
<li>{{target}}&nbsp;-&nbsp;This value is from the File Setting ; Default Directory</li>
<li>{{name}}}&nbsp;-&nbsp;Name for book. Prompted when run/<li>
<li>{{type}}}&nbsp;-&nbsp;This value is from the File Setting ; Filetype in preferences. </li>
<li>{{device}}}&nbsp;-&nbsp;GhostScript setting for 'Filetype'. For PNG this should be 'png16m'. This is changed dpending upon the Filetype you select.</li>
<li>{{debug}}}&nbsp;-&nbsp;Set to 'echo' if debug is turned on</li>
</ul>
<p>
The program will do a string replacement for each of these values. They must match <i>exactly</i>.
When the script is run, you will be able to run this in debug mode.
</p><p>
The script will be stored in the default music directory as 'convert-pdf.smc'. You can edit this with
any editor. If you change the music directory, the script will need to be moved manually to the new
location
</p>
"""


# if __name__ == "__main__":
#     app = QApplication()
#     settings = MusicSettings()
#     window = UiPreferences()
#     window.format_data()
#     window.show()
#     sys.exit(app.exec())
