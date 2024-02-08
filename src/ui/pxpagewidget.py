"""
User Interface : Module holds Validator, Properties and Property settings
    UI interfaces

 NOTE: There is some weird stuff with 3 pages. C++ deletes PxPageWidgets
 even when the references are just fine. There are some sloppy fixes to
 get around this. Sorry. I'll continue to try and change this.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.
"""

from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QLabel
from qdb.log import DbLog
from ui.label import LabelWidget
from ui.mixin.pagedisplay import PageDisplayMixin
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget

class PxPageWidget( PageDisplayMixin , ISheetMusicDisplayWidget):

    """ PxPageWidget is the simple page handler routines for creating a QLabel and
        populating it with images. It handles aspect ratio and helps keep state for
        the PageWidget
    """

    def __init__( self, name:str ):
        PageDisplayMixin.__init__( self, name )
        ISheetMusicDisplayWidget.__init__(self)
        self.logging = DbLog( 'PxPageWidget')
        self._widget =  LabelWidget( name )
        self.set_identity( name )
        self.clear()

    def identity(self)->str:
        return self._identity

    def set_identity(self, name:str)->str:
        """ Set the current identity of the widget"""
        self._identity = name

    def widget(self)->QLabel:
        """Return the wrapped label widget

        Returns:
            QLabel: Pixel map display widget
        """
        return self._widget

    def clear(self) -> None:
        self._widget.clear()
        self.set_clear(True)

    def hide(self )->None:
        return self.widget().hide()

    def is_visible(self)->bool:
        return self.widget().is_visible()

    def resize( self, *args )->None:
        self.widget().resize( *args )

    def show(self)->None:
        return self.widget().show()

    def set_content( self, content: str|QImage|QPixmap )->bool:
        """Set the label to either a pixmap or the contents of a file

        Args:
            content (str | QImage | QPixmap): Image

        Returns:
            bool: True if display widget set
        """
        rtn = self.widget().set_content( content )
        self.set_clear( not rtn )
        return rtn

    def set_content_page(self, content: str|QImage|QPixmap, page_number: int) -> bool:
        """
        Set the image for the label from a filename or a pixal map

        The file must exist or the load will fail. Check before calling
        """
        rtn = self.set_content( content)
        if rtn:
            self.set_pagenum(page_number)
        else:
            self.logging.debug( f'Page {page_number}')
        self.widget().resize()
        return rtn

    def content(self)->QPixmap:
        """ Return the widget's pixel map"""
        return self.widget().pixmap()

    def copy(self, source_object:object)->bool:
        """ Copy the image from one widget to another"""
        self.clear()
        if not source_object.is_clear():
            if self.set_content(source_object.content()):
                self.set_clear(False)
                self.set_pagenum(source_object.page_number())
        return not self.is_clear()
