
class PageDisplayMixin:
    """
        The mixin holds values that are used to control the page displays.

        This does not perform displays but acts more like a class or container."""
    PAGE_NONE = 0
    START_OF_BOOK = 0

    def __init__(self, *args, **kwargs):
        self.setPageNumber( PageDisplayMixin.PAGE_NONE )
        self._is_clear = True
        super().__init__(*args, **kwargs)

    def pageid(self)->str:
        """ Try and get the object name from the main class"""
        try:
            return self.identity()
        except:
            return '(no id)'
        
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
