""" General User Interface widget """
from PySide6.QtWidgets import (QMessageBox )

class QBox( QMessageBox ):
    """ Create a Message box to display on screen center"""
    def __init__(self):
        super().__init__()
        self.padding()
        self._info = ''
        self._text = ''


    def _set_textfields(self ):
        """ Resize based upon what text is the largest size"""
        flen = (max(len(self._text), len( self._info ) )  * \
                    self.fontMetrics().averageCharWidth() ) + self._padding
        fmt = f'{{0:{flen}s}}'
        super().setText( fmt.format( self._text ))
        super().setInformativeText( fmt.format( self._info ))

    def setText( self, text:str):
        """ Set text field (prompt)"""
        self._text = text

    def setInformativeText(self, text: str) -> None:
        self._info = text

    def padding(self, size:int=0):
        """ Set padding for text """
        self._padding = size

    def exec(self)->int:
        """ Set the text fields and exec the message box"""
        self._set_textfields()
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
