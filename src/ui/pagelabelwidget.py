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

# NOTE: There is some weird stuff with 3 pages. C++ deletes PageLabelWidgets
# even when the references are just fine. There are some sloppy fixes to
# get around this. Sorry. I'll continue to try and change this.

from PySide6.QtCore import QSize
from PySide6.QtGui import (QPixmap, Qt, QImage )
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy )
from ui.mixin.pagedisplay import PageDisplayMixin
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget

class PageLabelWidget( PageDisplayMixin , ISheetMusicDisplayWidget):

    """ PageLabelWidget is the simple page handler routines for creating a QLabel and 
        populating it with images. It handles aspect ratio and helps keep state for 
        the PageWidget
    """

    def __init__( self, name:str ):
        super( PageDisplayMixin, self).__init__( )
        super( ISheetMusicDisplayWidget, self).__init__()
        self._widget =  QLabel()
        self._widget.setMargin(5)
        self._widget.setAlignment(Qt.AlignCenter)
        self._widget.setStyleSheet("")
        #self._widget.setStyleSheet("background: #236dc9;" )
        self._widget.setSizePolicy( self._size_policy())
        self._widget.setObjectName( name )
        
        self.clear()

    def _size_policy(self)->QSizePolicy:
        qp = QSizePolicy()
        qp.setHorizontalStretch(1)
        qp.setVerticalStretch(1)
        return qp

    def identity(self)->str:
        name = self._widget.objectName()
        if name == '':
            return '(page-label-widget)'
        return name
    
    def widget(self)->QLabel:
        return self._widget
    
    def clear(self) -> None:
        """ Clear the label and set page number to None """
        self.widget().clear()
        self.setClear(True)
        self.setPageNumber(self.PAGE_NONE)

    def hide(self )->None:
        return self.widget().hide()

    def isVisible(self)->bool:
        return self.widget().isVisible()

    def resize( self, width:int|QSize, height:int=0)->None:
        if isinstance( width, QSize ):
            self.widget().resize( width )
        else:
            if height > 0 :
                self.widget().resize( width , height )
  
    def show(self)->None:
        return self.widget().show()
    
    def _set_label_from_pixmap(self, px: QPixmap) -> bool:
        if px is None or px is False or px.isNull() or not isinstance(px, QPixmap):
            return False
        self.widget().setPixmap( px ) 
        return True
    

    def _set_label_from_image(self, qimage: QImage) -> bool:
        """ Set the label to the pixmap passed
        
            NOTE: On high pixel monitors it will take into account the density in order
            to provide a sharper display ('ratio'). Otherwise the display is rather blurry
        """
        self.clear()
        if qimage is None or qimage is False or qimage.isNull() or not isinstance(qimage, QImage):
            return False
        ratio = QApplication.primaryScreen().devicePixelRatio()
        qimage.setDevicePixelRatio( ratio )
        size  = self.widget().size()
        if self.keepAspectRatio():
            qimage = qimage.scaled(int(size.width()*ratio), 
                                   int(size.height()*ratio) , 
                                   aspectMode=Qt.KeepAspectRatio , 
                                   mode=Qt.SmoothTransformation) 
        else:
            qimage = qimage.scaled( int( size.width()*ratio), int(size.height()*ratio) )
        self._set_label_from_pixmap( QPixmap.fromImage(qimage) ) 
        return True
    
    
    def _set_label_from_file( self, file_name:str  )->bool:
        """ Load the image from a file and call pixmap display routine"""
        qimage = QImage()
        qimage.load( file_name )
        return self._set_label_from_image( qimage )
    
    def setContent( self, newimage: str|QImage|QPixmap )->bool:
        """ Set the label to either a pixmap or the contents of a file"""
        rtn = False
        if isinstance(newimage, QImage):
            rtn= self._set_label_from_image(newimage )
        if isinstance(newimage, QPixmap):
            rtn= self._set_label_from_pixmap(newimage )
        if isinstance(newimage, str):
            rtn= self._set_label_from_file( newimage  )
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
        return rtn
 
    def content(self)->QPixmap:
        return self.widget().pixmap()
    
    def copy(self, otherPage:object)->bool:
        """ Copy the image from one widget to another"""
        self.clear()
        if not otherPage.isClear():
            self.setContent(otherPage.content())
            self.setClear(False)
            self.setPageNumber(otherPage.pageNumber())
        return not self.isClear()
