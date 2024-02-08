"""
User Interface , mixin: Page display common routines

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from util.pdfclass import PdfDimensions

class PageDisplayMixin:
    """
        The mixin holds values that are used to control the page displays.

        This does not perform displays but acts more like a class or container.
    """
    PAGE_NONE = 0
    START_OF_BOOK = 0

    def __init__(self, name:str , dimension:PdfDimensions = None):
        self._identity = name
        self._page_number =  PageDisplayMixin.PAGE_NONE
        self._is_clear = True
        self._dimensions = dimension

    def identity(self)->str:
        """ Return the page identity"""
        return self._identity

    def set_identity(self, name:str)->str:
        """ set the identity of this page """
        self._identity = name

    def set_pagenum(self, page_number: int) -> bool:
        """ Set the page number to display """
        self._page_number = page_number
        return True

    def page_number(self) -> int:
        """ Either return the current page number or
        return the start of book"""
        return self._page_number if self.ispage() else PageDisplayMixin.START_OF_BOOK

    def ispage(self)->bool:
        """ Return True if page number has been set """
        return ( self._page_number is not None and self._page_number != PageDisplayMixin.PAGE_NONE )

    @property
    def keep_aspect_ratio(self) -> bool:
        """ Return if this page's aspect ratio flag is set
            if not, return true """
        if hasattr( self , '_keep_aspect_ratio'):
            return self._keep_aspect_ratio
        return True

    @keep_aspect_ratio.setter
    def keep_aspect_ratio(self, keep_ratio: bool) -> None:
        self._keep_aspect_ratio = keep_ratio

    def set_clear(self, is_clear: bool) -> bool:
        """ Indicate no page or document is set """
        self._is_clear = is_clear
        self._page_number = PageDisplayMixin.PAGE_NONE
        return is_clear

    def is_clear(self) -> bool:
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
        """ Set the dimensions for the PDF """
        if pdf_dimensions:
            self._dimensions = pdf_dimensions
