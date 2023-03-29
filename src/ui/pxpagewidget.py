# This Python file uses the following encoding: utf-8
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

# NOTE: There is some weird stuff with 3 pages. C++ deletes PxPageWidgets
# even when the references are just fine. There are some sloppy fixes to
# get around this. Sorry. I'll continue to try and change this.

from PySide6.QtCore import QSize
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
    
    def set_identity(self, id:str)->str:
        self._identity = id

    def widget(self)->QLabel:
        return self._widget
    
    def clear(self) -> None:
        """ Clear the label and set page number to None """
        self.widget().clear()
        self.setClear(True)

    def hide(self )->None:
        return self.widget().hide()

    def isVisible(self)->bool:
        return self.widget().isVisible()

    def resize( self, *args )->None:
        self.widget().resize( *args )
  
    def show(self)->None:
        return self.widget().show()
    
    def setContent( self, newimage: str|QImage|QPixmap )->bool:
        """ Set the label to either a pixmap or the contents of a file"""
        rtn = self.widget().setContent( newimage )
        self.setClear( not rtn )
        return rtn

    def setContentPage(self, newimage: str|QImage|QPixmap, page: int) -> bool:
        """
        Set the image for the label from a filename or a pixal map

        The file must exist or the load will fail. Check before calling
        """
        rtn = self.setContent( newimage)
        if rtn:
            self.setPageNumber(page)
        else:
            self.logging.debug( f'Page {page}')
        self.widget().resize()
        return rtn
 
    def content(self)->QPixmap:
        return self.widget().pixmap()
    
    def copy(self, otherPage:object)->bool:
        """ Copy the image from one widget to another"""
        self.clear()
        if not otherPage.isClear():
            if self.setContent(otherPage.content()):
                self.setClear(False)
                self.setPageNumber(otherPage.pageNumber())
        return not self.isClear()
