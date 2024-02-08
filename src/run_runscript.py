""" Simple program that for running scriptfiles.

Not meant for general usage, but more for testing

"""
import os
import sys
from PySide6.QtWidgets  import QApplication


from ui.runscript       import UiRunScriptFile
from qdil.preferences   import SystemPreferences
from qdb.dbconn         import DbConn


if "__main__" == __name__ :

    syspref = SystemPreferences()
    dbLocation    = syspref.dbpath
    mainDirectory = syspref.dbdirectory
    DbConn.open_db( dbLocation )

    app = QApplication([])

    mainFile = os.path.abspath(sys.modules['__main__'].__file__)
    mainExePath = os.path.dirname( os.path.dirname(mainFile) )

    SCRIPT="""#!/bin/bash
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
    #     print("Script: {}\n\tpath: {}\nRequires: {}\nComment: {}\n".format(
    # key , listid[key]['path'], listid[key]['require'],listid[key]['comment'] ))
    # tmod = UiScriptSetting( filename='dummy', lines=script.splitlines() )
    # print( tmod.settings())

    # script_file="/Users/Charles/python/sheet_music/SheetMusic/src/util/scripts/scriptinfo.sh"
    SCRIPT_FILE="/Users/Charles/python/sheet_music/SheetMusic/src/util/scripts/fixpdf.sh"
    tmod = UiRunScriptFile( SCRIPT_FILE, [], is_file=True)

    tmod.run()


    #   sys.exit( app.exec() )
