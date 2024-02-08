"""
Database interface: All Program Constants

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from dataclasses import dataclass


Symbols = {
    'edit': '\U0000270D',
    'notebook': "\U0001F4D4",
    'notepage': "\U0001F4C4",
}


@dataclass(init=False, frozen=True)
class DbKeys():
    """
    Class contains all of the settings for labels and key default values.
    The home directory is still kept in the profile setting in order to 'bootstrap'

    The system stores
    """
    ENCODE_STR = 0
    ENCODE_B64 = 1
    ENCODE_PICKLE = 2
    ENCODE_BOOL = 3
    ENCODE_INT = 4

    VALUE_DEFAULT_RENDER_PDF = True
    VALUE_DEFAULT_DB_FILENAME = 'sheetmusic.sql'
    VALUE_DEFAULT_DIR = "~/sheetmusic"
    VALUE_DEFAULT_USER_SCRIPT_DIR = "~/sheetmusic/scripts"
    VALUE_FILE_PREFIX = 'page'
    VALUE_FILE_TYPE = 'png'
    VALUE_FILE_RES = '300'
    VALUE_GSDEVICE = 'png16m'
    VALUE_KEEP_ASPECT = True

    VALUE_PAGES_SINGLE = "single"
    VALUE_PAGES_SIDE_2 = "side_2"
    VALUE_PAGES_SIDE_3 = 'side_3'
    VALUE_PAGES_STACK_2 = "stack_2"
    VALUE_PAGES_STACK_3 = "stack_3"

    VALUE_SMART_PAGES = True
    VALUE_REOPEN_LAST = True
    VALUE_SCRIPT_CMD = '/bin/bash'
    VALUE_SCRIPT_SPLIT = ';'  # Split script variables with this char
    VALUE_SCRIPT_VAR = '-c'
    VALUE_LAST_IMPORT_DIR = '~'
    VALUE_RECENT_SIZE_MIN = 5
    VALUE_RECENT_SIZE_MAX = 20
    VALUE_SHOW_FILEPATH = True
    VALUE_RECENT_SIZE_DEFAULT = 10
    VALUE_SHEETMUSIC_DOC = 'sheetmusic_doc'
    VALUE_SHEETMUSIC_INDEX = "index.doc"
    VALUE_RENDER_PDF = False
    VALUE_USE_TOML_FILE = True

    ###
    #       STORED IN ONLY IN QPREFERENCES
    ###
    SETTING_DEFAULT_PATH_MUSIC_DB = 'dbPath'
    SETTING_DEFAULT_MUSIC_FILENAME = 'dbFile'

    ###
    #       STORED IN System or BookSettings
    ###
    SETTING_PAGE_LAYOUT = 'layout'  # Page layout (1/2)
    SETTING_KEEP_ASPECT = 'aspectRatio'  # Keep aspect ratio when resizing
    SETTING_SMART_PAGES = 'smart_pages'  # Use alternate pages for two page displays
    SETTING_RENDER_PDF = 'viewer_pdf'

    ###
    #       STORED ONLY IN System table
    ###
    SETTING_DEFAULT_IMGFORMAT = 'gsdevice'  # Which ghostscript device will we use
    SETTING_DEFAULT_PATH_MUSIC = 'sheetmusicPath'  # Where is the music folder?
    SETTING_PATH_USER_SCRIPT = 'userScriptDir'  # Where to store user scripts?
    SETTING_PAGE_EDITOR = 'pageEditor'  # Page editor
    SETTING_PAGE_EDITOR_SCRIPT = 'pageEditorScript'  # Script for page editor
    SETTING_DEFAULT_SCRIPT = 'script'  # What we will run for conversion
    SETTING_DEFAULT_SCRIPT_VAR = 'scriptvar'  # What 'extra' variables we will run
    # SETTING_FILE_PREFIX: sheet music output prefix: e.g. "page" for "page-nnn."
    SETTING_FILE_PREFIX = 'pagePrefix'
    SETTING_FILE_TYPE = 'file_type'  # File extension (type)
    SETTING_FILE_RES = 'resolution'  # Output resolution
    SETTING_BOOK_DEFAULT_GENRE = 'genre'  # Default genre selection
    SETTING_PDF_SCRIPT = 'pdfScript'  # The PDF conversion script template
    SETTING_LAST_BACKUP = 'last_backup'  # Where we stored the last backup
    # Logging enabled 1-9 are levels 0 is None.
    SETTING_LOGGING_ENABLED = 'logging_enabled'
    SETTING_VERSION = 'version'  # Database Version (current)

    #       book settings
    SETTING_LAST_BOOK_NAME = 'book'  # Last book opened.
    SETTING_LAST_BOOK_REOPEN = 'reopen'  # Should we reopen? BOOL (text)
    # SETTING_MAX_RECENT_SIZE: How many should show in 'Open Recent' file menu
    SETTING_MAX_RECENT_SIZE = 'size_booklist'
    SETTING_SHOW_FILEPATH = 'recentFilepath'
    # Read/Write toml file for configuration
    SETTING_USE_TOML_FILE = 'use_toml_file'

    #       window settings
    SETTING_WIN_GEOMETRY = 'geometry'
    SETTING_WIN_STATE = 'state'
    SETTING_WIN_POS = 'position'
    SETTING_WIN_SIZE = 'size'
    SETTING_WIN_ISMAX = 'ismaximized'
    SETTING_WIN_STATUS_ENABLED = 'statusbar'
    SETTING_WINDOW_STATE_SAVED = 'windowState'

    #       keyboard settings
    SETTING_PAGE_PREVIOUS = 'previousPage'
    SETTING_PAGE_NEXT = 'nextPage'
    SETTING_FIRST_PAGE_SHOWN = 'page_shownFirst'
    SETTING_LAST_PAGE_SHOWN = 'page_shownLast'
    SETTING_BOOKMARK_PREVIOUS = 'previousBookmark'
    SETTING_BOOKMARK_NEXT = 'nextBookmark'

    SETTING_LAST_IMPORT_DIR = 'importDir'
    SETTING_NAME_IMPORT = 'useInfoName'
    VALUE_NAME_IMPORT_PDF = 9
    VALUE_NAME_IMPORT_FILE_0 = 0           # Minimal cleanup only (bad chars)
    # Just use filename but get rid of characters
    VALUE_NAME_IMPORT_FILE_1 = 1
    VALUE_NAME_IMPORT_FILE_2 = 2           # Try and tidy up the filename more

    SETTING_IMPORT_SCRIPT = 'importScript'

    VALUE_DEFAULT_COMPOSER = 'Unknown'
    VALUE_DEFAULT_GENRE = 'Unknown'

    VALUE_PDF = 'pdf'
    VALUE_PNG = 'png'

    ###
    #       Settings for DbSettings only
    ###
    SETTING_EDIT_HISTORY = 'history'  # You need to store this as 'history_pagename'
    SETTING_EDIT_HISTORY_FORMAT = 'history_"{0:03d}'

    ###
    #       END DATABASE
    ###

    primaryKeys = {
        'Book':         ['book'],
        'BookSetting':  ['book_id'],
        'Composer':     ['name'],
        'Bookmark':     ['book_id'],
        'Genre':        ['name'],
    }

    # QSETTINGS_DICT is what is stored in the QSettings system prefs
    # Currently, this is just db path and filename
    QSETTINGS_DICT = {
        SETTING_DEFAULT_PATH_MUSIC_DB: VALUE_DEFAULT_DIR,
        SETTING_DEFAULT_MUSIC_FILENAME: VALUE_DEFAULT_DB_FILENAME,
    }

    # PREF_SYS_KEYS is what we store but user can't alter
    PREF_SYS_KEYS = [
        SETTING_WIN_GEOMETRY,
        SETTING_WIN_STATE,
        SETTING_WIN_POS,
        SETTING_WIN_SIZE,
        SETTING_WIN_ISMAX,
        SETTING_WIN_STATUS_ENABLED,
    ]


@dataclass(init=False, frozen=True)
class ImportNameSetting:
    """ Values used for importing into the system """
    forImportName = {
        "Only cleanup illegal characters from name":
            DbKeys.VALUE_NAME_IMPORT_FILE_0,
        "Use filename with minimal cleanup":
            DbKeys.VALUE_NAME_IMPORT_FILE_1,
        "Use filename with maximum cleanup and Title Name":
            DbKeys.VALUE_NAME_IMPORT_FILE_2}
