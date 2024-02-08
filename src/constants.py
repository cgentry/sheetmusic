"""
Program Constants

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import platform
from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class ProgramConstants:
    """Program constatns used throughout the program """
    VERSION = "0.7.01"
    VERSION_MAIN = "0.7"
    AUTHOR = "Charles Gentry"
    COPYRIGHT = '©2022-2024 Charles Gentry'
    SYSTEM = platform.system()
    ISMACOS = platform.system() == 'Darwin'
    SYSTEM_NAME = 'SheetMusic'

    RETURN_CANCEL = False
    RETURN_CONTINUE = True

    OUT_PLAIN = 'plain'
    OUT_STDOUT = 'stdout'
    OUT_NONE = 'none'
