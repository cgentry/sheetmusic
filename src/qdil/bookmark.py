""" High level database interface for bookmarks
    This is based on the lower-level DbBookmark class
"""
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

from PySide6.QtCore     import Qt
from PySide6.QtWidgets  import QInputDialog, QMessageBox

from qdb.fields.bookmark import BookmarkField
from qdb.dbbookmark     import DbBookmark
from ui.bookmark        import UiBookmark

class DilBookmark( DbBookmark):
    """High level bookmark class, wraps DbBookmark

    Args:
        DbBookmark (class): database interface (basic)
    """
    def __init__(self, book: str | int=None):
        super().__init__()
        self.bookmark = None
        self.book_name = None
        self.open( book )

    def open(self, book: str | int ):
        """ Open bookmark for book """
        self.close()
        self.book_id   = self.lookup_book_id(book)

    def close(self):
        """Close book. Name and bookmarks are deleted.
        """
        self.bookmark = None
        self.book_name = None

    def is_open( self )->bool:
        """return open status

        Returns:
            bool: True if book is open, false otherwise
        """
        return self.book_name is not None

    def count(self)->int:
        """
        Get number of pages

        Returns:
            int: Number of pages in book
        """
        return super().get_count( book=self.book_name )

    def all( self )->list:
        """
            get all bookmarks complete data
        """
        return super().get_all( book=self.book_name )

    def get_list(self )->list:
        """
            This returns just the names of bookmarks as a name list
            (Other bookmark fields are ignored )
        """
        bmk = super().get_all( book=self.book_name )
        return [ bookmark[ BookmarkField.NAME ] for bookmark in bmk ]

    def lookup_bookmark( self, page:int)->dict:
        """ Lookup bookmark for current book and page """
        return super().get_bookmark_for_page( book=self.book_name, page=page )

    def first(self):
        """ Return first bookmark for current book """
        return super().get_first( book = self.book_name )

    def last(self):
        """ Return last bookmark for current book """
        return super().get_last( book = self.book_name )

    def get_previous(self, page:int)->dict:
        """ Get previous boookmark from this page. return a dictionary with page/content """
        return super().get_previous_bookmark_for_page(book=self.book_name, page=page)

    def get_next(self, page:int)->dict:
        """ Get next """
        return super().get_next_bookmark_for_page(book=self.book_name, page=page )

    def is_last( self, bookmark:dict )->bool:
        """
            Pass in the bookmark dictionary we returned and determine if this is the last
        """
        next_mark = super().get_next_bookmark_for_page(
                    book=self.book_name,
                    page=bookmark[BookmarkField.PAGE ])
        return( next_mark is None or next_mark[BookmarkField.PAGE] is None )

    def is_first( self, bookmark:dict)->bool:
        """
            Pass in the bookmark dictionary we returned and determine if this is the first
        """
        prev = super().get_previous_bookmark_for_page(
                        book=self.book_name,
                        page=bookmark[BookmarkField.PAGE ])
        return  prev is None or prev[BookmarkField.PAGE] is  None

    def save(self, name:str=None, page:int=0, layout:str=None )->None:
        '''
            Save a bookmark with name, page number and layout.
            pageNumer should be absolute in order to go to page properly.
            Layout is optional, but if passed it will be saved.
            If no name is passed, it will be 'Page-nnn' (nnn=pagenumber)

        '''
        del layout
        if name is None:
            name = f'Page-{page}'
        super().add( self.book_name, name, page )

    def current_book(self , book:str, page_relative:int, page_absolute:int ):
        """Prompt for current page number

        Args:
            book (str): Title of book
            page_relative (int): Bookmark's relative page number
            page_absolute (int): Bookmark's absolute page number
        """
        prompt = f"{book} bookmark at page {page_absolute}"
        if page_relative != page_absolute :
            prompt = prompt + f" (Shown {page_relative})"

        dlg = QInputDialog()
        dlg.setLabelText( prompt )
        dlg.setTextValue( "")
        dlg.setOption(QInputDialog.UsePlainTextEditForTextInput, False)
        dlg.setWindowFlag( Qt.FramelessWindowHint )
        if dlg.exec() :
            self.save( name=dlg.textValue() , page=page_absolute)


    def delete_select( self , book_name:str , ui_bmk:UiBookmark )->dict:
        """ Delete boomkarks with user prompt """
        ui_bmk.setBookmarkList( self.all() )
        bookm = {}
        rtn = ui_bmk.exec()
        if rtn == QMessageBox.Accepted:
            if ui_bmk.action_ == 'go':
                new_page = ui_bmk.selected_page
                if new_page :
                    bookm = super().get_bookmark_for_page( book=self.book_name, page=new_page )
                elif ui_bmk.selected_page :
                    #pylint: disable=C0209
                    title = "{}:   {}\n{}:   {}\n{}:    {}\n{}:    {}".format(
                        "Book", book_name,
                        "Bookmark", ui_bmk.selectedBookmark,
                        "Page shown", ui_bmk.page_relative,
                        "Book page:", ui_bmk.selected_page )
                    #pylint: enable=C0209
                    qbox = QMessageBox()
                    qbox.setIcon(QMessageBox.Question)
                    qbox.setCheckBox(None)
                    qbox.addButton('Delete', QMessageBox.AcceptRole)
                    qbox.addButton('Cancel', QMessageBox.RejectRole)

                    qbox.setText("Delete bookmark?")
                    qbox.setInformativeText(ui_bmk.selectedBookmark)
                    qbox.setDetailedText(title)
                    if qbox.exec() == QMessageBox.AcceptRole:
                        DbBookmark().delete(
                            book=book_name ,
                            bookmark=ui_bmk.selectedBookmark )
                    qbox.close()
                    del qbox
        ui_bmk.close()
        return bookm

    # def addBookmarkDialog( self, dlg ):
    #     try:
    #         self.addBookmarkDialogx( dlg )
    #     except Exception as err:
    #         raise( err )

    # def addBookmarkDialogx( self, dlg ):
    #     while dlg.exec() == QDialog.Accepted:
    #         changes = dlg.get_changes()
    #         dlg.clear()
    #         currentBookmark = self.get_name_for_page(
    #               self.book_name ,
    #               page=changes[ BookmarkField.PAGE ] )
    #         if currentBookmark :
    #             dlg.setup_fields( changes[BookmarkField.NAME])
    #             dlg.error("<b>Duplicate Bookmarked page {}:<br>{}</b>".format(
    #                   changes[BookmarkField.PAGE ] , currentBookmark))
    #         else:
    #             self.save( bookmark_name=changes[ BookmarkField.NAME ],
    #                   page_number=changes[ BookmarkField.PAGE ])
    #             if dlg.buttonClicked == dlg.BtnSave: # One shot operation
    #                 break
