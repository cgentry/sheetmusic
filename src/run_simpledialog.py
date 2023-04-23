from ui.simpledialog import SimpleDialog
from PySide6.QtWidgets  import ( QApplication )
import sys

if __name__ == "__main__":
    app = QApplication([])
                        
    test = [ "type='file'   label='Pick a good file '         option='include'" ,
             "type='file'   label='pick a PDF file'           option='include'     filter='(*.pdf *.PDF)'",
             "type='dir'    label='Enter directory here '     option=' include'",
             "type='text'   label='Enter a single line here'  include'req'         value='$DBFILE'   tag='DBFILE'",
             "type='text'   label='Music dir is:'             option='ro include'  value='$MUSIC'    tag='MUSIC'",
             "type='drop'   label='Select one:'               option='' dropdown='alpha;beta;delta'  value='delta'",
             "type='drop'   label='Names:'                    split='%' dropdown='USA%Mexico%Canada#data' data='U % M % C'",
             "type='check'  label='Say yes to michigan!'      option='' value='yes'",
             "type='button' label='Go away'                   value='reject'",
    ]

    replace= { 
            'DBFILE':'/db/file/name' , 
            'MUSIC': '/it/is/here'}
    tclass = SimpleDialog()
    #try:
    if True:
        tclass.parse( test )
        tclass.setKeywords( replace )
        if tclass.exec():
            for row in tclass.data: 
                print( row )
    
    #except Exception as err:
    #    print( "Nope!", str(err))

    # converter = UiConvertPDFDocuments()
    # converter.exec_()
    app.quit()
    sys.exit(0)
