
class PageDisplayMixin:
    """
        The mixin holds values that are used to control the page displays.

        This does not perform displays but acts more like a class or container."""
    PAGE_NONE = 0
    START_OF_BOOK = 0

    def __init__(self, *args, **kwargs):
        self.setPageNumber()
        self._is_clear = True
        super().__init__(*args, **kwargs)

    def pageid(self)->str:
        """ Try and get the object name from the main class"""
        try:
            return self.identity()
        except:
            return '(no id)'
        
    def setPageNumber(self, pgNumber: int = PAGE_NONE) -> None:
        self._pageNumber = pgNumber

    def pageNumber(self) -> int:
        return self._pageNumber if self._pageNumber is not None else self.START_OF_BOOK

    def setKeepAspectRatio(self, keep_ratio: bool) -> None:
        self._keep_aspect_ratio = keep_ratio

    def keepAspectRatio(self) -> bool:
        if hasattr( self , '_keep_aspect_ratio'):
            return self._keep_aspect_ratio
        return True

    def setClear(self, is_clear: bool) -> None:
        self._is_clear = is_clear

    def isClear(self) -> bool:
        """ Return the status of the page """
        return self._is_clear
