"""
 Class Interface Definition : Display widget

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

 Note: A lot of pylint warnings have been shutoff for this
 Its an interface, but
"""
import abc
from PySide6.QtCore import QSize

class ISheetMusicDisplayWidget( metaclass=abc.ABCMeta):
    """ Interface to define required methods for any low-level display widget
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        """Determine if a sublass

        Args:
            subclass (object):  subclass to check

        Returns:
            bool: True or false
        """
        return (hasattr(subclass, 'clear') and
                callable(subclass.clear) and
                hasattr(subclass, 'content') and
                callable(subclass.content) and
                hasattr(subclass, 'copy') and
                callable(subclass.copy) and
                hasattr(subclass, 'hide') and
                callable(subclass.hide) and
                hasattr(subclass, 'is_visible') and
                callable(subclass.is_visible) and
                hasattr(subclass, 'page_number') and
                callable(subclass.page_number) and
                hasattr(subclass, 'resize') and
                callable(subclass.resize) and
                hasattr(subclass, 'setContent') and
                callable(subclass.setContent) and
                hasattr(subclass, 'set_content_page') and
                callable( subclass.set_content_page) and
                hasattr(subclass, 'keep_aspect_ratio') and
                callable( subclass.keep_aspect_ratio) and
                hasattr(subclass, 'set_pagenum') and
                callable(subclass.setPage) and
                hasattr(subclass, 'show') and
                callable(subclass.show) and
                hasattr(subclass, 'widget') and
                callable(subclass.widget) or
                NotImplemented)

    @abc.abstractmethod
    def clear(self)->None:
        """ Clear the current dispaly widget """
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self, source_object:object)->bool:
        """ Copy content and values from source"""
        raise NotImplementedError

    @abc.abstractmethod
    def content(self )->object:
        """ Return the widget contents """
        raise NotImplementedError

    @abc.abstractmethod
    def hide(self)->None:
        """ Hide the current widget """
        raise NotImplementedError

    @abc.abstractmethod
    def is_visible(self)->bool:
        """ Return true if widget is displayed """
        raise NotImplementedError

    @abc.abstractmethod
    def page_number(self )->int:
        """ return current page number """
        raise NotImplementedError

    @abc.abstractmethod
    def resize(self, wide:int|QSize  , height:int )->None:
        """ Change the current widgets display """
        raise NotImplementedError

    @abc.abstractmethod
    def set_content(self, content:object )->bool:
        """ Set the widget's content """
        raise NotImplementedError

    @abc.abstractmethod
    def set_content_page(self, content:object, page_number:int)->bool:
        """ Set this page's content to 'content' """
        raise NotImplementedError

    @abc.abstractmethod
    def keep_aspect_ratio(self, keep:bool)->None:
        """Maintain aspect ratio

        Args:
            keep (bool):
            True to keep original aspect ratio

        Raises:
            NotImplementedError:
                Abstract method must be implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_pagenum(self, page_number:int)->bool:
        """Set the current page number

        Args:
            page_number (int): page to go to

        Raises:
            NotImplementedError:
                Abstract method must be implemented

        Returns:
            bool: True if changed page
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show(self)->None:
        """ Display widget contents """
        raise NotImplementedError

    @abc.abstractmethod
    def widget(self)->object:
        """ Return the wrapped widget """
        raise NotImplementedError
