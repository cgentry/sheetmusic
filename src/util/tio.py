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

#########################
# tio contains small, terminal IO routines writting to make my life
# easier. 
#       printDictionary takes a dict and prints out titles and a nice columnar list
#       printColums takes an input list and prints out data as a column


from selectors import DefaultSelector

def printDictionary( dbDictionary, title:str="Current entries", key:str=None, order:list=[], skip:list=[], totalWidth:int=100)->None:
    """
        key:    what will be the 'title' of this entry
        order:  what order whould fields be printed in
                if order is empty or None, ALL fields will be printed.
        skip:   Which fields should be skipped, even if in the order list
                (This overrides the printed list)
    """
    if len( dbDictionary) == 0 :
        print( "(No entries)")
        return
    print(title , end="")
    ## compute widest entry.

    if len(order) == 0:
        order = dbDictionary[0].keys()
    chunk = 0
    counter = 0
    keyWidth = 0
    for row in dbDictionary:
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
                keyWidth = max( keyWidth , len( rkey ))
                thisLen = len( rkey) + len(str(entry)) + 2
                chunk += thisLen
                counter += 1
    chunk = int( chunk / counter ) 
    maxChunks = max( 1 , int(totalWidth / chunk ) )

    ## we print out in columns of 'chunk' size
    for row in dbDictionary:
        if key is not None:
            print( "\n\n{}\n{}".format( row[ key ], "-"*(len(row[key])))  , end="")
        numChunksUsed=99
        for rkey in order:
            if rkey in row:
                entry = row[ rkey ]
            else:
                entry = "(doesn't exist)"                
            if entry is None:
                entry = '-'
            if rkey != key and not rkey in skip:
                prval = F"{ rkey : >{keyWidth}}: {str(entry)} " 
                prlen = len( prval )
                ## how many 'chunks' will this take ?
                numChunksNeeded = max( 1 , int( (chunk-1 + prlen) / chunk ) )
                numChunksUsed += numChunksNeeded
                #print("\nlen:", prlen, "NeedChunks", numChunksNeeded, "maxChunks:", maxChunks,"Chunks used",numChunksUsed, end="\t" )
                if numChunksUsed > maxChunks:
                    print("\n  . ", end="")
                    numChunksUsed = numChunksNeeded
                print( F"{ prval : <{numChunksNeeded*chunk}}", end="" )
    print("\n")

    

def printColumns( list ,title:str='Current entries:', numberColumns:int=None,totalWidth:int=100)->None:
    if len(list) == 0 :
        print( "(No entries)")
        return
    print( title )
    ## Each entry is numbered 1-n. How long should we print each entry?
    ## allow 2 extra for ': '
    numbersWide = max(2,len( str( len( list ))))
    ### find maximum length of a list entry
    maxLengthListEntry = 0
    for entry in list:
        maxLengthListEntry = max( len(entry), maxLengthListEntry )
    
    if numberColumns==None:
        numberColumns = max( 1 , int(totalWidth/(maxLengthListEntry+numbersWide+4)) )
    for across in range(0,numberColumns):
        print( "{}-{}  ".format( '-'*(numbersWide+1), '-'*(maxLengthListEntry)) , end="")
    print("")
    listIndex = 0
    for i in range( 0, len(list )):
        if listIndex >= len( list ):
                break
        for across in range( 0, numberColumns ):
            if listIndex >= len( list ):
                break
            print( F"{ listIndex+1 : >{numbersWide}}: { list[listIndex] :<{maxLengthListEntry+2}}" , end="")
            listIndex += 1
        print("")
    print("\n")

def question( prompt:str , default:str='y')->bool:
    """
        Ask a 'yes' or 'no' question. If enter, the default answer will be returned.
    """
    defaultAnswer = 'Y|n' if default == 'y' else 'y|N'
    value = input( "{}? ({}) ".format(prompt , defaultAnswer) )
    value = value.strip()
    if not value:
        value = default
    value = value.lower()
    return ( value.startswith('y') or value == 'ok' )

def selectListEntry( list , addEntry=True, allowBlank=True, confirm=True)->str:
    """ 
        Return either the string from the list, a new entry, or None if
        new entries are not allowed.
        addEntry    True to allow new text entries, False to only low index into list
        allowBlank  True to allow blank entries
        confirm     True to confirm entry False to reurn whatever is entered.
    """
    if len(list) == 0 and addEntry == False:
        return None

    returnValue = ''
    while True:
        if len( list ) > 0:
            if addEntry:
                value = input("Enter record number or new entry: ")
            else:
                value = input("Enter record number: ")
        else:
            value = input("Enter new entry: ")
        value = value.strip()
        if value.isdigit() :
            index = int(value)-1
            if index >= len( list ) and index < 0:
                print("Invalid entry, retry")
                continue
            returnValue = list[ index]
        else:
            if not addEntry:
                print("Please enter record number from list")
                continue
            if not value and not allowBlank:
                print("Blank entries are not allowed")
                continue
            returnValue = value
        if not confirm or question( "Use '{}' for entry".format( returnValue )):
            break
    return returnValue
    
def inputint( prompt:str, default:int=1, min:int=1, max:int=999)->int:
    """
        Input an integer within the min, max values passed.
    """
    while True:
        value = input("{} (default is {}) : ".format(prompt, default))
        value = value.strip()
        if not value:
            return default
        try:
            intval = int( value )
        except Exception as err:
            print(str(err))
            continue
        if intval < min or intval > max:
            print("'{}' is outside accepted values {} to {}", value, min, max)
        else:
            break
    return intval

def inputIfNone( prompt:str, default:str=None, required:bool=True)->str:
    """
        This will prompt for input if there is no default value passed.
        If they enter nothing when prompted and required is true, it will
        keep prompting.
    """
    if default is None or default == '':
        while True:
            default = input( "{}: ".format( prompt ))
            default = default.strip()
            if default or not required:
                break
            print("Input is required")
    return default