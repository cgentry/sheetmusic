from PySide6.QtCore import QSizeF, QSize
from PySide6.QtPdf import QPdfDocument
from dataclasses import dataclass


@dataclass
class PdfDimensions:
    widthPortrait: float = 0.0
    widthLandscape: float = 0.0
    heightPortrait: float = 0.0
    heightLandscape: float = 0.0
    _dimensionsSet : bool = False


    def isPortrait(self, dimensions: QSizeF) -> bool:
        return dimensions.width() < dimensions.height()

    def checkSizeDocument( self, document: QPdfDocument ):
        """ Scan the entire document and find maximum sizes """
        self.widthLandscape = 0.0
        self.widthPortrait = 0.0
        self.heightLandscape = 0.0
        self.heightPortrait = 0.0
        self.isSet = False
        for page in range( document.pageCount() ):
            self.checkSizePage( document , page )

    @property
    def isSet(self)->bool:
        return self._dimensionsSet
    
    @isSet.setter
    def isSet( self, flag:bool):
        self._dimensionsSet = flag 
        
    def checkSizePage(self, document: QPdfDocument, page: int):
        """ Check one page against current accumulated pages """
        self.checkSize(document.pagePointSize(page))

    def checkSize(self, dimensions: QSizeF):
        """ Process the document's page size """
        w = dimensions.width()
        h = dimensions.height()
        if self.isPortrait(dimensions):
            self.widthPortrait = max(self.widthPortrait, w)
            self.heightPortrait = max(self.heightPortrait, h)
        else:
            self.widthLandscape = max(self.widthLandscape, w)
            self.heightLandscape = max(self.heightLandscape, h)
        self.isSet = True

    def equalisePage(self, document: QPdfDocument, page: int) -> QSize:
        """ Equalise one page of a document """
        if not self.isSet :
            self.checkSizeDocument( document )
        return self.equalise( document.pagePointSize(page) )

    def equalise(self, dimensions: QSizeF) -> QSize:
        """ Return a size that matches the maximum value for the document """
        if not self.isSet :
            return QSize( dimensions.width(), dimensions.height() )
        if self.isPortrait(dimensions):
            return QSize(self.widthPortrait, self.heightPortrait)
        return QSize(self.widthLandscape, self.heightLandscape)
