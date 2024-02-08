"""
Settings Interface : SystemPreferences

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import os

from PySide6.QtCore import QSettings

from qdb.keys import DbKeys
from qdb.dbconn import DbConn
from qdb.dbsystem import DbSystem
from ui.main import UiMain
from util.convert import ( decode, encode )

class DummyPreferences():
    """ this is used only for testing purposes."""
    tstor = []

    def is_protected(self, key: str) -> bool:
        """Check to see if a key is one of the protected values

        Args:
            key (str): test

        Returns:
            bool: True if protected, false if not
        """
        return key in DbKeys().QSETTINGS_DICT

    def set_value(self, key, value):
        """ Save data to dictionary """
        DummyPreferences.tstor[key] = value

    def value(self, key, default_value=None):
        """ Return stored value or default value """
        if key in DummyPreferences.tstor:
            return DummyPreferences.tstor[key]
        return default_value

    def get_all(self) -> dict:
        """
            getAll will only return USER available keys
        """
        rtn_dict = {}
        for key in DbKeys().QSETTINGS_DICT:
            rtn_dict[key] = self.value(key)
        return rtn_dict

    def save_all(self, changes: dict):
        """ save will write valid keys into the pref store """
        for key, value in changes.items():
            if key in DbKeys().QSETTINGS_DICT:
                self.set_value(key, value)

    def get_key_list(self) -> list[str]:
        """
            Return list of all special system keys
        """
        return DbKeys().PREF_SYS_KEYS

    @property
    def dbdirectory(self) -> str:
        """Return the system value for the database directory
        If no path is in the system, return default directory

        Returns:
            str: Full, expanded directory setting without filename
        """
        return os.path.expanduser(
            self.value(
                DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB,
                DbKeys.VALUE_DEFAULT_DIR))

    @dbdirectory.setter
    def dbdirectory(self, new_dir: str) -> None:
        """Set the directory path to the database.

        Args:
            new_dir (str): Directory path to db, without filename
        """
        self.set_value(DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB, new_dir)

    @property
    def dbname(self):
        """ get the database name used without path

        Returns:
            string: database name
        """
        return self.value(
            DbKeys.SETTING_DEFAULT_MUSIC_FILENAME,
            DbKeys.VALUE_DEFAULT_DB_FILENAME)

    @dbname.setter
    def dbname(self, new_file_name: str):
        """Set the name of the database file

        Args:
            new_file_name (str): Name of database file
                if you pass a path, it will strip off the path
                and use only the name

        """
        name = os.path.basename(os.path.realpath(new_file_name))
        self.set_value(DbKeys.SETTING_DEFAULT_MUSIC_FILENAME,  name)

    @property
    def dbpath(self) -> str:
        """Get the full, expanded path to the database

        Returns:
            str: expanded path to database
        """
        return os.path.join(
            self.dbdirectory,
            self.dbname
        )


class SystemPreferences(QSettings):
    """
    SystemPreferences is where we store all the directories, names, etc for the system interaction.
    All preferences are stored in a system independent way.
    N.B.: We only store key bits of information. Most of it is stored in the
    database, not here. Think of this as a 'pointer' interface.

    Keys are prefixed with 'PREF_SYS_'
    """
    DEFAULT_ORG = 'OrganMonkey project'
    DEFAULT_APP = 'SheetMusic'
    TEST_APP = 'SheetMusic_Test'

    def __init__(self, org=DEFAULT_ORG, app=DEFAULT_APP, reset=False):
        super().__init__(org, app)
        if reset:
            self.clear()
            self.save_all(DbKeys().QSETTINGS_DICT)
        # Save keys to the preferences.
        # (Note: this saves expanded paths.)
        for key, value in DbKeys().QSETTINGS_DICT.items():
            if value is not None and not self.contains(key):
                self.set_value(key, value)
        self.sync()

    def is_protected(self, key: str) -> bool:
        """Check to see if a key is one of the protected values

        Args:
            key (str): test

        Returns:
            bool: True if protected, false if not
        """
        return key in DbKeys().QSETTINGS_DICT

    def get_all(self) -> dict:
        """
            get_all will only return USER available keys
        """
        rtn_dict = {}
        for key in DbKeys().QSETTINGS_DICT:
            rtn_dict[key] = super().value(key)
        return rtn_dict

    def set_value(self, key, value):
        """Set the key to value in system settings
        if  it is a reserved key, we run it through the
        dedicated call (just in case )

        Args:
            key (str): primary key
            value (Any): What to set key to
        """
        if key == DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB:
            self.dbdirectory = value
        elif key == DbKeys.SETTING_DEFAULT_MUSIC_FILENAME:
            self.dbname = value
        else:
            super().setValue(key, value)

    def save_all(self, changes: dict):
        """ save will write valid keys into the pref store """
        for key, value in changes.items():
            if key in DbKeys().QSETTINGS_DICT:
                self.set_value(key, value)
        self.sync()

    def get_key_list(self) -> list[str]:
        """
            Return list of all special system keys
        """
        return DbKeys().PREF_SYS_KEYS

    @property
    def dbdirectory(self) -> str:
        """Return the system value for the database directory
        If no path is in the system, return default directory

        Returns:
            str: Full, expanded directory setting without filename
        """
        return os.path.expanduser(
            self.value(
                DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB,
                DbKeys.VALUE_DEFAULT_DIR))

    @dbdirectory.setter
    def dbdirectory(self, new_dir: str) -> None:
        """Set the directory path to the database.

        Args:
            new_dir (str): Directory path to db, without filename
        """
        super().setValue(
            DbKeys.SETTING_DEFAULT_PATH_MUSIC_DB,
            new_dir)

    @property
    def dbname(self):
        """ get the database name used without path

        Returns:
            string: database name
        """
        return self.value(
            DbKeys.SETTING_DEFAULT_MUSIC_FILENAME,
            DbKeys.VALUE_DEFAULT_DB_FILENAME)

    @dbname.setter
    def dbname(self, new_file_name: str):
        """Set the name of the database file

        Args:
            new_file_name (str): Name of database file
                if you pass a path, it will strip off the path
                and use only the name

        """
        super().setValue(
            DbKeys.SETTING_DEFAULT_MUSIC_FILENAME,
            os.path.basename(os.path.realpath(new_file_name))
        )

    @property
    def dbpath(self) -> str:
        """Get the full, expanded path to the database

        Returns:
            str: expanded path to database
        """
        return os.path.join(
            self.dbdirectory,
            self.dbname
        )

# disable too many public methods (22/20)
# pylint: disable=R0904


class DilPreferences():
    """
        This handles queries against system properties (database) or system preferences (qsettings)
        Note that you can pass the dbsystem and systempref in order to do unit testing.
     """

    def __init__(self, dbsystem: DbSystem = None, systempref: SystemPreferences = None):
        super().__init__()
        if dbsystem:
            self.dbsystem = dbsystem
        else:
            self.dbsystem = DbSystem()
        if systempref:
            self.systempref = systempref
        else:
            self.systempref = SystemPreferences()

    def __del__(self):
        """ Before deletion, commit all changes """
        DbConn.commit()

    @property
    def dbpath(self) -> str:
        """ Fetch the file path where database is stored """
        return self.systempref.dbpath

    @dbpath.setter
    def dbpath(self, new_path: str):
        self.systempref.dbpath = new_path

    @property
    def dbdirectory(self) -> str:
        """ Fetch the directory for the database """
        return self.systempref.dbdirectory

    @dbdirectory.setter
    def dbdirectory(self, new_path: str):
        self.systempref.dbdirectory = new_path

    @property
    def musicdir(self) -> str:
        """ Get directory where music images saved """
        return self.get_value(DbKeys.SETTING_DEFAULT_PATH_MUSIC)

    @musicdir.setter
    def musicdir(self, new_dir: str):
        self.set_value(DbKeys.SETTING_DEFAULT_PATH_MUSIC, new_dir)

    def get_value(self,
                  key: str,
                  default: str | int | bool = None) -> str:
        """
            Get the value from the DbSystem table
            if not found, get the value from the system preferences

            This is a base call from all special 'modal' calls
        """
        if self.systempref.is_protected(key):
            return self.systempref.value(key,
                                         default=default)
        return self.dbsystem.get_value(key,
                                       default=default)

    def set_value(self,
                  key: str,
                  value: str = None,
                  replace: bool = True,
                  ignore: bool = False) -> str:
        """ Set key to a value for a book """
        if self.systempref.contains(key):
            self.systempref.set_value(key, value)
        else:
            self.dbsystem.set_value(key, value, replace=replace, ignore=ignore)
        return value

    def get_all(self) -> dict:
        """ Retrieve all the values """
        s = self.systempref.get_all()
        d = self.dbsystem.get_all()
        return s | d

    def save_all(self, changes: dict) -> int:
        """
            Save changes first to the system preferences then to the database
        """
        self.systempref.save_all(changes)
        # get rid of system stuff
        for key in self.systempref.get_key_list():
            if key in changes:
                changes.pop(key)
        self.dbsystem.save_all(changes, replace=True)

    def update(self, ui):
        """ Update all the saved preferences """
        ui.format(self.get_all())
        ui.exec()
        self.save_all(ui.get_changes())

    def save_mainwindow(self, win):
        '''
        Save window attributes as settings.
        Called when window moved, resized, or closed.
        '''

        self.set_value(
            key=DbKeys.SETTING_WIN_STATE,
            value=encode(
                value=win.saveState(),
                code=DbKeys.ENCODE_PICKLE)
        )
        self.set_value(
            key=DbKeys.SETTING_WIN_GEOMETRY,
            value=encode(
                value=win.saveGeometry(),
                code=DbKeys.ENCODE_PICKLE)
        )
        self.set_value(
            key=DbKeys.SETTING_WIN_ISMAX,
            value=encode(
                win.isMaximized(),
                code=DbKeys.ENCODE_PICKLE)
        )
        self.set_value(
            key=DbKeys.SETTING_WINDOW_STATE_SAVED,
            value=encode( True,
                code=DbKeys.ENCODE_BOOL)
        )
        if not win.isMaximized() is True:
            self.set_value(
                key=DbKeys.SETTING_WIN_POS,
                value=encode(
                    value=win.pos(),
                    code=DbKeys.ENCODE_PICKLE)
            )
            self.set_value(
                key=DbKeys.SETTING_WIN_SIZE,
                value=encode(
                    value=win.size(),
                    code=DbKeys.ENCODE_PICKLE)
            )

    def restoremain_window(self, win):
        '''
        Read window attributes from settings,
        using current attributes as defaults (if settings not exist.)

        Called at QMainWindow initialization, before show().
        '''
        winstate = self.get_value(
                key=DbKeys.SETTING_WINDOW_STATE_SAVED,
                default=False)
        if decode(
            code=DbKeys.ENCODE_BOOL,
            value= winstate):

            win.restoreState(
                decode(
                    code=DbKeys.ENCODE_PICKLE,
                    value=self.get_value(
                        DbKeys.SETTING_WIN_STATE
                    )
                )
            )

            is_win_maximized = decode(
                    code=DbKeys.ENCODE_BOOL,
                    value=self.get_value(
                        DbKeys.SETTING_WIN_ISMAX,
                        default=False)
            )

            win.restoreGeometry(self.get_value(
                DbKeys.SETTING_WIN_GEOMETRY,
                DbKeys.ENCODE_PICKLE))

            win.move(self.get_value(
                DbKeys.SETTING_WIN_POS,
                DbKeys.ENCODE_PICKLE))

            win.resize( decode(
                code=DbKeys.ENCODE_PICKLE,
                value=self.get_value(
                    DbKeys.SETTING_WIN_SIZE,
                    )
                )
            )

            if is_win_maximized:
                win.showMaximized()

    def save_shortcut(self, win) -> None:
        """ Not currenty implemented """
        del win

    def restore_shortcuts(self, ui: UiMain):
        """Restore all shortcuts to the UI passed

        Args:
            ui (UiMain): Main User interface
        """
        values = self.get_all()
        ui.set_navigation_shortcuts(values)
        ui.set_bookmark_shortcuts(values)
