from PySide6.QtCore import QPoint

from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from ui.pagewidget import PageDisplayMixin
from ui.interface.sheetmusicdisplay import ISheetMusicDisplayWidget
    
class PdfDisplayWidget( PageDisplayMixin , ISheetMusicDisplayWidget ):
    def __init__( self, *args, **kargs ):
        super().__init__( *args, **kargs )
        self._create_viewer()
        self._current_page = 0
        self._current_pdf = None

    def _create_viewer(self):
        self.widget = QWidget()
        self.pdf = QPdfView()
        self.pdf.setPageMode( QPdfView.PageMode.SinglePage )
        self.pdf.setZoomMode( QPdfView.ZoomMode.FitInView )

    def widget( self )->QWidget:
        return self.widget
    
    def pdfview( self )->QPdfView:
        return self.pdf

    def clear(self )->None:
        self._current_page = 0
        self._current_pdf = None
        self.setClear(True)
        self.setPageNumber(self.PAGE_NONE)

    def content( self )->QPdfDocument:
        self.setClear( False )
        return self.pdf.document()
    
    def setContent( self, pdfdoc: QPdfDocument )->bool:
        """ Pass in the PDF Document for the viewer """
        self.close()
        self.pdf.setDocument( pdfdoc )
        return True
    
    def setContentPage( self, pdfdoc:QPdfDocument , page:int=1  )->bool:
        """ Pass in the PDF Document and page number to go to
        
            This is a convienence function which simply calls setContent and setpage
        """
        self.setContent( pdfdoc )
        self.setPage( page )
        return True
    
    def pageNumber(self)->int:
        return self._current_page if self._current_pdf is not None else 0
    
    def setPageNumber( self, page:int )->bool:
        """ Navigate to the page number passed.
        
            True if we changed page number, false if not
        """
        if self.pdf.document().pageCount() < page:
            return False
        
        nav = self.pdf.pageNavigator()
        nav.jump(page, QPoint(), nav.currentZoom() )
        self._current_page = page
        return True

    def copy( self, otherPage ):
        """ Copy moves the page number from one PDF view to this one """
        self.clear()
        if not otherPage.isClear():
            self.setContent( otherPage.content() )
            self.setPageNumber(otherPage.page())
        return not self.isClear()

    def setKeepAspectRatio( self, arg_1: bool)->None:
        """ Ignore whatever they set and keep aspect ratio
        
            PDFs will always display properly.
        """
        super().setKeepAspectRatio( True )

    def resize( self, width:int|QSize, height:int=0)->None:
        if isinstance( width, QSize ):
            self.widget().resize( width )
        else:
            if height > 0 :
                self.widget().resize( width , height )

    def hide(self )->None:
        return self.widget().hide()

    def isVisible(self)->bool:
        return self.widget().isVisible()
    
    def show(self)->None:
        return self.widget().show()
#class PdfWidget: