import os
import sys
import logging
from   PySide6.QtHelp     import QHelpEngine
from   PySide6.QtWidgets  import QApplication, QMainWindow, QTabWidget, QTextBrowser, QSplitter, QDialog, QVBoxLayout, QDockWidget
from   PySide6.QtCore     import QUrl, Qt


class HelpBrowser(QTextBrowser):
    def __init__(self, helpEngine, parent=None):
        super().__init__(parent)
        self.setStyleSheet( '* { font-family: "Times New Roman", Times, serif; font-size: large; }')
        self.helpEngine = helpEngine

    def loadResource(self, _type, name):
        if name.scheme() == "qthelp":
            return self.helpEngine.fileData(name)
        else:
            return super().loadResource(_type, name)



class UiHelp( QDialog ):
    def __init__(self, mainWindow:QMainWindow, mainExePath ):
        super().__init__(  )
        self.logger = logging.getLogger('UiHelp')
        self.mainWindow = mainWindow
        self.mainExepath =  mainExePath

    def setupHelp( self):
        #print( os.path.join(self.mainExepath, "docs", "sheetmusic.qhc") )
        try:
            self.helpEngine = QHelpEngine(
                os.path.join(self.mainExepath, "docs", "sheetmusic.qhc")
            )
            self.helpEngine.setupData()
        except Exception as err:
            self.logger.exception( "Setting up Help system")
            raise err

        layout = QVBoxLayout()
        tWidget = QTabWidget()
        tWidget.setMaximumWidth(200)
        tWidget.addTab(self.helpEngine.contentWidget(), "Contents")
        tWidget.addTab(self.helpEngine.indexWidget(), "Index")

        textViewer = HelpBrowser(self.helpEngine)
        txt = os.path.join( self.mainExepath, "docs", "index.html")
        textViewer.setSource( QUrl.fromLocalFile( txt ))

        self.helpEngine.setUsesFilterEngine(True)
        self.helpEngine.contentWidget().linkActivated.connect(textViewer.setSource)
        self.helpEngine.indexWidget().linkActivated.connect(textViewer.setSource)

        horizSplitter = QSplitter(Qt.Horizontal)
        horizSplitter.insertWidget(0, tWidget)
        horizSplitter.insertWidget(1, textViewer)
        #horizSplitter.hide()

        self.setWindowTitle( u'Help')
        layout.addWidget( horizSplitter )
        self.resize( 1024,600 )
        self.setLayout( layout )

if "__main__" == __name__ :
    from PySide6.QtWidgets import QApplication
    app = app = QApplication([])
    mainFile = os.path.abspath(sys.modules['__main__'].__file__)
    mainExePath = os.path.dirname( os.path.dirname(mainFile) )
    uihelp = UiHelp( None , mainExePath)
    uihelp.setupHelp()
    uihelp.exec()
