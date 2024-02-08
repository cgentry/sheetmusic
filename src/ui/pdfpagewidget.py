"""
User Interface : PDF Dsiplay widgets

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

from PySide6.QtCore import QPoint,  QSize, Signal
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication

from qdb.log import DbLog
from ui.mixin.pagedisplay import PageDisplayMixin
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget
from ui.label import LabelWidget


class PdfView(PageDisplayMixin,QPdfView):
    """ Base level for PDF display"""
    def __init__(self, name: str):
        PageDisplayMixin.__init__( self, name )
        QPdfView.__init__(self)

        self.setObjectName(name)
        self.setPageMode(QPdfView.PageMode.SinglePage)
        self.setZoomMode(QPdfView.ZoomMode.FitInView)

        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: black')

    def navigate(self, page_number: int):
        """ Navigate to a specific page """
        if self.document() is not None:
            self.set_pagenum( page_number )
            nav = self.pageNavigator()
            nav.jump(page_number-1, QPoint(), nav.currentZoom())
            self.show()
            return True
        return False


class PdfLabel(LabelWidget):
    """ Use PDF documents to display sheetmusic
    Replaces the previous use of images derived from pdf"""
    documentChanged = Signal(QPdfDocument)
    def __init__(self, name: str):
        super().__init__(name)
        self.pdf_document = None
        self.ratio = QApplication.primaryScreen().devicePixelRatio()


    def set_doc(self, *args):
        """ Set the current pdf document """
        if len( args) < 1 or args[0] is not QPdfDocument:
            raise ValueError( 'Invalid argument for set_doc')
        if args[0] != self.pdf_document:
            self.pdf_document = args[0]
            self.documentChanged.emit(args[0])

    def navigate(self, page_number: int)->bool:
        """ Navigate to a PDF page"""
        if self.pdf_document is not None:
            if page_number == 0 or page_number is None:
                return False
            if not self.dimensions.isSet :
                self.dimensions.checkSizeDocument( self.pdf_document )
            render_size = self.dimensions.equalisePage(
                                self.pdf_document, page_number ) * ( self.ratio )
            self.set_pagenum( page_number )
            img = self.pdf_document.render(page_number-1, render_size)
            return self.set_content( img )
        return False

    def close(self):
        self.clear()


class PdfPageWidget(PageDisplayMixin, ISheetMusicDisplayWidget):
    """ PdfPageWidget is created by the PdfWidget
        It is responsible for displaying a single page from the PDF
    """
    pdf_error = {QPdfDocument.Error.Unknown: 'Unknown',
                 QPdfDocument.Error.DataNotYetAvailable: 'Not available',
                 QPdfDocument.Error.FileNotFound: 'Not found',
                 QPdfDocument.Error.InvalidFileFormat: 'Invalid format',
                 QPdfDocument.Error.IncorrectPassword: 'Incorrect Password',
                 QPdfDocument.Error.UnsupportedSecurityScheme: 'Locked'}

    def __init__(self, name: str, usepdf:bool=False ):
        self._widget = None
        PageDisplayMixin.__init__( self, name )
        ISheetMusicDisplayWidget.__init__(self)
        self._name = name
        self._use_pdf_viewer = usepdf
        self.logger = DbLog('PdfPageWidget')
        self._current_pdf = QPdfDocument()
        self._create_viewer()
        self.clear()

    def _create_viewer(self ):
        self._widget = (PdfView(self._name)
                        if self._use_pdf_viewer else
                        PdfLabel(self._name))
        #self._widget.setStyleSheet( "border-color: blue; border-width: 7px;background: white;")
        # self._widget.documentChanged.connect(self._document_changed)

    # -----------------------------------------------
    #        DISPLAY METHODS
    # -----------------------------------------------
    #
    @property
    def pdfdisplaymode(self )->bool:
        """ return True if we are using pdf viewer"""
        return self._use_pdf_viewer

    @pdfdisplaymode.setter
    def pdfdisplaymode(self, usepdf:bool):
        if usepdf != self._use_pdf_viewer:
            content = self.content()
            page = self.page_number()
            iscontent = self.iscontent()
            self._use_pdf_viewer = usepdf
            self._create_viewer( )
            if iscontent :
                self.set_content_page( content  , page )

    def _document_changed(self, document: QPdfDocument):
        self.logger.debug('Document changed ' +
            document.metaData(QPdfDocument.MetaDataField.Title))
        rtn = self.widget().navigate( self.page_number() )
        self.logger.debug( f'Return is {rtn}')

    def hide(self) -> None:
        """ Hide the pdfview widget """
        return self.widget().hide()

    def is_visible(self) -> bool:
        return self.widget().is_visible()

    def show(self) -> None:
        return self.widget().show()

    def clear(self) -> None:
        """ Clear the widget and current PDF document """
        self.set_clear(True)
        if self._widget is not None:
            self._widget.close()
        if self._current_pdf is not None:
            self._current_pdf.close()

    def resize(self, wide: int | QSize, height: int = 0) -> None:
        """ Issue a resize either with a QSize or dimentsions"""
        if isinstance(wide, QSize):
            self.widget().resize(wide)
        else:
            if height > 0:
                self.widget().resize(wide, height)
        return self.widget().navigate( self.page_number() )

    # -----------------------------------------------
    #      CONTENT METHODS
    #  -----------------------------------------------
    #
    def widget(self) -> PdfLabel|PdfView:
        """Return the current PDF widget in use

        Raises:
            ValueError: No PDF widget defined

        Returns:
            PdfLabel|PdfView: Current PDF widget
        """
        if self.widget is None:
            raise ValueError('Widget is none')
        return self._widget

    def iscontent(self)->bool:
        """determine if current doc is a PDF

        Returns:
            bool: True if set and QPdfDocument
        """
        return self._current_pdf is not None and \
            isinstance( self._current_pdf, QPdfDocument )

    def content(self) -> QPdfDocument | None:
        """ Return the current PDF Document"""
        return self._current_pdf

    def is_page_valid( self, page:int )->bool:
        """Determine if a page number is valid
        A page must be set, content must be set
        and the page must be within the page boundries

        Args:
            page (int): page number

        Returns:
            bool: True if a valid page
        """
        return self.ispage() and \
            self.iscontent() and \
                self.content().pageCount() < page

    def set_content(self, content: QPdfDocument | str) -> bool:
        """
            Pass in the PDF Document for the widget

            If you set the content, a page gets displayed. you should call set_content_page
        """

        if isinstance(content, str):
            self.logger.debug(f'pdf is file {content}')
            self._current_pdf = QPdfDocument()
            err = self._current_pdf.load(content)

            if err is not None and err != QPdfDocument.Error.None_:
                msg = PdfPageWidget.pdf_error[
                    err] if err in PdfPageWidget.pdf_error else '(Unknown)'
                self.logger.error(
                    f'Err loading document: {err}:{msg}')
                return self.set_clear(False)
        else:
            self.logger.debug(
                f'pdf doc title is {content.metaData(QPdfDocument.MetaDataField.Title)}')
            self._current_pdf = content

        self.widget().dimensions = self.dimensions
        self.widget().setDocument(self._current_pdf )
        return self.set_clear(True)

    def set_content_page(self,
                         content: QPdfDocument | str,
                         page_number: int = 1) -> bool:
        """ Pass in the PDF Document and page number to go to
            This is a convience function. You can also call 'setContent' then 'set_pagenum'

            This loads the document and relies on the signal to set the page
        """
        self.set_content(content)
        return self.widget().navigate( page_number )

    def _pdfview_page(self, page: int) -> bool:
        return self.widget().navigate(page)

    def _lblview_page(self, page: int) -> bool:
        pass

    def set_pagenum(self, page_number: int) -> bool:
        """ Navigate to the page number passed.

            True if we changed page number, false if not
        """
        if page_number < 1 and not self.is_page_valid( page_number):
            #pylint: disable=C0209
            self.logger.debug('Page not valid: {} < {}'.format(
                ('no doc' if not self.iscontent()
                  else self._current_pdf.pageCount()),
                page_number))
            #pylint: enable=C0209
            return False

        self.logger.debug(f'Set page to {page_number}')
        self.widget().dimensions = self.dimensions
        return self.widget().navigate( page_number )

    def page_number(self)->int:
        return self.widget().page_number()

    def copy(self, source_object )->bool:
        """ Copy moves the page number from one PDF view to this one """
        if source_object.iscontent():
            page = source_object.page_number()
            self.set_content_page(source_object.content(), page )
        return not self.is_clear()
