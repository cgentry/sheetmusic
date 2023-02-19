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
from   os import path
from   datetime import datetime
from   pathlib import PurePath

from qdb.keys         import BOOK, DbKeys, ImportNameSetting

class _SimplePdfInfo:
    """
        Base class for PDF information.
    """
    def __init__(self, pdf_lib:None ):
        self.pdf_lib = pdf_lib
        self.pdf_info = { }

    def get_info_from_pdf( self, filename:str )->dict:
        pass

class _DefaultPdfInfo( _SimplePdfInfo ):
    """ This actually doesn't do anything but returns an empty dictionary
    
        This allows us to add any default information as if it came from 
        a PDF
    """

    def get_info_from_pdf( self, filename:str )->dict:
        super().get_info_from_pdf( filename )
        return self.pdf_info
    
class _UsePyPDF( _SimplePdfInfo ):
           
    def _get_meta_info( self, metadata ):
        if metadata.title is not None:
            self.pdf_info[BOOK.name] = metadata.title 
        if metadata.author is not None:
            self.pdf_info[BOOK.author ] = metadata.author
        if metadata.producer is not None:
            self.pdf_info[BOOK.publisher] = metadata.producer
        if metadata.creation_date_raw is not None:
            try:
                text = metadata.creation_date_raw.replace("'","" )
                if text.find( 'Z' ) != -1:
                        dt = datetime.strptime( text[0:17] , "D:%Y%m%d%H%M%S%z" )
                else:
                        dt = datetime.strptime( text , "D:%Y%m%d%H%M%S%z" )
                self.pdf_info[ BOOK.pdfCreated ]= dt.isoformat( ' ')
            except Exception as err:
                print( "Error on dt '{}' ignored: {}".format( text , str(err )) )
                pass

        return
    
    def _get_keyword_info( self, keyword_data ):
        """ Read the xmp for keywords and fill in additonal data fields
        
            NOTE: This is not yet implemented. Once decode the info from 
            PREVIEW, it will be filled in
        """
        if keyword_data is not None:
            pass
    
    def _get_annotation_info( self, pages ):
        """ Examine annotation / notes for keywords to use """
        
        annotation_search = { 'Composer:' : BOOK.composer , 
                             'Genre:'      : BOOK.genre , 
                             'Title:'     : BOOK.name ,
                             'Author:'    : BOOK.author,
                             'Publisher:' : BOOK.publisher,
                             'Link:'      : BOOK.link, }
        for page in pages:
            # if "/Keywords" in page:
            #     print("Keyword")
            # if "/Bookmark" in page:
            #     print("Bookmark")
            try:
                if page is not None and "/Annots" in page:
                    for annot in page["/Annots"]:
                        subtype = annot.get_object()["/Subtype"]
                        if subtype == "/Text":
                            lines = annot.get_object()["/Contents"].splitlines()
                            for line in lines:
                                line = line.strip()
                                for search_for , key in annotation_search.items() :
                                    if line.startswith(search_for):
                                        self.pdf_info[ key ] = line[ len( search_for) : ].strip()
            except Exception as err: # currently ignore errors
                print( 'Error with pages {}'.format( str(err)))
                pass
        return

    def get_info_from_pdf(self, sourceFile ):
        """ Try to get info from PDF direct.

            This uses the the pdf library created in the setup. It will:
            (1) get simple, generic information from metadata
            (2) Try and get more information from the XML metadata
            (3) Finally try and find annotation within the pages and fill in extra fields.
        """

        super().get_info_from_pdf( sourceFile )
        pdf_file = open( sourceFile, 'rb')
        pdf_read = self.pdf_lib.PdfReader(pdf_file)
                
        self.pdf_info[BOOK.numberEnds]  = len( pdf_read.pages )
        self._get_meta_info( pdf_read.metadata )
        self._get_keyword_info( pdf_read.xmp_metadata )
        self._get_annotation_info( pdf_read.pages )
        return self.pdf_info

class PdfInfo:
    """
    PdfInfo will link to a Python PDF library to get information about the PDF. 
    
    If there is no library, nothing will be returned. If no fields are present no field will be returned.
    """

    _pdf_library_list = [ 'pypdf', 'pypdf2']
    _pdf_import = None

    def __init__(self, prefer:str=None ):
        if not self.has_pdf_library() :
            if prefer is not None:
                position = PdfInfo._pdf_library_list.index( prefer )
                if position > -1 :
                    PdfInfo._pdf_library_list.pop( position )
                    PdfInfo._pdf_library_list.insert(0,prefer)

            for library_name in PdfInfo._pdf_library_list:
                try:
                    lib = __import__( library_name )
                    PdfInfo._pdf_import = library_name
                    break
                except:
                    pass

    def has_pdf_library(self)->bool:
        return PdfInfo._pdf_import is not None
    
    def get_info_from_pdf( self, sourcefile)->dict: 
        """
            Get info from PDF using a PDF library If none are availble it will return
            default information.
        """
        if PdfInfo._pdf_import == 'pypdf':
            pdf = _UsePyPDF( __import__( PdfInfo._pdf_import ) )
        else:
            pdf = _DefaultPdfInfo( None )
        return pdf.get_info_from_pdf( sourcefile )

    