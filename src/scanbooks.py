"""
CLI for working with database

 This file is part of SheetMusic
 Copyright: 2022,2023 by Chrles Gentry
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 This file is part of Sheetmusic.

 This is one of those 'quick' utilities that seems to have grown horribly.
 written mostly as procedural code (yeah, yeah, don't moan) it's really
 just used for me to check on things in the database.

"""
import getopt
import sys
import os
import re
from dataclasses import dataclass

from PySide6.QtWidgets import QApplication

from qdb.fields.book import BookField
from qdb.dbbook import DbBook, DbGenre, DbComposer, Migrate
from qdb.setup import Setup
from util.tio import ( print_columns, question,
                      select_entry, inputint,
                      input_if_none, print_dictionary )
from qdil.book import DilBook

SKIP_THIS_BOOK = '.skip'

@dataclass( init=False)
class Variables :
    """ this holds 'global' values for the routines"""
    directory = None
    database = None
    command = None
    table_type = None
    options = None

def usage():
    """ Print out a general usage command like most UNIX utilities """
    print("Usage:")
    print(
        f"{sys.argv[0]} database command [parameters] [-d directory]")
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


def parse_args() -> bool:
    """ Parse the command line argumens """

    Variables().options = []
    Variables().database = sys.argv[1]
    Variables().command = sys.argv[2]

    start = 3
    for name in sys.argv[start:]:
        if name.startswith('-'):
            break
        Variables().options.append(sys.argv[start])
        start = start+1
    arg_list = sys.argv[start:]

    Variables().directory = "~/sheetmusic"
    Variables().database = os.fspath(
        os.path.expanduser(Variables().database) \
            + '/sheetmusic.sql')

    # Options
    short_options = "hd:"

    # Long options
    long_options = ["Help", "dir="]

    try:
        # Parsing argument
        arguments, _ = getopt.getopt(
            arg_list, short_options, long_options)

        # checking each argument
        for current_argument, _ in arguments:
            if current_argument in ("-h", "--Help"):
                usage()
                return False

            if current_argument in ("-d", "--dir"):
                Variables().directory = sys.argv[0]

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
        usage()
        return False

    Variables().directory = os.fspath(os.path.expanduser(Variables().directory))
    print("Sheetmusic in", Variables().directory)
    print("Database is", Variables().database, "\n")
    return True


def list_all():
    """ List all books in the system """
    dbbook = DbBook()
    sort_order = 'book'
    skip_fields = []
    fields = []
    if 'order' in Variables().options:
        index = Variables().options.index('order')
        index += 1
        if index < len(Variables().options):
            sort_order = Variables().options[index]
            if sort_order == 'name':
                sort_order = 'book'
    if 'fields' in Variables().options:
        index = Variables().options.index('fields')
        index += 1
        if index < len(Variables().options):
            fields = Variables().options[index:]
        else:
            fields = ['composer',
                      'genre',
                      BookField.DATE_ADDED,
                      BookField.DATE_UPDATED,
                      BookField.DATE_READ,
                      'last_read',
                      'numbering_starts',
                      'numbering_ends',
                      'location',
                      'source']
            skip_fields = ['id']
    rows = dbbook.get_all(order=sort_order)
    if rows is not None:
        if 'short' in Variables().options:
            for row in rows:
                print(f"ID: {row['id']:03d} TITLE: '{row['book']}'")
            print("\n")
        else:
            book_dictionary = [dict(r) for r in rows]
            print_dictionary(book_dictionary, key='book',
                            skip=skip_fields, order=fields)
    else:
        print("There are no books to print")


def list_composers():
    """ List all composers in db """
    print_columns(DbComposer().get_all())


def list_genres():
    """ List all genres in db """
    print_columns(DbGenre().get_all())


def _check_value_for_command(value):
    """
        this checks input to see if it is either a .skip or .quit
        if .skip, it returns None as the value
        if .quit or .exit, the program will exit.
    """
    special_help = """
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
    if value in ( '.quit' , '.exit'):
        print("Exiting program\n")
        sys.exit(0)
    if value in ( '.','.?' ):
        print(special_help)
    return value


def _get_entry_value(category, list_values) -> str:
    while True:
        value = input(f"Enter the {category} for this book \
            (? for list, {category} ID, or return for none): ")
        value = value.strip()
        return_value = ""

        if value:
            if _check_value_for_command(value) == SKIP_THIS_BOOK:
                return_value =  SKIP_THIS_BOOK
                break
            if value in ['.', '.?']:
                continue
            if value == '?':
                print_columns(list_values)
                return_value = select_entry(list_values, confirm=False)
            else:
                if not value.isdigit():
                    return_value = value
                else:
                    if 1 < int(value) > len(list_values):
                        print("Index out of range.")
                        continue
                return_value = list_values[int(value)-1]
        # end if value
        break
    return return_value


def _get_composer():
    clist = DbComposer().get_all()
    while True:
        rtn_value = _get_entry_value('composer', clist)
        if rtn_value == SKIP_THIS_BOOK:
            return SKIP_THIS_BOOK
        if question(f"Use '{rtn_value}' for composer"):
            return rtn_value


def _get_genre():
    glist = DbGenre().get_all()
    while True:
        rtn_value = _get_entry_value('genre', glist)
        if question(f"Use '{rtn_value}' for genre"):
            return rtn_value


def _get_pages():
    print("These offsets are when page numerbering starts and how many pages there are.")
    start = inputint("Enter the offset for the first page numbered")
    end = inputint("Enter the highest page number shown in book:") + start - 1
    return (start, end)


def _get_name(book) -> str:
    prompt = True

    while prompt:
        value = input(
            "\tEnter new name: (return to keep, . for special commands): ")
        value = value.strip()
        if value:
            if value.startswith('.'):
                if _check_value_for_command(value) == SKIP_THIS_BOOK:
                    return SKIP_THIS_BOOK
                if value in ['.', '.?']:
                    continue
                if 'caps' in value:
                    splits = re.split('[A-Z]', book)
                    value = ' '.join(splits)
                    value = value.title()
                if 'pretty' in value or 'title' in value:
                    for rep in ['-', '_', '  ', '"', "'"]:
                        value = book.replace(rep, " ")
                    value = value.title()
        else:
            value = book
        prompt = not question(f"\tUse '{value}' for name")
    return value


def _update(blist):
    dbbook = DbBook()

    for book, items in blist.items():
        skip = False
        print("\nBook:", book)
        changes = {'book': book}
        confirm = []
        confirm_format = '{:20} {}'
        for problem in items:
            if skip:
                continue
            print(f"\t{problem[0].upper()}{problem[1:]}")
            if problem.startswith('name:'):
                value = _get_name(book)
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:
                    changes['*book'] = value
                    changes['name_default'] = 0
                    confirm.append(confirm_format.format('Book name', value))
            if problem.startswith('composer:'):
                value = _get_composer()
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:
                    changes['composer'] = value
                    confirm.append(confirm_format.format('Composer', value))
            if problem.startswith('genre:'):
                value = _get_genre()
                if value is None or value == SKIP_THIS_BOOK:
                    skip = True
                    continue
                if value:
                    changes['genre'] = value
                    confirm.append(confirm_format.format('Genre', value))
            if problem.startswith('numbering:'):
                (start, end) = _get_pages()
                changes['numbering_starts'] = start
                changes['numbering_ends'] = end
                confirm.append(confirm_format.format(
                    'Offset to first page', value))
                confirm.append(confirm_format.format(
                    'Number of pages', end-start+1))
        # end of for loop
        if skip is False and len(changes) > 1:
            print("Confirm changes")
            print(confirm_format.format("Field", "New value"))
            print(confirm_format.format("-"*20, "-"*40))
            if question("{}\n\nOK to continue".format("\n".join(confirm))):
                print("call with:", changes)
                count = dbbook.update(**changes)
                print(f"\tchanged {count} record.")

            else:
                print("*** Changes canceled")


def scan():
    """ Import a book directory """
    app = QApplication()

    bk = DilBook()
    bk.import_directory()
    del app


def update():
    """ Update incomplete books """
    app = QApplication()

    bk = DilBook()
    bk.update_incomplete_books_ui()
    del app

def migrate():
    """Migrate all genres or composers from one to another.

    This will allow a user to change from Mozartt to Mozart (for example)
    """
    if 'genre' in Variables().options:
        genre = DbGenre()
        genre_list = genre.get_all()
        print_columns(genre_list, title='Current genre entries:')
        current_value = select_entry(
            genre_list, add=False, blanks=False, confirm=False)
        new_value = input_if_none(prompt="New genre name", required=True)
        if question(f"Change '{current_value}' to '{new_value}'"):
            rcount = Migrate().genres(current_value, new_value)
            print("Total records changed:", rcount)
        else:
            print("Change cancelled!\n")
    elif 'composer' in Variables().options:
        composer = DbComposer()
        composer_list = composer.get_all_composers()
        print_columns(composer_list, title='Current composer entries:')
        current_value = select_entry(
            composer_list, add=False, blanks=False, confirm=False)
        new_value = input_if_none(prompt="New composer name", required=True)
        if question(f"Change '{current_value}' to '{new_value}'"):
            rcount = Migrate().composers(current_value, new_value)
            print("Total records changed:", rcount)
        else:
            print("Change cancelled!\n")
    else:
        print("Invalid change type.")
        usage()
        sys.exit(1)


def init(sup: Setup):
    """Initialise values and database as required.

    Args:
        s (Setup): Setup class
    """
    print("*"*62)
    print("* This will load some predefined composers and genres.       *")
    print("* It will not delete or remove any data that has been added. *")
    print("*"*62)
    if question("Do you want to initialise the database? "):
        sup.init_data()


if __name__ == "__main__":
    # The first parm should be the database name.
    # The second parm should be the command
    # Then, -d is for directory commands
    # If not, it will add it (prompting will occur)

    sys.path.append("../")
    if len(sys.argv) < 3:
        usage()
        print("\nERROR: Too few arguments\n")
        sys.exit(1)

    if not parse_args():
        print("FAIL")
        sys.exit(2)

    if not Variables().command in [
        'change',
        'composer', 'composers',
        'genre', 'genres',
        'print',
        'scan',
        'list',
        'init',
            'update']:
        print(f"Error: Unknown command {Variables().command}")
        usage()
    else:
        try:
            s = Setup(Variables().database)
            s.create_tables()
            if Variables().command == 'scan':
                scan()
            elif Variables().command == 'init':
                init(s)
            elif Variables().command == 'update':
                update()
            elif Variables().command.startswith('composer'):
                list_composers()
            elif Variables().command.startswith('genre'):
                list_genres()
            elif Variables().command.startswith('change'):
                migrate()
            else:
                list_all()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt - program terminated\n")
