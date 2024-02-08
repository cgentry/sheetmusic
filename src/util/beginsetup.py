"""
Utility: Initialise the system

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import os
import time
from PySide6.QtWidgets import (
            QDialog, QTextEdit ,
            QVBoxLayout, QApplication,
            QDialogButtonBox )
from qdb.setup  import Setup
from qdb.dbconn import DbConn


class Initialise( QDialog ):
    """Interface with the user to initialise the system

    Args:
        QDialog (QT Object): Standard dialog
    """
    def __init__(self, ):
        super().__init__()
        self.dbloc = None
        self.create_output()

    def exec(self)->int:
        """ initialise the database and execute system

        Returns:
            int: _description_
        """
        self.output("<b>Checking components</b>")
        self._init_database( self.dbloc)
        # self.init_help(self.helpdir )
        self.btnbox.setHidden(False)
        return super().exec()

    def run(self, dblocation:str):
        """Save database location and show dialog

        Args:
            dblocation (str): Database location
        """
        self.dbloc = dblocation
        #self.helpdir = helpdir
        self.show()
        self.exec()

    def create_output(self)->None:
        """Create the output layout and contents
        """
        self._dialog_layout = QVBoxLayout()
        self.setWindowTitle( "Setup Sheetmusic")
        #windowsize = self.sreen().availableGeometry()
        self.resize( 500,300)

        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self._dialog_layout.addWidget( self.status )

        self.btnbox = QDialogButtonBox(QDialogButtonBox.Close )
        self.btnbox.clicked.connect( self.accept )
        self.btnbox.setHidden(True)
        self._dialog_layout.addWidget( self.btnbox)
        self.setLayout( self._dialog_layout )

    def destroy_output(self):
        """Output a message and close dialog
        """
        self.output("\n<b>Setup complete</b>")
        time.sleep( 5 )
        self.close()
        self.accept()

    def output( self, outstr:str , end:str=None)->None:
        """Add a string to the output

        Args:
            outstr (str): String to add to output
            end (str, optional): end output.
                HTML, blanks replaced with break
                Defaults to None.
        """
        outstr = outstr.replace('\t', '&nbsp;'*5).replace('\n', '<br/>')
        if end is None:
            self.status.insertHtml( outstr + "<br/>")
        else:
            self.status.insertHtml( outstr + end.replace(" ", "&nbsp;"))
        QApplication.processEvents()

    def _init_database(self, dblocation:str):
        """Initialise the database

        Args:
            dblocation (str): Database location
        """
        self.output("\n<b>Setup library (database)</b>")
        if not os.path.isdir( dblocation ):
            DbConn.open_db( dblocation )
            self.output(f"Checking library at {dblocation}".format( dblocation))
            s = Setup( dblocation )
            self.output("&hellip;", end= " ")
        if s.init_system():
            self.output("System", end="&hellip;")
        if s.system_update():
            self.output("Update", end="&hellip;")
        if s.init_genre():
            self.output("Genre", end= "&hellip;")
        if s.init_composer():
            self.output("Composer", end="&hellip;")
        self.output("Done.")

    # def init_help(self, helpdir ):
    #     help_index = os.path.join( helpdir , DbKeys.VALUE_SHEETMUSIC_INDEX)
    #     self.output("<b>Setup help</b>")
    #     try:
    #         import requests
    #     except:
    #         QMessageBox.critical(None,
    #         "Python package not found",
    #         "Install requests package:\npython -m pip install requests",
    #         QMessageBox.Ok)
    #         self.output("Help system cannot be download. Install python 'requests' package.")
    #         return
    #     if not os.path.isdir( helpdir ) :
    #         if not os.path.isdir( helpdir ):
    #             os.mkdir( helpdir )
    #             self.output("Created help directory {}".format( helpdir ))

    #     if not os.path.isfile( help_index ):
    #         from util.help import UiHelp
    #         helper = UiHelp()
    #         self.output("Loading dictionary from repository", end='&hellip;<br/>')
    #         self.output( '\t' + helper.LoadDictionary( helpdir, DbKeys.VALUE_SHEETMUSIC_INDEX ))
    #         self.output("Loading help contents", end='&hellip;<br/>')
    #         self.output( "\t" + helper.LoadHelpFiles( helpdir ))
    #         time.sleep(1)
