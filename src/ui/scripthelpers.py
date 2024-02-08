"""
 User interface : Scripthelprs

scripthelpers splits off support functions for runscript

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import platform
import re
import sys
import tempfile
import time

from os import path, chmod
from dataclasses import dataclass

from PySide6.QtCore import QProcess, Qt, QProcessEnvironment, QVersionNumber
from PySide6.QtWidgets import (
    QDialog,        QDialogButtonBox,
    QHBoxLayout,    QLineEdit,
    QMessageBox, QWidget,
)

from constants import ProgramConstants
from qdb.keys import DbKeys
from qdb.log import DbLog
from qdil.preferences import DilPreferences

from util.utildir import (get_scriptinc,
                          get_user_scriptinc, get_scriptdir,
                          get_user_scriptdir, get_os_class)

@dataclass(init=False, frozen=True)
class ScriptKeys:
    """ Class has all the constant values """
    # #:KEYWORD tags
    COMMENT = 'comment'
    DEBUG = 'debug'             # Within #:require - pass debug flag
    DIALOG = 'dialog'           # use simpledialog
    PICKER = 'picker'           # use OpenFile to pick a current book
    DIR = 'dir'                 # Directory request
    DIR_PROMPT = 'dir-prompt'   # ""
    FILE = 'file'
    FILE_FILTER = 'file-filter'
    FILE_PROMPT = 'file-prompt'
    FLAG = 'flag'
    INCLUDE = 'inc'             # Include another file (future)
    OPTIONS = 'options'         # See options, below
    OS = 'os'                   # Free-form option list
    # set the flag prefix for the script (default is -)
    PREFIX = 'prefix'
    REQUIRE = 'require'         # Fields required ( file / dir )
    SYSTEM = 'system'           # See information, below.
    TITLE = 'title'             # passed to script
    VARS = 'vars'               # Reserved for intenal use

    # 'INFORMATION' requests (after #:SYSTEM )
    DEBUG = 'debug'

    # DISPLAY CONTROL
    HEIGHT = 'height'           # separate line #:height n
    NOFRAME = 'noframe'         # Within #:require
    ONTOP = 'ontop'             # Within #:require
    SIMPLE = 'simple'           # Within #:require
    WIDTH = 'width'             # separate line:  #:width n

    # OS options
    OS_ANY = 'any'
    OS_LINUX = 'linux'
    OS_UNIX = 'unix'
    OS_BSD = 'bsd'
    OS_MACOS = 'macos'
    OS_WIN = 'win'

    # ENV SETTING
    ENV_DBFILE = 'DBFILE'
    ENV_DIR_SYS = 'SCRIPT_SYSTEM'
    ENV_DIR_USER = 'SCRIPT_USER'
    ENV_INC_SYS = 'INCLUDE_SYSTEM'
    ENV_INC_USER = 'INCLUDE_USER'
    ENV_MUSIC_DIR = 'MUSIC_DIR'
    ENV_PYTHON_RUN = 'PYTHON_RUN'
    ENV_PYTHON_VERSION = 'PYTHON_VERSION'
    ENV_QT_VERSION = 'QT_VERSION'
    ENV_SHEETMUSIC = 'SHEETMUSIC_VERSION'
    ENV_SYSTEM_OS = 'SYSTEM_OS'
    ENV_SYSTEM_CLASS = 'SYSTEM_CLASS'

    # DB export information
    ENV_IMG_RES = 'IMG_RES'
    ENV_IMG_TYPE = 'IMG_TYPE'
    ENV_LAST_BACKUP = 'LAST_BACKUP'
    ENV_IMG_FORMAT = 'IMG_FORMAT'


class UiScriptSetting():
    """ This will parse a scriptfile for known keys, values, and options """

    # SEARCH_TAGS looks for the tags formatted as:  #:<keyword> <options><end-of-line>
    SEARCH_TAGS = r'\s*#:([a-z-]+)\s+([^\n\r]*)'
    # SEARCH_KEYWORDS looks for:  <blanks><text><blanks<text><blanks>
    SEARCH_KEYWORDS = r'\s*(\w+)\s*(\w+)\s*'

    def __init__(self, filename: str, lines=None, deep: bool = True):
        """ Setup and to parse either a file or text.

        filename: File to open and parse.
        lines: parse lines already read and ignore filename
        deep: (future) this will continue to scan any 'include' links
        """

        self._fname = filename
        self.translate_tag_to_flag = {
            ScriptKeys.DIR:       ['d'],
            ScriptKeys.DEBUG:     ['X']}
        if lines is None:
            with open(filename, "r", encoding='utf-8') as f:
                script = f.read()
            self.parse(script, deep)
        else:
            self.parse(lines, deep)

    def parse_option_line(self, line: str):
        """ Parse one line for options."""
        matches = re.findall(UiScriptSetting.SEARCH_KEYWORDS, line)
        for match in matches:
            self.set_flag(match[0], match[1])
        if self.flag('prefix', 'dash') == 'dash':
            self.set_flag('prefix', '-')
        elif self.flag('prefix') == 'blank':
            self.set_flag('prefix', '')

    def parse_setting_line(self, line: str):
        """ This parses lines made up of keyword keyword keyword"""
        settings = line.split()
        for setting in settings:
            self.translate_tag_to_flag[setting] = [True]

    def is_option(self, option_type: str, option: str) -> bool:
        """Determine if 'option' is within the 'type' line.

            Typically used for #:system or #:require settings

        Args:
            option_type (str): which setting value to examine
            option (str): what string to look for

        Returns:
            bool: True if found, False if not
        """
        return self.setting_value(option_type).find(option) > -1

    def get_options(self, key: str = ScriptKeys.VARS) -> list:
        """ Return a list of options for a keyword. Can be used for #:system """
        return self.setting_value(key).split()

    def include(self, filename) -> None:
        """ Not currently implemented """
        del filename

    def parse(self, lines, deep) -> None:
        """ Parse will Parse all the lines and create a key/list entry"""
        if isinstance(lines, list):
            matches = re.findall(UiScriptSetting.SEARCH_TAGS, "\n".join(lines))
        else:
            matches = re.findall(UiScriptSetting.SEARCH_TAGS, lines)
        if len(matches) > 0:
            for match in matches:
                if match[0] in self.translate_tag_to_flag:
                    self.translate_tag_to_flag[match[0]].append(
                        match[1].strip())
                else:
                    self.translate_tag_to_flag[match[0]] = [match[1].strip()]
            if ScriptKeys.FLAG in self.translate_tag_to_flag:
                for line in self.translate_tag_to_flag[ScriptKeys.FLAG]:
                    self.parse_option_line(line)
            if deep:
                lines = self.setting(ScriptKeys.INCLUDE, [])

    def flag(self, key: str, default=None) -> str:
        """ return the flag for a key """
        if self.translate_tag_to_flag is not None and key in self.translate_tag_to_flag:
            return self.translate_tag_to_flag[key][0]
        return default

    def set_flag(self, key, value) -> None:
        """Set a translation flag to value

        Args:
            key (str): Key
            value (str): value to translate to
        """
        self.translate_tag_to_flag[key] = [value.strip()]

    def is_set(self, key: str) -> bool:
        """ Determine if 'key' is within the dictionary """
        return self.translate_tag_to_flag is not None and key in self.translate_tag_to_flag

    def setting(self, key: str, default=None) -> list:
        """ Return the list that is entered for the dictionary 'key' """
        if self.is_set(key):
            return self.translate_tag_to_flag[key]
        if default is None:
            return []
        if isinstance(default, list):
            return default
        return [default]

    def setting_value(self, key: str, default='') -> str:
        """ Set key to value and return the setting """
        return self.setting(key, default)[0]

    def settings(self) -> dict:
        """ Return flag setting """
        return self.translate_tag_to_flag

    def __str__(self) -> str:
        """ Convert all the tags to a string """
        rtn = ""
        for key, items in self.translate_tag_to_flag.items():
            rtn = rtn + f"Key: {key}\n"
            for item in items:
                rtn = rtn + f"\tValue: '{item}'\n"
        return rtn


class RunScriptBase():
    """
    Contains the process functions for running shell scripts

    ATTRIBUTES:
    ===========
    _process : QProcess
        Contains process object when script is running
    script_file : str
        full path to script to be run. Can be name of tempfile
    script_parms : UiScriptSetting object
        Created when script file is set. Use to pull parms from script
    _shell : str
        Contains shell program path for script execution
    process_state : QProcess.ProcessState
        Save the ProcessState when change is signalled
    _temp_file  : tempfile.NamedTemporaryFile
        Either None (no temp file) or temp file data for closure
    vars  : list
        List of parms to pass to shell script. For example: ['-D', '/where/is/dbfile' , '-X' ]

    OVERRIDES:
    ==========
    output_message( msg:str , override=None)->None
        Output msg to the user. Used during script execution
    notify_start( )->None
        Called when processing starts
    notify_end()->None
        Called when processing completes
    notify_script_change( script_file:str )->None
        When the script is changed, this is called.
    add_final_vars()->None
        Derived class can add other parms to list (Prefer to end)
    """

    shlist = ['/bin/bash',
              '/bin/zsh',
              '/bin/sh',
              '/usr/local/bin/bash',
              '/usr/local/bin/zsh',
              '/usr/local/bin']


    transfer_from_db = {
        ScriptKeys.ENV_IMG_RES: DbKeys.SETTING_FILE_RES,
        ScriptKeys.ENV_IMG_TYPE: DbKeys.SETTING_FILE_TYPE,
        ScriptKeys.ENV_LAST_BACKUP: DbKeys.SETTING_LAST_BACKUP,
        ScriptKeys.ENV_IMG_FORMAT: DbKeys.SETTING_DEFAULT_IMGFORMAT,
    }

    def __init__(self):
        """ Initialise all values used in program to None """
        self._extra_env = {}
        self._process = None
        self._current_state = None
        self._shell = None
        self._temp_file = None
        self.macro_replace = {}
        self.script_file = None
        self.script_parms = None
        self._script_text = None
        self.vars = None
        self.time_start = None
        self.dilpref = DilPreferences()

        # This should be instantiated in the derived script
        self.btn_list = {}

        self._logger = DbLog('RunScript')

    def __del__(self):
        self._close_temporary_file()

    def output_message(self, msg: str, override=None, mode: str = 'stdout') -> None:
        """ override - optional
            Outputs messages to the user as the program runs
            All our message processing for output runs through here.
        """
        del msg, override, mode

    def notify_start(self):
        """ override - optional
            Call when the program is about to start
        """
        return None

    def notify_end(self, msg: str)->None:
        """ override
            Call when the program has completed
        """
        del msg


    def notify_script_change(self, script_name: str) -> None:
        ''' override '''
        del script_name


    def process_status(self, msg):
        ''' override '''
        del msg


    def add_final_vars(self):
        """ override- optional Child class last chance to add more variables """
        return

    def _close_temporary_file(self):
        if self._temp_file is not None:
            self._temp_file.close()
            self._temp_file = None

    def _create_temporary_file(self):
        """ Generate a temporary file from the scriptText and set flag"""
        try:
            self._temp_file = tempfile.NamedTemporaryFile(mode="w+")
            self._temp_file.write(self._script_text)
            self._temp_file.flush()
            self.script_file = self._temp_file.name
            chmod(self.script_file, 0o550)
        except Exception as err:
            QMessageBox.critical(None,
                                 "",
                                 "Error creating temporary file\n" + str(err),
                                 QMessageBox.StandardButton.Cancel)
            self._close_temporary_file()
            return False
        return True

    def variable_flag(self, tag: str) -> str:
        """ Add tag to script 'PREFIX-tag = tag"""
        return f"{self.script_parms.setting_value(ScriptKeys.PREFIX, '-')}\
            {self.script_parms.setting_value(tag, tag)}"

    def add_variable_flag(self, tag: str, front=False) -> None:
        """
        Add just the tag to self.vars based on UiScriptSetting

        For example, if you want 'debug' and call it as:
        add_variable_flag( ScriptKeys.DEBUG ) it will add ['-X']
        """
        if front:
            self.vars.insert(0, self.variable_flag(tag))
        else:
            self.vars.append(self.variable_flag(tag))

    def add_variable(self, tag: str, value: str, front=False) -> None:
        """
        Add the tag and value to the self.vars list based on UiScriptSetting values

        An example: if you want to have the script file added, you waould call it as
            add_variable( ScriptKeys.SCRIPT , self.script_file )
        and it would add:
            ['-Z' , '/script/file/path' ]
        """
        if front:
            self.vars.insert(0, value)
            self.add_variable_flag(0, tag)
        else:
            self.vars.append(self.variable_flag(tag))
            self.vars.append(value)

    def add_includes_to_vars(self):
        """ Currently not implemented """
        return None

    def add_system_to_vars(self):
        """ Add to vars list based on '#:system' tag in script file """
        if self.script_parms.is_set(ScriptKeys.SYSTEM):
            for key in self.script_parms.get_options(ScriptKeys.SYSTEM):
                if key == ScriptKeys.DEBUG:
                    self.add_debug_to_vars()

    def add_debug_to_vars(self, debug: bool = False):
        """ Turn on debugging """
        if debug:
            self.macro_replace['DEBUG'] = True
            self.add_variable_flag(ScriptKeys.DEBUG, front=False)

    def add_script_to_vars(self):
        """ Add script to the very first position in the variables being passed """
        self.vars.insert(0, self.script_file)

    def save_script(self, script, is_file: bool = True) -> bool:
        """ Save the script to file and setup script parameter class """
        self.script_file = script
        if is_file:
            if not path.isfile(script):
                QMessageBox.critical(None,
                                     "",
                                     "Script not found:\n" + script,
                                     QMessageBox.StandardButton.Cancel)
                return False
            with open(self.script_file, 'r', encoding='utf-8') as f:
                self._script_text = f.read()

        self.script_parms = UiScriptSetting(
            self.script_file, self._script_text, is_file)
        return True

    def set_script(self, script: str,
                   script_vars: list = None, env: dict = None,
                   is_file: bool = True) -> bool:
        """Save the script and notify child we changes script status

        This closes previous file, resets the variables passed to shell script
        and will notify the child class of the script change.

        Args:
            script (str): script filename or string
            script_vars (list, optional): Script variables. Defaults to None.
            env (dict, optional): Environment to set. Defaults to None.
            is_file (bool, optional): Is this a file or a script string. Defaults to True.

        Returns:
            bool: _description_
        """
        self._close_temporary_file()
        self.vars = script_vars if script_vars is not None else []
        self._extra_env = env if env is not None else {}
        if script is None or len(script) < 2:
            QMessageBox.critical(None,
                                 "",
                                 "Empty script passed",
                                 QMessageBox.StandardButton.Cancel)
            return False

        self.save_script(script, is_file)
        self.add_includes_to_vars()
        self.add_system_to_vars()
        self.notify_script_change((script if is_file else None))
        return True

    def reset(self):
        """ This clears the variables, resets the key ones from the script """
        self.vars = []
        self.add_includes_to_vars()
        self.add_system_to_vars()

    def wait_for_process(self) -> None:
        """ Wait for script process to end """
        if self._process is not None:
            self._process.waitForFinished(-1)

    def cancel_process(self) -> None:
        """ Cancel the process currently running """
        if self._process is not None and self._process.state() == QProcess.ProcessState.Running:
            self.btn_list['Execute'].hide()
            self.btn_list['Close'].hide()
            self.btn_list['Cancel'].hide()
            self._process.kill()
            self._process.waitForFinished()
            self.btn_list['Close'].show()

    def add_to_environment(self, env_dict: dict) -> None:
        """Add dictionary to environment for script

        Args:
            env_dict (dict): Key / value pairs
        """
        self._extra_env = env_dict

    def _add_to_environment(self, env: QProcessEnvironment, extra: dict) -> None:
        """Process the environment variables

        Args:
            env (QProcessEnvironment): Environment
            extra (dict): Any extra dictionary values to add
        """
        self._remove_from_environment(env, extra)
        for key, value in extra.items():
            env.insert(key, value)

    def _remove_from_environment(self, env: QProcessEnvironment, extra: dict) -> None:
        """Remove duplicate dictionary values

        Args:
            env (QProcessEnvironment): Q Process
            extra (dict): Extra values.
        """
        for key in extra.keys():
            env.remove(key)

    def setup_environment(self):
        """ Add in environment variables that are standard for all runs """
        dilpref = DilPreferences()

        env = QProcessEnvironment.systemEnvironment()

        env.insert(ScriptKeys.ENV_INC_SYS, get_scriptinc())
        env.insert(ScriptKeys.ENV_DIR_SYS, get_scriptdir())
        env.insert(ScriptKeys.ENV_INC_USER, get_user_scriptinc())
        env.insert(ScriptKeys.ENV_DIR_USER, get_user_scriptdir())

        env.insert(ScriptKeys.ENV_MUSIC_DIR, dilpref.dbdirectory)
        env.insert(ScriptKeys.ENV_DBFILE, dilpref.dbpath)
        env.insert(ScriptKeys.ENV_SYSTEM_OS, platform.platform(terse=True))
        env.insert(ScriptKeys.ENV_SYSTEM_CLASS, get_os_class())

        env.insert(ScriptKeys.ENV_QT_VERSION, QVersionNumber.toString())
        env.insert(ScriptKeys.ENV_PYTHON_VERSION, platform.python_version())
        env.insert(ScriptKeys.ENV_PYTHON_RUN, sys.executable)
        env.insert(ScriptKeys.ENV_SHEETMUSIC, ProgramConstants.VERSION)
        keys = [ScriptKeys.ENV_INC_SYS, ScriptKeys.ENV_DIR_SYS,
                ScriptKeys.ENV_INC_USER, ScriptKeys.ENV_DIR_USER,
                ScriptKeys.ENV_MUSIC_DIR, ScriptKeys.ENV_DBFILE,
                ScriptKeys.ENV_SYSTEM_OS, ScriptKeys.ENV_QT_VERSION,
                ScriptKeys.ENV_PYTHON_VERSION, ScriptKeys.ENV_PYTHON_RUN,
                ScriptKeys.ENV_SHEETMUSIC,
                ScriptKeys.ENV_SYSTEM_CLASS] + list(self._extra_env.keys())

        # Transfer default settings from database
        for env_key, db_key in RunScriptBase.transfer_from_db.items():
            env.insert(env_key, dilpref.get_value(db_key))
            keys.append(env_key)

        # This overrides any defaults we have set in the DB
        self._add_to_environment(env, self._extra_env)
        env.insert('SHEETMUSIC_ENV', ':'.join(keys))

        self._process.setProcessEnvironment(env)

    def start_process(self):
        """
        start_process will setup and execute the shell script that is in the self._scriptfile.

        Only one process can run at a time. self_process hold the QProcess state.
        """

        if self._process is None:  # No process running.
            # Keep a reference to the QProcess (e.g. on self) while it's running.
            self._process = QProcess()
            self._process.readyReadStandardOutput.connect(self._process_stdout)
            self._process.readyReadStandardError.connect(self._process_stderr)
            self._process.stateChanged.connect(self._process_state)
            self._process.errorOccurred.connect(self._process_error)
            # Clean up once complete.
            self._process.finished.connect(self._process_finished)

            try:
                self.setup_environment()
                self.add_script_to_vars()
                self.add_final_vars()
                self.time_start = time.perf_counter()
                self._process.setProgram(self.shell())
                self._process.setArguments(self.vars)
                self._process.start()
                if not self._process.waitForStarted():
                    self._logger.critical('Process did not start')
            except Exception as err:
                self._close_temporary_file()
                raise err

    def get_current_status(self):
        """
        Call this to get the current state of the process
        """
        if self._current_state is None:
            return QProcess.NotRunning
        return self._current_state

    def _process_stderr(self) -> None:
        """ Output error messages """
        data = self._process.readAllStandardError()
        stderr_msg = "ERROR: " + bytes(data).decode("utf8", errors='ignore')
        self.output_message(stderr_msg, mode='stderr')

    def _process_stdout(self) -> None:
        """ Output standard messages """
        data = self._process.readAllStandardOutput()
        stdout_msg = bytes(data).decode("utf8").strip()
        if 'code>' in stdout_msg or 'pre>' in stdout_msg:
            self.output_message(stdout_msg, override='html', mode='stdout')
        else:
            self.output_message(stdout_msg, mode='stdout')

    def _process_state(self, state) -> None:
        """ Handle starting / Running state changes """
        self._current_state = state
        if state == QProcess.Starting:
            self.time_start = time.perf_counter()
        if state == QProcess.Running:
            self.notify_start()

    def _process_finished(self) -> None:
        """ Processing finished. Output messages and status"""
        total_time = time.perf_counter() - self.time_start
        minutes, sec = divmod(total_time, 60)
        hour, minutes = divmod(minutes, 60)
        self.notify_end(
            f"Script done. Total time: {hour:2.0f}:{minutes:02.0f}:{sec:02.0f}")
        self._close_temporary_file()
        self.time_start = None

    def _process_error(self, error):
        """
        If a process error occurs then a popup message box will be shown
        """
        self._close_temporary_file()
        match error:
            case QProcess.FailedToStart:
                msg = "Program didn't start. Check script for errors."
            case QProcess.Crashed:
                msg = "Process crashed."
            case QProcess.Timedout:
                msg = "While waitFor calls, timeout"
            case QProcess.WriteError:
                msg = "While writing from script"
            case QProcess.ReadError:
                msg = "While reading from script"
            case _:
                msg = "General script error"
                if isinstance(error, str):
                    msg = f"{msg}\n{error}"

        QMessageBox.critical(None,
                             "",
                             "Error running script\n" + msg,
                             QMessageBox.StandardButton.Cancel)

    def set_shell(self, cmd) -> bool:
        """ set_shell sets the command to anything passed and returns true if there was a value"""
        self._shell = cmd
        return (self._shell is not None and len(self._shell) > 0)

    def set_shell_preferences(self) -> bool:
        """ SetShell will set the shell command from the system preferences setting"""
        self._shell = self.dilpref.get_value(DbKeys.SETTING_DEFAULT_SCRIPT, None)
        return (self._shell is not None and len(self._shell) > 0)

    def set_system_shell(self) -> bool:
        """ set_system_shell willl (eventually) look at the system type and fill in how to
            run the program. For now, it only works on UNIX systems that have a standard
            shell program (like /bin/bash)
        """
        for shell in enumerate(RunScriptBase.shlist):
            if path.exists(shell):
                self.set_shell(shell)
                return True
        return False

    def shell(self) -> str:
        """ shell will retrieve the shell setting from whatever we have set
            If none has been set explicity, then get first the shell from preferences,
            then a shell from the system list
            IF none are found, 'None' is returend.
        """
        if self._shell is None:
            if not self.set_shell_preferences() and not self.set_system_shell():
                self._shell = None
                QMessageBox.critical(None,
                                     "Runtime Error",
                                     "No shell program found to run script",
                                     QMessageBox.StandardButton.Cancel)
        return self._shell


class DialogSettings():
    """
        Set either the window title or create space in the area of the buttons
    """

    def __init__(self):
        self._bottom_text = None
        self._bottom_widget = None
        self._bottom_layout = None

    def generate(self,
                 script_parms: UiScriptSetting,
                 buttons: QDialogButtonBox) -> QDialogButtonBox:
        """Generate a dialog box with scripts and buttons

        Args:
            script_parms (UiScriptSetting): script parameters
            buttons (QDialogButtonBox): button box

        Returns:
            QDialogButtonBox: Button box
        """
        if script_parms.is_option(ScriptKeys.REQUIRE, ScriptKeys.NOFRAME):
            self._bottom_widget = QWidget()
            self._bottom_text = QLineEdit()
            self._bottom_text.setReadOnly(True)

            self._bottom_layout = QHBoxLayout()
            self._bottom_layout.addWidget(self._bottom_text)
            self._bottom_layout.addWidget(buttons)
            self._bottom_widget.setLayout(self._bottom_layout)
            return self._bottom_widget
        return buttons

    def set(self, script_parms: UiScriptSetting, dlg: QDialog):
        """ set will set the title, frame setting, and the ontop hint."""
        title = script_parms.setting_value(ScriptKeys.TITLE, 'Script')
        if self._bottom_text is not None:
            self._bottom_text.setText(title)
        else:
            dlg.setWindowTitle(title)

        dlg.setWindowFlag(Qt.FramelessWindowHint, script_parms.is_option(
            ScriptKeys.REQUIRE, ScriptKeys.NOFRAME))
        if script_parms.is_option(ScriptKeys.REQUIRE, ScriptKeys.ONTOP):
            dlg.setWindowFlag(Qt.WindowStaysOnTopHint, True)
