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
#
#
import pathlib
from PySide6.QtPdf import QPdfDocument
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from qdb.keys import BOOK, BOOKSETTING
from util.pdfclass import PdfDimensions


class PdfInfo:
    """
    PdfInfo will link to a Python PDF library to get information about the PDF. 

    If there is no library, nothing will be returned. If no fields are present no field will be returned.
    """

    def __init__(self):
        return

    def has_pdf_library(self) -> bool:
        return True

    def open(self, name):
        self.pdfDocument = QPdfDocument()
        self.pdfDocument.load(name)
        self.pdfclass = PdfDimensions()

    def _calculate_pdf_largest_size(self):
        for page in range(self.document.pageCount()):
            self.pdfclass.checkSize( self.document.pagePointSize(page) )

    def get_info_from_pdf(self, sourcefile):
        self.open(sourcefile)
        pdf_info = {
            BOOK.author: self.pdfDocument.metaData(QPdfDocument.MetaDataField.Author),
            BOOK.name: self.pdfDocument.metaData(QPdfDocument.MetaDataField.Title),
            BOOK.pdfCreated: self.pdfDocument.metaData(QPdfDocument.MetaDataField.CreationDate),
            BOOK.pdfModified: self.pdfDocument.metaData(QPdfDocument.MetaDataField.ModificationDate),
            BOOK.publisher: self.pdfDocument.metaData(QPdfDocument.MetaDataField.Producer),
        }
        if pdf_info[BOOK.name] == '':
            pdf_info[BOOK.name] = pathlib.Path(sourcefile).stem

        self._calculate_pdf_largest_size( )
        pdf_info[ BOOKSETTING.dimensions ] = self.pdfclass 
        return pdf_info
