"""
Database Fields: BookPropertyField

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class BookPropertyField:
    """
        BookProperty are values that MAY be in the book or, if None, will be in System
    """
    LAYOUT = 'layout'
    FILE_TYPE = 'file_type'
