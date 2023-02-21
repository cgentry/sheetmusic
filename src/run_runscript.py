from ui.runscript       import UiRunScript, UiRunScriptFile, UiScriptSetting, UiRunSimpleNote
from qdil.preferences   import SystemPreferences
from qdb.dbconn         import DbConn
from PySide6.QtWidgets  import QApplication
import os, sys
from util.toollist      import GenerateToolList


if "__main__" == __name__ :

    sy = SystemPreferences()
    dbLocation    = sy.getPathDB()          # Fetch the system settings
    mainDirectory = sy.getDirectory()       # Get direcotry
    DbConn.openDB( dbLocation )

    app = QApplication([])

    mainFile = os.path.abspath(sys.modules['__main__'].__file__)
    mainExePath = os.path.dirname( os.path.dirname(mainFile) )
  
    script="""#!/bin/bash
    #:title This is just a test and doesn't do anything
    #:comment line 1
    #:comment line 2
    #:comment
    #:comment Do you want to run?
    #:file-prompt Select a file!
    #:file-filter (*.pdf *.PDF)
    #:dir-prompt Enter target directory
    #:require file dir
    #:system dbfile version music
    #: width 1024
    #: heigth 920
    cd /tmp
    ls -la
    #:include another.sh
    """
    # gen = GenerateToolList()
    # listid =  gen.list()
    # for key in listid :
    #     print("Script: {}\n\tpath: {}\nRequires: {}\nComment: {}\n".format( key , listid[key]['path'], listid[key]['require'],listid[key]['comment'] ))
    # tmod = UiScriptSetting( filename='dummy', lines=script.splitlines() )
    # print( tmod.settings())

    # script_file="/Users/Charles/python/sheet_music/SheetMusic/src/util/scripts/scriptinfo.sh"
    script_file="/Users/Charles/python/sheet_music/SheetMusic/src/util/scripts/fixpdf.sh"
    tmod = UiRunScriptFile( script_file, [], isFile=True)

    tmod.run()


    #   sys.exit( app.exec() )
