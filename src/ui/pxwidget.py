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

from PySide6.QtWidgets import ( QMainWindow)
from ui.pxpagewidget import PxPageWidget
from ui.bottomsheet import BottomSheet

class PxWidget( BottomSheet):
    """ PageWidget will construct and handle multi-page layouts. 
        It handles all the construction, layout, and page flipping
        functions.
    """
    
    def __init__(self, MainWindow: QMainWindow):
        super().__init__( MainWindow , u'PxWidget')
 
    def content_generator( self , obj_name:str )->PxPageWidget:
        return PxPageWidget( obj_name)
