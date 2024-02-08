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

"""
runscript will run the system shell and pass it several variables
The first variable will be the shell script. Other variables can be
passed in a list. For example, if you have a file 'doit.sh' and you
you want to pass it two filenames (/dir/a.txt and /dir/b.txt) you would
call the runner as:
    myrun = UiRunScript( 'doit.sh', [ '/dir/a.txt' , '/dir/b.txt'])
    myrun.run()
##
This will handle several tags within the script:
    :title  Title of the script to put into the top label
        (ignored for shell scripts at this point)
    :comment This can be a multi-line comment. that will be
        displayed in the box before it begins
    :width  How WIDE to set the dialog. Max is 2048, min 500
    :heigth Just how HIGH do you want the box. Max is 1024, min 500
    :inc    file to include (for settings)
        allows you to have global settings for flag, setting, etc.
        File must be relative to the tool directory ( inc/file )
    :flag   keywords that control how parameters are passed
        example: #:flag file f prefix dash dir d version v

        prefix  - either 'dash' or 'blank'  default DASH
        file    - tag used for passing file entry
        dir     - tag used for passing directory entry
        version - tag used for versioning
        dbfile  - tag used for passing database file
##
    :setting setting values
        dbfile   where db is located (path)
        version  current code version
##
    :require what (optional) values must be entered
        file    if there is a file-prompt, make file required
    dir     if there is a dir-prompt,  make directory required
##
RESERVED WORDS FOR TAGS:
    title, comment, width, height, inc, flag, prefix, file, dir, version, dbfile, setting
"""


import time

from os import path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,   QDialog,        QDialogButtonBox,
    QFileDialog, QLineEdit,
    QMessageBox, QPlainTextEdit, QTabWidget,
    QVBoxLayout, QWidget,
)

from constants import ProgramConstants
from ui.simpledialog import SimpleDialog, SDOption
from ui.scripthelpers import (
        ScriptKeys,
        RunScriptBase, DialogSettings )
from ui.file import Openfile
from util.convert import to_int


class UiRunScript(RunScriptBase):
    """
        Run a script based on values in the script file.
        This does not provide any prompting for files/dirs/etc.

        Tags that are used
        ==================
            #:comment multi-line comment displayed before execution
            #:require debug ontop noframe
            #:title   Script title for user
            #:width   int
            #:height  int

        Attributes (well, important ones)
        =================================
        btn_debug : QCheckBox
            Displayed if script '#:require' contains 'debug'
        text - QPlainTextEdit
            Set to read-only, contains output from program: title, comments, stdout and stderr
        text_scriptname  : QLineEdit
            Set read-only, contains script name and final runtime status
        text_script : QPlainTextEdit
            Contains contents of script
        tab_layout : QTabWidget
            Contains two tabs: Output and Script. Double click Script to show runtime variables
        dlg_w : int
            Width of dialog box
        dlg_h : int
            Height of dialog box

        """

    def __init__(self,
                 script: str,
                 script_vars: list = None,
                 env:dict=None,
                 is_file=True,
                 output_dest='plain') -> None:
        """
        Setup the runscript values

        script can be text of script to run or a file path.
        vars is  a aof options to pass as variables to script
        is_file : true when passed a filename rather than a script
        output_dest must be a 'none', 'stdout' or 'plain'
        """
        super().__init__()
        self.btn_list = None
        self.debug_mode = False
        self.tab_layout = None
        self._script_save = None
        self.btn_debug = None

        self.titler = None
        self.create_text_fields()
        if self.set_script(script, script_vars, env=env, is_file=is_file):
            width = min(2048, to_int(self.script_parms.setting_value(
                ScriptKeys.WIDTH, '600'), 600))
            height = min(1024, to_int(self.script_parms.setting_value(
                ScriptKeys.HEIGHT, '700'), 700))
            self.set_size(width, height)
            self.set_output(output_dest)
            self.status = ProgramConstants.RETURN_CONTINUE
        else:
            self.status = ProgramConstants.RETURN_CANCEL

    def notify_start(self):
        """ Clear the general text field when process starts """
        self.text.clear()
        if self.btn_list is not None:
            self.btn_list['Execute'].hide()
            self.btn_list['Close'].hide()
            self.btn_list['Cancel'].show()

    def notify_end(self, msg: str) -> None:
        """ Write the end message on the text file line and move cursor to top of output """
        self.output_message("Script complete.", mode='stdout')
        self.text_scriptname.setText(msg)
        self.text.moveCursor(QTextCursor.Start)
        if self.btn_list is not None:
            self.btn_list['Execute'].show()
            self.btn_list['Close'].show()
            self.btn_list['Cancel'].hide()

    def output_message(self, msg: str, override=None,  mode: str = 'stdout') -> None:
        """ output_message will output the current state to the text in output tab

        It can either output to a plain or regular text edit box
        If you sent 'stdout' it will print to the console instead.
        """
        use = self.use if override is None else override
        if use == 'plain':
            self.text.appendPlainText(msg)
        elif use == 'text':
            self.text.appendPlainText(msg)
        elif use == 'html':
            self.text.appendHtml(msg)
        elif use == 'stdout':
            print(f"Script: {msg}")

    def notify_script_title_comment(self) -> bool:
        """ If the script has #:title / #:comment entries, display in output box """
        if self.script_parms.is_set(ScriptKeys.TITLE):
            title = self.script_parms.setting_value(ScriptKeys.TITLE)
            if len(title) > 0:
                sep = '='*len(title)
                msg = f"<b>{sep}<br/>&nbsp;{title}<br/>{sep}</b>"
                self.output_message(msg, 'html')
        if self.script_parms.is_set(ScriptKeys.COMMENT):
            cmt = '<br/>'.join(self.script_parms.setting(ScriptKeys.COMMENT, ''))
            self.output_message(
                f"<br/><p>{cmt}</p><br/>"
                'html')
        return True

    def notify_script_change(self, script_name: str) -> None:
        """Add text name for script title change

        Args:
            script_name (str): Script text
        """
        self.text_script.setPlainText(self._script_text)
        if script_name is not None:
            self.text_scriptname.setText(f"Script: {script_name}")
        else:
            self.text_scriptname.setText(self.script_parms.setting_value(
                ScriptKeys.TITLE, 'Script passed by program'))

    def set_output(self, output_dest:str=None):
        """ Set the output destination
        Can be one of 'plain', 'text', 'none'
        """
        self.use = 'stdout'
        if output_dest in ['plain',  'text', 'none']:
            self.use = output_dest

    def _get_button_list(self, btn_box: QDialogButtonBox):
        btn_list = {}
        for button in btn_box.buttons():
            btn_list[button.text()] = button
        return btn_list

    def _run_buttons(self):
        btn_box = QDialogButtonBox()
        btn_box.addButton('Execute', QDialogButtonBox.AcceptRole)
        btn_box.addButton(QDialogButtonBox.Close)
        btn_box.addButton(QDialogButtonBox.Cancel)
        self.btn_list = self._get_button_list(btn_box)
        self.btn_list['Close'].hide()
        return (btn_box, self.btn_list)

    def _debug_buttons(self):
        """ Debug will be shown if there is a debug in the script, otherwise it will be hidden """
        self.btn_debug = QCheckBox('Debug')  # Added later to display
        self.btn_debug.setObjectName('Debug')
        self.btn_debug.setCheckable(True)
        self.btn_debug.setChecked(False)
        self.btn_debug.setHidden(not self.script_parms.is_option(
            ScriptKeys.REQUIRE, ScriptKeys.DEBUG))
        return self.btn_debug

    def _run_tab_layout(self):
        tab_layout = QTabWidget()
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.text_scriptname)
        vlayout.addWidget(self._debug_buttons())
        vlayout.addWidget(self.text)
        w = QWidget()
        w.setLayout(vlayout)
        tab_layout.addTab(w, "Output")
        tab_layout.setTabText(0, "Output")

        tab_layout.addTab(self.text_script, "Script")
        tab_layout.setTabText(1, "Script")

        return tab_layout

    def create_text_fields(self):
        """create text input fields
        """
        plain_font = QFont()
        plain_font.setFixedPitch(True)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.text_scriptname = QLineEdit()
        self.text_scriptname.setReadOnly(True)

        self.text_script = QPlainTextEdit()
        self.text_script.setFont(plain_font)

    def _action_single_click_tab(self, index) -> None:
        if index != 1 and self.tab_layout.tabText(1) != 'Script':
            self._action_double_click_tab(1)

    def _action_double_click_tab(self, index) -> None:
        """ If the user double clicks on the script tab, it will show script parameters """
        if index == 1:
            if self.tab_layout.tabText(index) == 'Script':
                self._script_save = self.text_script.toPlainText()
                self.tab_layout.setTabText(index, 'Runtime')
                self.text_script.clear()
                self.text_script.insertPlainText(
                    f"Shell command: {self.shell()}\n")
                self.text_script.insertPlainText(
                    f"Script file: {self.script_file}\n\n")
                self.text_script.insertPlainText(
                    "Variables passed to shell by position:\n")
                for i, script_var in enumerate( self.vars):
                    self.text_script.insertPlainText(
                        f"   {i+1}: '{script_var}'\n")
            else:
                self.tab_layout.setTabText(index, 'Script')
                self.text_script.setPlainText(self._script_save)
                del self._script_save

    def is_debug(self) -> bool:
        """ Return True if we are in debug mode """
        return self.debug_mode

    def _prompt_for_file(self) -> bool:
        # See about any 'dialog' displays we have to do first
        if self.script_parms.is_set(ScriptKeys.PICKER):
            of = Openfile('Select Book to Resize')
            of.exec()
            if of.bookSelected is None:
                return False
            self.add_variable('PICKER', of.bookSelected)
        return True

    def _user_dialog(self , no_dialog:bool=False) -> bool:
        if not no_dialog and self.script_parms.is_set(ScriptKeys.DIALOG):
            sd = SimpleDialog()
            try:
                sd.parse(self.script_parms.setting(
                    ScriptKeys.DIALOG), self.macro_replace)
                if QMessageBox.Rejected == sd.exec():
                    return False
            except (ValueError, RuntimeError) as err:
                QMessageBox.critical(None,
                                     "Script error",
                                     "Script has a dialog error and cannot run:\n" +
                                     str(err),
                                     QMessageBox.StandardButton.Cancel)
                return False
            self._add_vars_from_simple_dialog(sd)
        return True

    def _add_vars_from_simple_dialog(self, sd: SimpleDialog) -> None:
        for entry in sd.data:
            self.add_variable(entry[SDOption.KEY_TAG],
                              entry[SDOption.KEY_VALUE])

    def run(self,
            start_msg: str = "Hit Execute button to run program",
            no_dialog:bool=False) -> bool:
        """
        run is the interface between the dialog box displaying information and the
        actual process that will be executed.

        It will run dialog interaction_s unless you set no_dialog

        It returns True to continue, False to Cancel
        """

        def button_clicked(button):
            match button.text().strip():
                case 'Execute':
                    self.status = ProgramConstants.RETURN_CONTINUE
                    btn_list['Execute'].setDisabled(True)
                    self.debug_mode = self.btn_debug.isChecked()
                    self.add_debug_to_vars(self.debug_mode)
                    self.text.clear()
                    self.start_process()

                    # don't close dialog box!

                case 'Cancel':
                    self.cancel_process()
                    self.status = ProgramConstants.RETURN_CANCEL
                    dlg_run.reject()

                case _:
                    self.status = ProgramConstants.RETURN_CONTINUE
                    dlg_run.accept()

        if self.status == ProgramConstants.RETURN_CONTINUE:
            if not self._prompt_for_file() or not self._user_dialog(no_dialog):
                self.status = ProgramConstants.RETURN_CANCEL
                return ProgramConstants.RETURN_CANCEL

            self.tab_layout = self._run_tab_layout()
            self.tab_layout.tabBarDoubleClicked.connect(
                self._action_double_click_tab)
            self.tab_layout.tabBarClicked.connect(self._action_single_click_tab)
            (btn_box, btn_list) = self._run_buttons()
            btn_box.clicked.connect(button_clicked)

            self.titler = DialogSettings()
            run_layout = QVBoxLayout()
            run_layout.addWidget(self.tab_layout)
            run_layout.addWidget(self.titler.generate(
                self.script_parms, btn_box))

            dlg_run = QDialog()
            dlg_run.setLayout(run_layout)
            dlg_run.setMinimumHeight(500)
            dlg_run.setMinimumWidth(500)
            self.titler.set(self.script_parms, dlg_run)
            dlg_run.resize(self.dlg_w, self.dlg_h)
            self.notify_script_title_comment()
            self.output_message(start_msg)
            dlg_run.exec()

        return self.status

    def set_size(self, w: int, h: int) -> None:
        """ Set the width and height of the dialog box"""
        self.dlg_w = w
        self.dlg_h = h


class UiRunScriptFile(UiRunScript):
    """
    Run a script that may require a filename / Directory *** OBSOLETE *** Use UiRunSimpleNote

    Tags that are used (in addtion to UiRunScript)
    ==============================================
        #:file-prompt  message
        #:file-filter ( type, type )
        #:dir-prompt   message
        #:require      file dir noframe ontop

    if file or directory are required, the tag
        #:require
    should contain the required values: file dir
    If no require, the files are considered optional
    """

    def __init__(self,
                 script: str,
                 script_vars: list = None,
                 is_file: bool = True,
                 output_dest='plain') -> None:
        super().__init__(script, script_vars, is_file, output_dest)
        self._float_text = None
        if self.status:
            self.create_float_window()
            self.prompt_file_dir()
            self.float_hide()

    def __del__(self):
        if ProgramConstants.ISMACOS and hasattr(self, '_float_text'):
            del self._float_text
        super().__del__()

    def create_float_window(self):
        """ Create a floating text window for status"""
        if ProgramConstants.ISMACOS:
            self._float_text = QPlainTextEdit()
            self._float_text.setWindowFlag(Qt.FramelessWindowHint, True)
            self._float_text.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self._float_text.setPlainText("")
            self._float_text.setGeometry(10, 10, 200, 75)

    def float_text(self, txt: str) -> None:
        """ Set text for floating text box"""
        if ProgramConstants.ISMACOS:
            self._float_text.setPlainText(txt)
            self._float_text.show()

    def float_hide(self) -> None:
        """Hide floating text box"""
        if ProgramConstants.ISMACOS:
            self._float_text.hide()

    def required_field_error(self, msg: str) -> bool:
        """ Prompt with an error giving them another chance
            unless the dialog box is gone
        """
        title = self.script_parms.setting_value(ScriptKeys.TITLE)

        self.status = QMessageBox.question(None,
                                           "Tool Script",
                                           f"Script '{title}'\n{msg}",
                                           QMessageBox.Retry, QMessageBox.Cancel)
        self.status = self.status == QMessageBox.Retry
        return self.status

    def prompt_file_dir(self):
        """ Prompt for missing file dirs """
        while not self.prompt_file():
            if not self.required_field_error('File is required.'):
                return

        while not self.prompt_dir():
            if not self.required_field_error('Directory is required.'):
                return


    def prompt_file(self) -> bool:
        """ Prompt for file """
        prompt = self.script_parms.setting_value(ScriptKeys.FILE_PROMPT, '')
        pfilter = self.script_parms.setting_value(ScriptKeys.FILE_FILTER, '')
        required = self.script_parms.is_option(ScriptKeys.REQUIRE, 'file')

        if prompt == '':
            return not required

        dlg = QFileDialog(caption=prompt, filter=pfilter)
        dlg.setFileMode(QFileDialog.ExistingFile)
        self.float_text(prompt)
        if dlg.exec():
            filenames = dlg.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                if not path.isfile(filename):
                    return not required
                self.output_message(f"{prompt}: {filename}")
                self.add_variable(ScriptKeys.FILE, filename, front=False)
                return True
        self.output_message(f"{prompt}: (none)")
        return not required

    def prompt_dir(self) -> bool:
        """ Prompt for directory """
        prompt = self.script_parms.setting_value(ScriptKeys.DIR_PROMPT, '')
        required = self.script_parms.is_option(ScriptKeys.REQUIRE, 'dir')

        if prompt == '':
            return not required

        self.float_text(prompt)
        new_directory_name = QFileDialog.getExistingDirectory(None, prompt)

        if new_directory_name:
            if not path.isdir(new_directory_name):
                return not required
            self.output_message(f"{prompt}: {new_directory_name}")
            self.add_variable(ScriptKeys.DIR, new_directory_name, front=False)
            return True
        self.output_message(f"{prompt}: (none)")
        return not required


class UiRunSimpleNote(RunScriptBase):
    """
    Display any dialogs asked for, run the script and only show a close button.

    Tags that are used:
    ==============================================
        #:require   file dir noframe ontop simple
        #:title     name to display to user
        #:width     n
        #:height    n
        #:dialog    ".....( passed to simple dialogue )

    """

    def __init__(self, script: str,
                script_vars:
                list = None,
                env:dict=None,
                is_file=True,
                output_dest='text') -> None:
        """
        Setup the runscript values

        script can be text of script to run or a file path.
        vars is  a aof options to pass as variables to script
        is_file : true when passed a filename rather than a script
        output_dest must be a 'none', 'stdout' or 'plain'
        """
        super().__init__()

        if self.set_script(script, script_vars, env=env, is_file=is_file):
            width = min(2048, to_int(self.script_parms.setting_value(
                ScriptKeys.WIDTH, '600'), 600))
            height = min(1024, to_int(self.script_parms.setting_value(
                ScriptKeys.HEIGHT, '700'), 700))
            self.set_size(width, height)
            self.set_output(output_dest)
            self.create_output_fields()
            self.status = ProgramConstants.RETURN_CONTINUE
        else:
            self.status = ProgramConstants.RETURN_CANCEL

    def notify_start(self):
        """ Clear the general text field when process starts """
        self.text.clear()

    def notify_end(self, msg: str) -> None:
        """ Move cursor to top of output """
        self.output_message("Script complete.")
        self.text.moveCursor(QTextCursor.Start)

    def output_message(self, msg: str, override=None, mode: str = 'stdout') -> None:
        """ output_message will output the current state to the text in output tab

        It can either output to a plain or regular text edit box
        If you sent 'stdout' it will print to the console instead.
        """
        use = self.use if override is None else override
        if use == 'plain':
            self.text.insertPlainText(msg)
        elif use == 'text':
            self.text.appendPlainText(msg)
        elif use == 'html':
            self.text.appendHtml(msg)
        elif use == 'stdout':
            print(f"Script: {msg}")

    def set_output(self, output_dest='stdout'):
        """Set where output will occur

        Args:
            output_dest (str, optional): Where to output strings. Defaults to stdout.
        """
        self.use = 'stdout'
        if output_dest in ['plain',  'text', 'none']:
            self.use = output_dest

    def create_output_fields(self) -> bool:
        """ Initialise all of the output fields for the dialog"""
        self.titler = DialogSettings()
        plain_font = QFont()
        plain_font.setFixedPitch(True)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(plain_font)

        self.btn_box = QDialogButtonBox()
        self.btn_box.addButton(QDialogButtonBox.Close)

        self._dialog_layout = QVBoxLayout()
        self._dialog_layout.addWidget(self.text)
        self._dialog_layout.addWidget(
            self.titler.generate(self.script_parms, self.btn_box))

        return True

    def _create_output_dialog(self) -> QDialog:
        """ Create a runtime dialog """
        dlg_run = QDialog()
        dlg_run.setLayout(self._dialog_layout)
        dlg_run.setMinimumHeight(500)
        dlg_run.setMinimumWidth(500)
        dlg_run.resize(self.dlg_w, self.dlg_h)
        self.titler.set(self.script_parms, dlg_run)
        self.text.clear()
        return dlg_run

    def run(self, msg: str = "Hit Execute button to run program") -> bool:
        """
        run is the interface between the dialog box displaying information and the
        actual process that will be executed.

        It returns True to continue, False to Cancel
        """
        del msg
        def button_clicked(button):
            del button
            self.status = ProgramConstants.RETURN_CONTINUE
            dlg_run.accept()

        self.btn_box.clicked.connect(button_clicked)
        if self.status == ProgramConstants.RETURN_CONTINUE:
            dlg_run = self._create_output_dialog()
            self.start_process()

            dlg_run.exec()

        return self.status

    def set_size(self, w: int, h: int) -> None:
        """ Set dialog dimensions"""
        self.dlg_w = w
        self.dlg_h = h


class RunSilentRunDeep(UiRunSimpleNote):
    """ Run a script with no output box UNLESS we have an error occur """

    def __init__(self, script: str,
                 script_vars: list = None,
                 env:dict=None,
                 is_file=True,
                 output_dest='text'):
        super().__init__(script, script_vars,
                         env=env, is_file=is_file,
                         output_dest=output_dest)
        self.text.hide()

    def output_message(self, msg: str, override=None, mode: str = 'stdout') -> None:
        super().output_message(msg, override, mode)
        if mode == 'stderr':
            self.text.show()

    def run(self, msg: str = "Hit Execute button to run program") -> bool:
        """
        run is the interface between the dialog box displaying information and the
        actual process that will be executed.

        It returns True to continue, False to Cancel
        """
        del msg
        def button_clicked(button):
            del button
            self.status = ProgramConstants.RETURN_CONTINUE
            dlg_run.accept()

        self.btn_box.clicked.connect(button_clicked)

        if self.status == ProgramConstants.RETURN_CONTINUE:
            dlg_run = self._create_output_dialog()
            self.start_process()
            time.sleep(3)
            self.wait_for_process()
            if not self.text.isHidden():
                dlg_run.exec()
            else:
                dlg_run = None

        return self.status
