# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file is part of Sheetmusic.

# Sheetmusic is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PySide6.QtCore import QSizeF, QSize
from PySide6.QtPdf import QPdfDocument
from dataclasses import dataclass


@dataclass
class PdfDimensions:
    """ PdfDimensions stores and computes dimensions for PDF Pages"""
    widthPortrait: float = 0.0
    widthLandscape: float = 0.0
    heightPortrait: float = 0.0
    heightLandscape: float = 0.0
    _dimensionsSet : bool = False


    def isPortrait(self, dimensions: QSizeF) -> bool:
        """ Return True if width < height (portrait) """
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
        """ Have dimensions bet set? """
        return self._dimensionsSet
    
    @isSet.setter
    def isSet( self, flag:bool):
        """ Set the dimension flag """
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

    def equalisePage(self, document: QPdfDocument, page: int, offset:int=1) -> QSize:
        """ Equalise one page of a document 
            Offset is 1 if we use numbering 1->n
        """
        if not self.isSet :
            self.checkSizeDocument( document )
        return self.equalise( document.pagePointSize(page-offset) )

    def equalise(self, dimensions: QSizeF) -> QSize:
        """ Return a size that matches the maximum value for the document """
        if not self.isSet :
            return QSize( dimensions.width(), dimensions.height() )
        if self.isPortrait(dimensions):
                return QSize(self.widthPortrait, self.heightPortrait)
        return QSize(self.widthLandscape, self.heightLandscape)
    
