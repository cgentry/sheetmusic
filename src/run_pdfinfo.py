from util.pdfinfo import PdfInfo

if __name__ == "__main__":
	pdf = PdfInfo( )
	if pdf.has_pdf_library():
		print( pdf.get_info_from_pdf( '/Volumes/organ/_music/David Sanger - Play The Organ - Volume 1 - Rescan.pdf'))
	else:
		print("There is no PDF library!")
