from curses.ascii import isdigit
import getopt, sys, os
from qdb.dbbook import DbBook, DbGenre, DbComposer
from qdb.setup import Setup
from qdb.keys  import BOOK
from util.tio import printColumns, question, selectListEntry, inputint,inputIfNone, printDictionary

###
### This is one of those 'quick' utilities that seems to have grown horribly.
### written mostly as procedural code (yeah, yeah, don't moan) it's really 
### just used for me to check on things in the database.
###
SKIP_THIS_BOOK = '.skip'

def usage():
    print("Usage:")
    print("{} database command [parameters] [-d directory]".format(sys.argv[0]))
    print("\tdatabase   directory holding database")
    print("\tcommand    One of:")
    print("\t           init - build new database")
    print("\t           scan - scan book directory")
    print("\t           update - update any incomplete entries")
    print("\t           list - print all books")
    print("\t               short - it will only print out a short bit of info")
    print("\t               fields name.....name - print only field names")
    print("\t           change type  where type is:")
    print("\t               composers Migrate one genre to another")
    print("\t               genre     Migrate one genre to another")
    print("\t-d dir     sheetmusic directory")
    print("\t           default is ~/sheetmusic\n")

def parseArgs()->bool:
    global directory, database, command, tableType, options
    options = []

    database = sys.argv[1]
    command  = sys.argv[2]
    
    start = 3
    for name in sys.argv[start:]:
        if name.startswith('-'):
            break
        options.append( sys.argv[start] )
        start = start+1
    argumentList = sys.argv[start:]

    directory = "~/sheetmusic"
    database = os.fspath(os.path.expanduser( database ) + '/sheetmusic.sql' )

    # Options
    short_options = "hd:"
 
    # Long options
    long_options = ["Help", "dir="]
 
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, short_options, long_options)
     
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                usage()
                return(False)
             
            elif currentArgument in ("-d", "--dir"):
                directory =  sys.argv[0]
             
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()
        return False

    directory = os.fspath( os.path.expanduser( directory))
    print( "Sheetmusic in", directory)
    print( "Database is", database,"\n")
    return True


def list():
    global directory, options
    bk = DbBook()
    sortOrder = 'book'
    skipFields = []
    fields = []
    if 'order' in options:
        index = options.index('order')
        index += 1
        if index < len( options):
            sortOrder = options[ index ]
            if sortOrder == 'name':
                sortOrder = 'book'
    if 'fields' in options:
        index = options.index('fields')
        index += 1
        if index < len( options):
            fields = options[index:]
        else:
            fields = ['composer', 'genre', BOOK.dateAdded, BOOK.dateUpdated, BOOK.dateRead, 'last_read', 'numbering_starts', 'numbering_ends', 'location', 'source']
            skipFields=['id']
    rows = bk.getAll( order=sortOrder)
    if rows is not None:
        if 'short' in options:
            for row in rows:
                print("ID: {:03} TITLE: '{}'".format(row['id'], row['book']))
            print("\n")
        else:
            bookDictionary = [dict(r) for r in rows ]
            printDictionary( bookDictionary , key='book', skip=skipFields, order=fields)
    else:
        print("There are no books to print")

def listComposer():
    bk = DbBook()
    printColumns( bk.getAllComposers() )

def listGenre():
    printColumns( DbGenre().getAll() )

def _checkValueForCommand( value ):
    """
        this checks input to see if it is either a .skip or .quit
        if .skip, it returns None as the value
        if .quit or .exit, the program will exit.
    """
    specialHelp = """
    Enter a period (.) followed by any of these words separated by comma:
        pretty - Capitalise each word and replace dashes and underscores with blanks
        caps -   Split name at capital letters into separate words (e.g. HelloThere becomes Hello There)
        skip -   Skip this book and move on to the next.
        quit -   Quit the program.
    You can combine commands, for example .caps,pretty and it will perform both operations.
"""
    if value == SKIP_THIS_BOOK:
        print("\t**** No changes recorded, skipping this book")
        return SKIP_THIS_BOOK
    if value == '.quit' or value == '.exit':
        print("Exiting program\n")
        sys.exit(0)
    if value == '.' or value == '.?':
        print( specialHelp)
    return value

def _getEntryValue( category , list )->str:
    while True:
        value=input("Enter the {} for this book (? for list, {} ID, or return for none): ".format(category, category))
        value = value.strip()
        returnValue = ""
    
        if value:
            if _checkValueForCommand( value ) == SKIP_THIS_BOOK :
                return SKIP_THIS_BOOK
            if value in ['.', '.?']:
                continue
            if value == '?':
                printColumns( list )
                returnValue = selectListEntry( list , confirm=False)
            else:
                if not value.isdigit():
                    returnValue = value
                else:
                    if int(value) < 1 or int(value) > len(list):
                        print("Index out of range.")
                        continue
                returnValue = list[ int(value)-1]
        ## end if value
        break
    return returnValue

def _getComposer():
    list = DbBook().getAllComposers()
    while True:
        rtnValue = _getEntryValue( 'composer', list)
        if rtnValue == SKIP_THIS_BOOK:
            return SKIP_THIS_BOOK
        if question("Use '{}' for composer".format( rtnValue) ):
            return rtnValue
    

def _getGenre():
    list = DbGenre().getAll()
    while True:
        rtnValue = _getEntryValue( 'genre', list )
        if question("Use '{}' for genre".format( rtnValue) ):
            return rtnValue

def _getPages():
    print("These offsets are when page numerbering starts and how many pages there are.")
    start = inputint("Enter the offset for the first page numbered")
    end = inputint("Enter the highest page number shown in book:") + start - 1
    return ( start, end )

def _getName( book )->str:
    prompt=True

    while prompt:
        value = input("\tEnter new name: (return to keep, . for special commands): ")
        value = value.strip()
        if value:
            if value.startswith('.'):
                if _checkValueForCommand( value ) == SKIP_THIS_BOOK:
                    return SKIP_THIS_BOOK
                if value in [ '.' , '.?'] :
                    continue
                if value.__contains__('caps'):
                    import re
                    splits = re.split('[A-Z]', book)
                    value = ' '.join(splits)
                    value = value.title()
                if value.__contains__('pretty') or value.__contains__('title'):
                    for rep in ['-', '_', '  ','"',"'"]:
                        value = book.replace(rep, " ")
                    value = value.title()
        else:
            value = book
        prompt = not question("\tUse '{}' for name".format(value))
    return value

def _update( list ):
    bk = DbBook()
    
    for book, items in list.items():
        skip = False
        print("\nBook:", book)
        changes = {'book': book }
        confirm = []
        confirmFormat='{:20} {}'
        for problem in items:
            if skip:
                continue
            print( "\t{}{}".format(problem[0].upper(), problem[1:]) )
            if problem.startswith( 'name:'):
                value = _getName( book )
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:           
                    changes['*book'] = value
                    changes['name_default'] = 0
                    confirm.append( confirmFormat.format( 'Book name', value) )
            if problem.startswith('composer:'):
                value =  _getComposer()
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:
                    changes['composer'] = value
                    confirm.append( confirmFormat.format( 'Composer', value) )
            if problem.startswith( 'genre:'):
                value = _getGenre()
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:
                    changes['genre'] = value
                    confirm.append( confirmFormat.format( 'Genre', value) )
            if problem.startswith('numbering:'):
                (start, end) = _getPages()
                changes['numbering_starts'] = start
                changes['numbering_ends'] = end
                confirm.append( confirmFormat.format( 'Offset to first page', value) )
                confirm.append( confirmFormat.format( 'Number of pages', end-start+1) )
        if skip == False and len(changes)> 1:
            print("Confirm changes")
            print( confirmFormat.format("Field", "New value"))
            print( confirmFormat.format("-"*20, "-"*40 ))
            if question( "{}\n\nOK to continue".format( "\n".join( confirm)) ):
                print("call with:", changes)
                count=bk.update( **changes )
                print("\tchanged {} record.".format( count ))

            else:
                print("*** Changes canceled")

def scan( ):
    global directory, database, command
    from qdil.book import DilBook
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    
    bk = DilBook()
    bk.addBookDirectoryUI()

def update():
    from qdil.book import DilBook
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    
    bk = DilBook()
    bk.updateIncompleteBooksUI()


def migrate():
    global options
    if 'genre' in options:
        bk = DbGenre()
        list = bk.getAll()
        printColumns( list ,title='Current genre entries:')
        oldValue = selectListEntry( list , addEntry=False, allowBlank=False, confirm=False)
        newValue = inputIfNone( prompt="New genre name", required=True)
        if question("Change '{}' to '{}'".format( oldValue, newValue )) :
            rcount = bk.editAllGenres( oldValue, newValue)
            print("Total records changed:", rcount )
        else:
            print("Change cancelled!\n")
    elif 'composer' in options:
        bk = DbComposer()
        list = bk.getAllComposers()
        printColumns( list ,title='Current composer entries:')
        oldValue = selectListEntry( list , addEntry=False, allowBlank=False, confirm=False)
        newValue = inputIfNone( prompt="New composer name", required=True)
        if question("Change '{}' to '{}'".format( oldValue, newValue )) :
            rcount = bk.editAllComposers( oldValue, newValue)
            print("Total records changed:", rcount )
        else:
            print("Change cancelled!\n")
    else:
        print("Invalid change type.")
        usage()
        sys.exit(1)

def init( s:Setup ):
    print("*"*62)
    print("* This will load some predefined composers and genres.       *")
    print("* It will not delete or remove any data that has been added. *")
    print("*"*62)
    if question( "Do you want to initialise the database? "):
        s.initData()


if __name__ == "__main__":
    """
    The first parm should be the database name.
    The second parm should be the command
    Then, -d is for directory commands
    If not, it will add it (prompting will occur)
    """
    global directory, database, command
    sys.path.append("../")
    if len(sys.argv) < 3:
        usage()
        print("\nERROR: Too few arguments\n")
        sys.exit(1)

    if not parseArgs():
        print("FAIL")
        sys.exit(2)

    if not command in ['scan', 'print', 'list','init','composer','composers', 'genres', 'genre', 'change','update']:
        print("Error: Unknown command {}".format(command))
        usage()
    else:
        try:
            s=Setup(database)
            s.createTables()
            if command == 'scan':
                scan(  )
            elif command == 'init':
                init(s )
            elif command == 'update':
                update()
            elif command.startswith( 'composer'):
                listComposer()
            elif command.startswith('genre'):
                listGenre()
            elif command.startswith('change'):
                migrate()
            else:
                list()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt - program terminated\n")
    
