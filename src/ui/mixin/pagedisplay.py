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


from util.pdfclass import PdfDimensions

class PageDisplayMixin:
    """
        The mixin holds values that are used to control the page displays.

        This does not perform displays but acts more like a class or container."""
    PAGE_NONE = 0
    START_OF_BOOK = 0

    def __init__(self, name:str , dimension:PdfDimensions = None):
        self._identity = name
        self._pageNumber =  PageDisplayMixin.PAGE_NONE 
        self._is_clear = True
        self._dimensions = dimension

    def identity(self)->str:
        return self._identity 
    
    def set_identity(self, id:str)->str:
        self._identity = id

    def setPageNumber(self, pgNumber: int = 0) -> None:
        self._pageNumber = pgNumber

    def pageNumber(self) -> int:
        return self._pageNumber if self.isPage() else PageDisplayMixin.START_OF_BOOK
    
    def isPage(self)->bool:
        """ Return True if page number has been set """
        return ( self._pageNumber is not None and self._pageNumber != PageDisplayMixin.PAGE_NONE )

    def setKeepAspectRatio(self, keep_ratio: bool) -> None:
        self._keep_aspect_ratio = keep_ratio

    def keepAspectRatio(self) -> bool:
        if hasattr( self , '_keep_aspect_ratio'):
            return self._keep_aspect_ratio
        return True

    def setClear(self, is_clear: bool) -> bool:
        """ Indicate no page or document is set """
        self._is_clear = is_clear
        self._pageNumber = PageDisplayMixin.PAGE_NONE
        return is_clear

    def isClear(self) -> bool:
        """ Return the status of the page """
        return self._is_clear
    
    @property
    def dimensions( self )->PdfDimensions:
        """ Return the PdfDimension class """
        if self._dimensions is None:
            self._dimensions = PdfDimensions()
        return self._dimensions 
    
    @dimensions.setter
    def dimensions( self, pdf_dimensions:PdfDimensions):
        if pdf_dimensions:
            self._dimensions = pdf_dimensions

