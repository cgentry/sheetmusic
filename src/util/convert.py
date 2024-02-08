"""
Utility: Provide common conversion routines

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

import base64
import pickle

from qdb.keys import DbKeys

def encode(value, code=DbKeys.ENCODE_STR):
    """Encode the value into what can be stored in
    the storage system.

    Args:
        value (Any ): Any value to be encoded
        code (int, optional): Method of encoding.
            Defaults to DbKeys.ENCODE_STR.

    Returns:
        Any: Properly encoded value
    """

    if value is None:
        return None
    if code == DbKeys.ENCODE_B64:
        return base64.b64encode(value)
    if code == DbKeys.ENCODE_PICKLE:
        return base64.b64encode(
                pickle.dumps(value)).decode('ascii')
    return str(value)

def decode( value,
            code=DbKeys.ENCODE_STR,
            default=None):
    """Decode the value from encoded form

    Args:
        value (Any): Value to decode
        code (int, optional): Method of encoding.
            Defaults to DbKeys.ENCODE_STR.
        default (Any, optional): What to return if unalbe to decode.
            Defaults to None.

    Returns:
        _type_: _description_
    """
    if value is None:
        value = default
    if code == DbKeys.ENCODE_BOOL:
        return to_bool(value, default)
    if code == DbKeys.ENCODE_B64:
        return base64.b64decode(value)
    if code == DbKeys.ENCODE_INT:
        return to_int(value)
    return str(value)

def to_int( value, default=0, ignore=True) -> int:
    """Convert value to integer

    Args:
        value (any): Value to be converted
        default (int, optional): Default value if invalid input.
            Defaults to 0.
        ignore (bool, optional): Ignore error or throw exception.
            Defaults to True (ignore)

    Raises:
        err: ValueError

    Returns:
        int: converted value
    """
    rtn = default
    if value is not None and value != "":
        if isinstance( value, bool ):
            rtn =  ( 1 if value else 0)
        else:
            try:
                rtn= int(value)
            except ValueError as err:
                print(str(err))
                if not ignore:
                    raise err
    return rtn

def to_bool(v,default=False):
    """ Convert a value to boolean.
    This will make sure we don't raise an exception and can
    handle the user's usual inputs. Also, allows default if
    no value passed
    """
    if isinstance(v,bool):
        return v
    if v is None:
        return default
    if isinstance( v , int ):
        return v != 0
    return v.lower() in ("yes", "true", "t", "1","ok")
