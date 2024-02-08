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

NOTE: There is some weird stuff with 3 pages. C++ deletes PxPageWidgets
even when the references are just fine. There are some sloppy fixes to
get around this. Sorry. I'll continue to try and change this.
"""

from PySide6.QtWidgets import ( QMainWindow)
from ui.pxpagewidget import PxPageWidget
from ui.bottomsheet import BottomSheet

class PxWidget( BottomSheet):
    """ PageWidget will construct and handle multi-page layouts.
        It handles all the construction, layout, and page flipping
        functions.
    """

    def __init__(self, main_window: QMainWindow):
        super().__init__( main_window , 'PxWidget')

    def content_generator( self , obj_name:str )->PxPageWidget:
        return PxPageWidget( obj_name)
