from PySide6.QtCore import QSize

import abc
class ISheetMusicDisplayWidget( metaclass=abc.ABCMeta):
    """ Interface to define required methods for any low-level display widget 
    """
    def __init__( self, *args, **kwargs ):
        super().__init__( )

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'clear') and callable(subclass.clear) and 
                hasattr(subclass, 'content') and callable(subclass.content) and 
                hasattr(subclass, 'copy') and callable(subclass.copy) and
                hasattr(subclass, 'hide') and callable(subclass.hide) and
                hasattr(subclass, 'isVisible') and callable(subclass.isVisible) and
                hasattr(subclass, 'pageNumber') and callable(subclass.pageNumber) and
                hasattr(subclass, 'resize') and callable(subclass.resize) and
                hasattr(subclass, 'setContent') and callable(subclass.setContent) and
                hasattr(subclass, 'setContentPage') and callable( subclass.setContentPage) and
                hasattr(subclass, 'setKeepAspectRatio') and callable( subclass.setKeepAspectRatio) and 
                hasattr(subclass, 'setPageNumber') and callable(subclass.setPage) and
                hasattr(subclass, 'show') and callable(subclass.show) and
                hasattr(subclass, 'widget') and callable(subclass.widget) or
                NotImplemented)
    
    @abc.abstractmethod
    def clear(self)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def copy(self, source_object:object)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def content(self )->object:
        raise NotImplementedError
    
    @abc.abstractmethod
    def hide(self)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def isVisible(self)->bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    def pageNumber(self )->int:
        raise NotImplementedError
    
    @abc.abstractmethod
    def resize(self, wide:int|QSize  , height:int )->None:
        raise NotImplementedError

    @abc.abstractmethod
    def setContent(self, content:object )->bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    def setContentPage(self, content:object, pageNumber:int)->bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    def setKeepAspectRatio(self, keep:bool)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def setPageNumber(self, page_number:int)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def show(self, flag:bool)->None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def widget(self, flag:bool)->object:
        raise NotImplementedError
