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

from functools import singledispatchmethod

from PySide6.QtCore import QPoint, Qt, QSize, Signal
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPixmap, Qt

from qdb.log import DbLog
from ui.mixin.pagedisplay import PageDisplayMixin
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget
from ui.label import LabelWidget


class PdfView(PageDisplayMixin,QPdfView):
    def __init__(self, name: str):
        super().__init__()
        self.setObjectName(name)
        self.setPageMode(QPdfView.PageMode.SinglePage)
        self.setZoomMode(QPdfView.ZoomMode.FitInView)

        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: black')

    def navigate(self, page: int):
        if self.document() is not None:
            nav = self.pageNavigator()
            nav.jump(page, QPoint(), nav.currentZoom())
            self.show()
            return True
        return False


class PdfLabel(LabelWidget):
    documentChanged = Signal(QPdfDocument)

    def __init__(self, name: str):
        super().__init__(name)
        self.pdfDocument = None
        self.ratio = QApplication.primaryScreen().devicePixelRatio()
        self._render_size = None

    def _calculate_pdf_largest_size( self ):
        self._width = 0
        self._height = 0

        for page in range( self.pdfDocument.pageCount() ):
            pdf_point_size = self.pdfDocument.pagePointSize( page )
            if pdf_point_size is not None:
                self._width = max( pdf_point_size.width() , self._width )
                self._height = max( pdf_point_size.height() , self._height )
                self._render_size = QSize(int(self._width * self.ratio), int(self._height*self.ratio))

    def setDocument(self, pdfdocument: QPdfDocument):
        if pdfdocument != self.pdfDocument:
            self.pdfDocument = pdfdocument
            self.documentChanged.emit(pdfdocument)
            self._calculate_pdf_largest_size()

    def navigate(self, page: int)->bool:
        if self.pdfDocument is not None:
            if self._render_size is None:
                self._calculate_pdf_largest_size()
            print('** RENDER',  self._render_size )
            return self.setContent( self.pdfDocument.render(page, self._render_size) )
            self.hide()
        return False

    def close(self):
        self.clear()


class PdfPageWidget(PageDisplayMixin, ISheetMusicDisplayWidget):
    pdf_error = {QPdfDocument.Error.Unknown: 'Unknown',
                 QPdfDocument.Error.DataNotYetAvailable: 'Not available',
                 QPdfDocument.Error.FileNotFound: 'Not found',
                 QPdfDocument.Error.InvalidFileFormat: 'Invalid format',
                 QPdfDocument.Error.IncorrectPassword: 'Incorrect Password',
                 QPdfDocument.Error.UnsupportedSecurityScheme: 'Locked'}

    def __init__(self, name: str):
        super(PageDisplayMixin, self).__init__()
        super(ISheetMusicDisplayWidget, self).__init__()
        self._use_pdf_viewer = False
        self.logger = DbLog('PdfPageWidget')
        self._current_pdf = QPdfDocument()
        self._create_viewer(name)
        self.clear()

    def _create_viewer(self, name: str):
        self._widget = (PdfView(name) 
                        if self._use_pdf_viewer else 
                        PdfLabel(name))
        self._widget.setStyleSheet( "border-color: blue; border-width: 7px;background: white;")
        self._widget.documentChanged.connect(self._document_changed)

    def _document_changed(self, document: QPdfDocument):
        self.logger.debug('Document changed {}'.format(
            document.metaData(QPdfDocument.MetaDataField.Title)))
        rtn = self.widget().navigate( self.pageNumber() )
        self.logger.debug( f'Return is {rtn}')

    def clear(self) -> None:
        self.setClear(True)
        try:
            self.widget().close()
        except:
            pass
        if self._current_pdf is not None:
            try:
                self._current_pdf.close()
            except:
                pass
        
    def widget(self) -> PdfLabel|PdfView:
        return self._widget

    def content(self) -> QPdfDocument | None:
        """ Return the current PDF Document"""
        return self._current_pdf

    def setContent(self, pdfdoc: QPdfDocument | str) -> bool:
        """ 
            Pass in the PDF Document for the widget

            If you set the content, a page gets displayed. you should call setContentPage
        """

        if isinstance(pdfdoc, str):
            self.logger.debug('pdf is file {}'.format(pdfdoc))
            self._current_pdf = QPdfDocument()
            err = self._current_pdf.load(pdfdoc)

            if err is not None and err != QPdfDocument.Error.None_:
                msg = PdfPageWidget.pdf_error[
                    err] if err in PdfPageWidget.pdf_error else '(Unknown)'
                self.logger.error(
                    'Err loading document: {}:{}'.format(err, msg))
                return self.setClear(False)
        else:
            self.logger.debug('pdf doc title is {}'.format(
                self.pdfdoc.metaData(QPdfDocument.MetaDataField.Title)))
            self._current_pdf = pdfdoc
        self.widget().setDocument(self._current_pdf)
        return self.setClear(True)

    def setContentPage(self, pdfdoc: QPdfDocument | str, page: int = 1) -> bool:
        """ Pass in the PDF Document and page number to go to
            This is a convience function. You can also call 'setContent' then 'setPageNumber'

            This loads the document and relies on the signal to set the page
        """
        super().setPageNumber( page )
        return self.setContent(pdfdoc)

    def _pdfview_page(self, page: int) -> bool:
        return self.widget().navigate(page)

    def _lblview_page(self, page: int) -> bool:
        pass

    def setPageNumber(self, page: int) -> bool:
        """ Navigate to the page number passed.

            True if we changed page number, false if not
        """
        if (self._current_pdf is None or not self.isPage() or 
                self._current_pdf.pageCount() < page):
            self.logger.debug('Page not set: {} < {}'.format(
                ('no doc' if self._pdf_view.document()
                 is None else self._pdf_view.document().pageCount()),
                page))
            return False
        
        self.logger.debug(f'Set page to {page}')
        super().setPageNumber( page )
        return self.widget().navigate( page )

    def copy(self, otherPage)->bool:
        """ Copy moves the page number from one PDF view to this one """
        self.clear()
        if not otherPage.isClear():
            self.setContent(otherPage.content())
            self.setPageNumber(otherPage.page())
        return not self.isClear()


    def resize(self, width: int | QSize, height: int = 0) -> None:
        """ Issue a resize either with a QSize or dimentsions"""
        print('** PDF RESIZE', width, height )
        if isinstance(width, QSize):
            self.widget().resize(width)
        else:
            if height > 0:
                self.widget().resize(width, height)
        return self.widget().navigate( self.pageNumber() )

    def hide(self) -> None:
        return self.widget().hide()

    def isVisible(self) -> bool:
        return self.widget().isVisible()

    def show(self) -> None:
        return self.widget().show()
