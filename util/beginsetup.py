
import os
import time
from PySide6.QtWidgets import QDialog, QTextEdit , QVBoxLayout, QApplication, QDialogButtonBox,QMessageBox
from qdb.setup  import Setup
from qdb.dbconn import DbConn


class Initialise( QDialog ):

    def __init__(self, ):
        super().__init__()
        self.create_output()

    def exec(self)->int:
        self.output("<b>Checking components</b>")
        self.init_database( self.dbloc)
        # self.init_help(self.helpdir )
        self.btnbox.setHidden(False)
        return super().exec()

    def run(self, dblocation:str):
        self.dbloc = dblocation
        #self.helpdir = helpdir
        self.show()
        self.exec()
    
    def create_output(self)->None:
        self.layout = QVBoxLayout()
        self.setWindowTitle( "Setup Sheetmusic")
        #windowsize = self.sreen().availableGeometry()
        self.resize( 500,300)
        
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        self.layout.addWidget( self.status )

        self.btnbox = QDialogButtonBox(QDialogButtonBox.Close )
        self.btnbox.clicked.connect( self.accept )
        self.btnbox.setHidden(True)
        self.layout.addWidget( self.btnbox)
        self.setLayout( self.layout )

    def destroy_output(self):
        self.output("\n<b>Setup complete</b>")
        time.sleep( 5 )
        self.close()
        self.accept()

    def output( self, newOutput:str , end=None)->None:
        newOutput = newOutput.replace('\t', '&nbsp;'*5).replace('\n', '<br/>')
        if end is None:
            self.status.insertHtml( newOutput + "<br/>")
        else:
            self.status.insertHtml( newOutput + end.replace(" ", "&nbsp;"))
        QApplication.processEvents()

    def init_database(self, dblocation:str):
        self.output("\n<b>Setup database</b>")
        if not os.path.isdir( dblocation ):
            DbConn.openDB( dblocation ) 
            self.output("Checking database at {}".format( dblocation))
            s = Setup( dblocation )
            self.output("&hellip;", end= " ")
        if s.initSystem():
            self.output("System", end="&hellip;")
        if s.updateSystem():
            self.output("Update", end="&hellip;")
        if s.initGenre():
            self.output("Genre", end= "&hellip;")
        if s.initComposer():
            self.output("Composer", end="&hellip;")
        self.output("Done.")

    # def init_help(self, helpdir ):
    #     help_index = os.path.join( helpdir , DbKeys.VALUE_SHEETMUSIC_INDEX) 
    #     self.output("<b>Setup help</b>")
    #     try:
    #         import requests
    #     except:
    #         QMessageBox.critical(None,
    #         "Python package not found","Install requests package:\npython -m pip install requests", QMessageBox.Ok)
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
        