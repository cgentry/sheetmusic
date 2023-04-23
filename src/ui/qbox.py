from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMessageBox )

class QBox( QMessageBox ):
    def __init__(self):
        super().__init__()
        self.padding()
        self._info = ''
        self._text = ''


    def _setTextFields(self ):
        print("Fields:\n{}\n{}\n".format( self._text, self._info ))
        """ Resize based upon what text is the largest size"""
        flen = ''
        flen = (max(len(self._text), len( self._info ) )  * self.fontMetrics().averageCharWidth() ) + self._padding
        fmt = f'{{0:{flen}s}}'
        super().setText( fmt.format( self._text ))
        super().setInformativeText( fmt.format( self._info ))
        return 
        
    def setText( self, text:str):
        self._text = text

    def setInformativeText(self, text: str) -> None:
        self._info = text

    def padding(self, size:int=0):
        self._padding = size

    def exec(self)->int:
        self._setTextFields()
        return super().exec()
    
    
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication()
    window = QBox( )
    print('set text')
    window.setText('informative example text for an example of something long       .')
    print('set info')
    window.setInformativeText('small')
    print('exec')
    rtn = window.exec()
    
    print( "....rtn is", rtn )
    sys.exit(0)