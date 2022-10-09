# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
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

from db.dbbookmark  import DbBookmark
from db.keys        import BOOKMARK
from ui.bookmark    import UiBookmark
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog, QMessageBox, QDialog
from db.dbgeneric   import DbTransform

class DilBookmark( DbBookmark):
    def __init__(self, book=None):
        super().__init__()
        self.open( book )

    def open(self, book ):
        self.bookmark = None
        self.bookName = book

    def close(self):
        self.bookmark = None
        self.bookName = None

    def isOpen( self )->bool:
        return self.bookName is not None
    
    def getTotal(self)->int:
        return super().getTotal( book=self.bookName )

    def getAll( self )->list:
        """
            get all bookmarks complete data
        """
        return super().getAll( book=self.bookName )

    def getList(self )->list:
        """
            This returns just the names of bookmarks as a name list
        """
        return DbTransform().toList( super().getAll( book=self.bookName ) )

    def getBookmarkPage( self, page:int)->dict:
        return super().getBookmarkForPage( book=self.bookName, page=page )

    def getFirst(self):
        return super().getFirst( book = self.bookName )

    def getLast(self):
        return super().getLast( book = self.bookName )

    def getPrevious(self, page:int)->dict:
        return super().getPreviousBookmarkForPage(book=self.bookName, page=page)

    def getNext(self, page:int)->dict:
        return super().getNextBookmarkForPage(book=self.bookName, page=page )

    def isLast( self, bookmark:dict )->bool:
        """
            Pass in the bookmark dictionary we returned and determine if this is the last
        """
        nextBkm = super().getNextBookmarkForPage( book=self.bookName, page=bookmark[BOOKMARK.page ])
        return( nextBkm is None or nextBkm[BOOKMARK.page] is None )

    def isFirst( self, bookmark:dict)->bool:
        """
            Pass in the bookmark dictionary we returned and determine if this is the first
        """
        prevBkm = super().getPreviousBookmarkForPage( book=self.bookName, page=bookmark[BOOKMARK.page ])
        return ( prevBkm is None or prevBkm[BOOKMARK.page] is  None)

    def saveBookmark(self, bookmarkName:str=None, pageNumber:int=0, layout:str=None )->None:
        '''
            Save a bookmark with name, page number and layout. 
            pageNumer should be absolute in order to go to page properly.
            Layout is optional, but if passed it will be saved.
            If no name is passed, it will be 'Page-nnn' (nnn=pagenumber)
            
        '''
        if bookmarkName is None:
            bookmarkName = 'Page-{}'.format( pageNumber )
        super().addBookmark( self.bookName, bookmarkName, pageNumber )

    def addBookmark(self , book:str, relativePage:int, absolutePage:int ):
        prompt = "Name for bookmark at "
        if relativePage != absolutePage :
            prompt = prompt + "Book Page {:d} / Page Shown {:d}:".format( absolutePage, relativePage )
        else:
            prompt = prompt + "Book Page {:d}:".format( absolutePage )
        windowFlag = Qt.FramelessWindowHint

        dlg = QInputDialog()
        dlg.setLabelText( prompt )
        dlg.setTextValue( "")
        dlg.setOption(QInputDialog.UsePlainTextEditForTextInput, False)
        dlg.setWindowFlag( windowFlag )
        if dlg.exec() :
            self.saveBookmark( bookmarkName=dlg.textValue() , pageNumber=absolutePage)
    
    def delete( self , bookName:str , uiBookmark:UiBookmark )->dict:
        uiBookmark.setBookmarkList( self.getBookmarkList() )
        bookm = {}
        rtn = uiBookmark.exec()
        if rtn == QMessageBox.Accepted:
            if uiBookmark.action == 'go':
                newPage = uiBookmark.selectedPage
                if newPage :
                    bookm = super().getBookmarkForPage( book=self.bookName, page=newPage )
                elif uiBookmark.selectedPage :
                    title = "{}:   {}\n{}:   {}\n{}:    {}\n{}:    {}".format(
                        "Book", bookName, 
                        "Bookmark", uiBookmark.selectedBookmark,
                        "Page shown", uiBookmark.relativePage, 
                        "Book page:", uiBookmark.selectedPage )
                    qbox = QMessageBox()
                    qbox.setIcon(QMessageBox.Question)
                    qbox.setCheckBox(None)
                    qbox.addButton('Delete', QMessageBox.AcceptRole)
                    qbox.addButton('Cancel', QMessageBox.RejectRole)

                    qbox.setText("Delete bookmark?")
                    qbox.setInformativeText(uiBookmark.selectedBookmark)
                    qbox.setDetailedText(title)
                    if qbox.exec() == QMessageBox.AcceptRole:
                        DbBookmark().delBookmark( 
                            book=bookName ,
                            bookmark=uiBookmark.selectedBookmark )
                    qbox.close()
                    del qbox
        uiBookmark.close()
        return bookm
    
    def addBookmarkDialog( self, dlg ):
        try:
            self.addBookmarkDialogx( dlg )
        except Exception as err:
            raise( err )

    def addBookmarkDialogx( self, dlg ):
        while dlg.exec() == QDialog.Accepted:
            changes = dlg.getChanges()
            dlg.clear()
            currentBookmark = self.getNameForPage( self.bookName , page=changes[ BOOKMARK.page ] )
            if currentBookmark :
                dlg.setupFields( changes[BOOKMARK.name])
                dlg.error("<b>Duplicate Bookmarked page {}:<br>{}</b>".format( changes[BOOKMARK.page ] , currentBookmark))
                continue
            else:
                self.saveBookmark( bookmarkName=changes[ BOOKMARK.name ],pageNumber=changes[ BOOKMARK.page ])
                if dlg.buttonClicked == dlg.BtnSave: # One shot operation
                    break
