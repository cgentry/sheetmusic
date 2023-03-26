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


from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy

from ui.mixin.pagedisplay import PageDisplayMixin

class LabelWidget( PageDisplayMixin, QLabel ):
    def __init__(self, name:str=None):
        super().__init__()
        self._setup_widget(name)

    def _size_policy(self)->QSizePolicy:
        qp = QSizePolicy()
        qp.setHorizontalStretch(1)
        qp.setVerticalStretch(1)
        return qp
    
    def _setup_widget(self, name:str=None):
        if name is not None:
            self.setObjectName( name )
    
        self.setMargin(5)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("")
        #self.setStyleSheet("background: #236dc9;" )
        self.setSizePolicy( self._size_policy())
        self._ratio = QApplication.primaryScreen().devicePixelRatio()

    def _set_from_pixmap(self, px: QPixmap) -> bool:
        if px is None or px is False or px.isNull() or not isinstance(px, QPixmap):
            return False
        self.setPixmap( px ) 
        return True
    
    def _set_from_file( self, file_name:str  )->bool:
        """ Load the image from a file and call pixmap display routine"""
        qimage = QImage()
        qimage.load( file_name )
        return self._set_from_image( qimage )
    
    def _set_from_image(self, qimage: QImage) -> bool:
        """ Set the label to the pixmap passed
        
            NOTE: On high pixel monitors it will take into account the density in order
            to provide a sharper display ('ratio'). Otherwise the display is rather blurry
        """
        self.clear()
        if qimage is None or qimage is False or qimage.isNull() or not isinstance(qimage, QImage):
            return False
        qimage.setDevicePixelRatio( self._ratio )
        size  = self.size().__mul__( self._ratio )
        if self.keepAspectRatio():
            qimage = qimage.scaled(size , 
                                   aspectMode=Qt.KeepAspectRatio , 
                                   mode=Qt.SmoothTransformation) 
        else:
            qimage = qimage.scaled( size )
        self._set_from_pixmap( QPixmap.fromImage(qimage) ) 
        return True
    
    def setContent( self, newimage: str|QImage|QPixmap )->bool:
        """ Set the label to either a pixmap or the contents of a file"""
        if isinstance(newimage, QImage):
            return self._set_from_image(newimage )
        if isinstance(newimage, QPixmap):
            return self._set_from_pixmap(newimage )
        if isinstance(newimage, str):
            return self._set_from_file( newimage  )
        return False
    
    def setDocument( self, *args ):
        """ Dummy function to handle PDF Interface """
        pass

    def close(self):
        """ Closing a label will just clear the contents """
        self.clear()
