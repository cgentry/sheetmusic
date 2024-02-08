"""
User Interface : Help display

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import os
import sys
import logging

from   PySide6.QtHelp     import QHelpEngine
from   PySide6.QtWidgets  import ( QApplication, QMainWindow, QTabWidget,
                                  QTextBrowser, QSplitter, QDialog, QVBoxLayout )
from   PySide6.QtCore     import QUrl, Qt


class HelpBrowser(QTextBrowser):
    """ Help Browser will set QTextBrowser interface specifications """
    def __init__(self, helpEngine, parent=None):
        super().__init__(parent)
        self.setStyleSheet( '* { font-family: "Times New Roman", Times, serif; font-size: large; }')
        self.help_engine = helpEngine

    def loadResource(self, _type, name):
        if name.scheme() == "qthelp":
            return self.help_engine.fileData(name)

        return super().loadResource(_type, name)



class UiHelp( QDialog ):
    """ Sheetmusic Help interface. Pass in a Qdialog and it will fill in the standard Help system"""
    def __init__(self, main_window:QMainWindow, main_path:str ):
        """Initialise system

        Args:
            main_window (QMainWindow): Main Window
            main_path (str): Path to program
        """
        super().__init__(  )
        self.help_engine = None
        self.logger = logging.getLogger('UiHelp')
        self.main_window = main_window
        self.main_exepath =  main_path

    def setup_help( self):
        """ Setup the interface window and help system """
        try:
            self.help_engine = QHelpEngine(
                os.path.join(self.main_exepath, "docs", "sheetmusic.qhc")
            )
            self.help_engine.setupData()
        except Exception as err:
            self.logger.critical( "Setting up Help system: '%s'" , str(err))
            raise err

        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        tab_widget.setMaximumWidth(200)
        tab_widget.addTab(self.help_engine.contentWidget(), "Contents")
        tab_widget.addTab(self.help_engine.indexWidget(), "Index")

        text_view = HelpBrowser(self.help_engine)
        txt = os.path.join( self.main_exepath, "docs", "index.html")
        text_view.setSource( QUrl.fromLocalFile( txt ))

        self.help_engine.setUsesFilterEngine(True)
        self.help_engine.contentWidget().linkActivated.connect(text_view.setSource)
        self.help_engine.indexWidget().linkActivated.connect(text_view.setSource)

        horiz_splitter = QSplitter(Qt.Horizontal)
        horiz_splitter.insertWidget(0, tab_widget)
        horiz_splitter.insertWidget(1, text_view)
        #horizSplitter.hide()

        self.setWindowTitle( 'Help')
        layout.addWidget( horiz_splitter )
        self.resize( 1024,600 )
        self.setLayout( layout )

if "__main__" == __name__ :
    app = QApplication([])
    main_file = os.path.abspath(sys.modules['__main__'].__file__)
    main_exepath = os.path.dirname( os.path.dirname(main_file) )
    uihelp = UiHelp( None , main_exepath)
    uihelp.setup_help()
    uihelp.exec()
