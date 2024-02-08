"""
Testing program: This just tests PdInfo.

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""
from util.pdfinfo import PdfInfo

if __name__ == "__main__":
    FNAME = '/Volumes/organ/_music/David Sanger - Play The Organ - Volume 1 - Rescan.pdf'
    pdf = PdfInfo()
    if pdf.has_pdf_library():
        print(pdf.get_info_from_pdf(FNAME))
    else:
        print("There is no PDF library!")
