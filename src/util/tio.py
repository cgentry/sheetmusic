"""
User Interface :Terminal IO routiens

 tio contains small, terminal IO routines writting to make my life
 easier.
       print_dictionary takes a dict and prints out titles and a nice columnar list
       print_columns takes an input list and prints out data as a column

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

"""

def print_dictionary( db_dict:[dict],
                     title:str="Current entries",
                     key:str=None,
                     order:list=None,
                     skip:list=None,
                     width:int=100)->None:
    """
        Print the db_dict in a nice, orderly list
    Args:
        db_dict (list dict): List of database returns
            [0-n] { key: value , key: value}
        title (str, optional): Title for the list.
            Defaults to "Current entries".
        key (str, optional): _description_.
            Defaults to None.
        order (list, optional):
            List of keys to print, in order desirec.
            Defaults to None. (Use keys returned)
        skip (list, optional): List of keys to skip.
            Defaults to None.
        width (int, optional): Total width of output
            Defaults to 100.
    """
    if len( db_dict) == 0 :
        print( "(No entries)")
        return
    print(title , end="")
    ## compute widest entry.

    if order is None or len(order) == 0  :
        order = db_dict[0].keys()
    if skip is None:
        skip = []
    chunk = 0
    counter = 0
    key_width = 0
    for row in db_dict:
        if order is None or len( order ) == 0:
            order = row.keys()
        for rkey in order:
            if rkey in row:
                entry = row[ rkey ]
            else:
                entry = "(doesn't exist)"
            if entry is None:
                entry = '-'
            if rkey != key and rkey not in skip:
                key_width = max( key_width , len( rkey ))
                this_len = len( rkey) + len(str(entry)) + 2
                chunk += this_len
                counter += 1
    chunk = int( chunk / counter )
    chunks = max( 1 , int(width / chunk ) )

    ## we print out in columns of 'chunk' size
    for row in db_dict:
        if key is not None:
            print( "\n\n{}\n{}".format( row[ key ], "-"*(len(row[key])))  , end="")
        chunks_used=99
        for rkey in order:
            if rkey in row:
                entry = row[ rkey ]
            else:
                entry = "(doesn't exist)"
            if entry is None:
                entry = '-'
            if rkey != key and not rkey in skip:
                prval = F"{ rkey : >{key_width}}: {str(entry)} "
                prlen = len( prval )
                ## how many 'chunks' will this take ?
                chunks_needed = max( 1 , int( (chunk-1 + prlen) / chunk ) )
                chunks_used += chunks_needed
                if chunks_used > chunks:
                    print("\n  . ", end="")
                    chunks_used = chunks_needed
                print( F"{ prval : <{chunks_needed*chunk}}", end="" )
    print("\n")



def print_columns( list_values:[list] ,
                  title:str='Current entries:',
                  columns:int=None,
                  width:int=100)->None:
    """Pirnt out a list in columnar format

    Args:
        list_values (list]): Data list
        title (_type_, optional): Title fo list.
            Defaults to 'Current entries:'.
        columns (int, optional): Number of columns to print.
            Defaults to None.
        width (int, optional): Column width.
            Defaults to 100.
    """
    if len(list_values) == 0 :
        print( "(No entries)")
        return
    print( title )
    ## Each entry is numbered 1-n. How long should we print each entry?
    ## allow 2 extra for ': '
    number_wide = max(2,len( str( len( list_values ))))
    ### find maximum length of a list entry
    max_len_list_entry = 0
    for entry in list_values:
        max_len_list_entry = max( len(entry), max_len_list_entry )

    if columns is None:
        columns = max( 1 , int(width/(max_len_list_entry+number_wide+4)) )
    for _ in range(0,columns):
        print( f"{'-'*(number_wide+1)}-" +\
            f"{'-'*(max_len_list_entry)}  " , end="")
    print("")
    for list_index, list_value in  enumerate( list_values  ):
        if list_index % columns == 0 :
            print( "" )
        print( f"{ list_index+1 : >{number_wide}}: "\
               f"{ list_value :<{max_len_list_entry+2}}" , end="")
    print("\n")

def question( prompt:str , default:str='y')->bool:
    """
        Ask a 'yes' or 'no' question. If enter, the default answer will be returned.
    """
    default_answer = 'Y|n' if default == 'y' else 'y|N'
    value = input( f"{prompt}? ({default_answer}) ")
    value = value.strip()
    if not value:
        value = default
    value = value.lower()
    return ( value.startswith('y') or value == 'ok' )

def select_entry( select_list:[list] , add=True, blanks=True, confirm=True)->str:
    """Return either the string from the list, a new entry, or None if
        new entries are not allowed.

        add    True to allow new text entries, False to only low index into list
        blanks  True to allow blank entries
        confirm     True to confirm entry False to reurn whatever is entered.

    Args:
        select_list (list): list to check or add entries to
        add (bool, optional): True to allow new text entries
            False to only allow index into list.
            Defaults to True.
        blanks (bool, optional): True to allow blank entries.
            Defaults to True.
        confirm (bool, optional): True to confirm entry
            False to return whatever is entered.
            Defaults to True.

    Returns:
        str: _description_
    """
    if len(list) == 0 and add is False:
        return None

    rtn = ''
    while True:
        if len( select_list ) > 0:
            if add:
                value = input("Enter record number or new entry: ")
            else:
                value = input("Enter record number: ")
        else:
            value = input("Enter new entry: ")
        value = value.strip()
        if value.isdigit() :
            index = int(value)-1
            if index >= len( select_list ) and index < 0:
                print("Invalid entry, retry")
                continue
            rtn = select_list[ index]
        else:
            if not add:
                print("Please enter record number from list")
                continue
            if not value and not blanks:
                print("Blank entries are not allowed")
                continue
            rtn = value
        if not confirm or question( f"Use '{rtn}' for entry"):
            break
    return rtn

def inputint( prompt:str, default:int=1, minimum:int=1, maximum:int=999)->int:
    """
        Input an integer within the min, max values passed.
    """
    while True:
        value = input(f"{prompt} (default is {default}) : ")
        value = value.strip()
        if not value:
            return default
        try:
            intval = int( value )
        except ValueError as err:
            print(str(err))
            continue
        if intval < minimum or intval > maximum:
            print(f"'{value}' is outside accepted values {minimum} to {maximum}")
        else:
            break
    return intval

def input_if_none( prompt:str, default:str=None, required:bool=True)->str:
    """
        This will prompt for input if there is no default value passed.
        If they enter nothing when prompted and required is true, it will
        keep prompting.
    """
    if default is None or default == '':
        while True:
            default = input( f"{prompt}: ")
            default = default.strip()
            if default or not required:
                break
            print("Input is required")
    return default

if __name__ == "__main__":
    test_list = ["aaaaaaaa", "bbbbbbb", "ccccccc", "ddd", "eee", "fff", "ggg", "hhh", "iii",
                 "aaaaaaaa", "bbbbbbb", "ccccccc", "ddd", "eee", "fff", "ggg", "hhh", "iii"]
    print_columns( test_list )