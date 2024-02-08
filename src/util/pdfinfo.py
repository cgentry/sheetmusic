"""
 Utility function : Interface to QPdfDocument

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
import pathlib
from PySide6.QtPdf import QPdfDocument
from qdb.fields.booksetting import BookSettingField
from qdb.dbbook import BookField
from util.pdfclass import PdfDimensions


class PdfInfo:
    """
    PdfInfo will link to a Python PDF library to get information about the PDF.

    If there is no library, nothing will be returned.
    If no fields are present no field will be returned.
    """

    def __init__(self):
        self._current_file = None
        self.pdfclass = None
        self.pdf_document = QPdfDocument()
        return

    def has_pdf_library(self) -> bool:
        """ Determine if we hae PDF support"""
        return True

    def open(self, name:str):
        """ Open the pdf document 'name'"""
        if self._current_file != name :
            if self.pdf_document is not None:
                self.pdf_document.close()
            self._current_file = name
            self.pdf_document.load(name)
            self.pdfclass = PdfDimensions()

    def _calculate_pdf_largest_size(self):
        for page in range(self.pdf_document.pageCount()):
            self.pdfclass.checkSize( self.pdf_document.pagePointSize(page) )

    def get_info_from_pdf(self, sourcefile:str)->dict:
        """Get information from the sourcefile name passed

        Args:
            sourcefile (str): Name of file to get info

        Returns:
            dict: Key: value dictionary. Properties of PDF
        """
        self.open(sourcefile)
        pdf_info = {
            BookField.AUTHOR:
                self.pdf_document.metaData(QPdfDocument.MetaDataField.Author),
            BookField.NAME:
                self.pdf_document.metaData(QPdfDocument.MetaDataField.Title),
            BookField.PDF_CREATED:
                self.pdf_document.metaData(QPdfDocument.MetaDataField.CreationDate),
            BookField.PDF_MODIFIED:
                self.pdf_document.metaData(QPdfDocument.MetaDataField.ModificationDate),
            BookField.PUBLISHER:
                self.pdf_document.metaData(QPdfDocument.MetaDataField.Producer),
        }
        if pdf_info[BookField.NAME] == '':
            pdf_info[BookField.NAME] = pathlib.Path(sourcefile).stem

        self._calculate_pdf_largest_size( )
        pdf_info[ BookSettingField.KEY_DIMENSIONS ] = self.pdfclass
        return pdf_info
