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

import platform

Symbols = {
    'edit'     : '\U0000270D',
    'notebook' : "\U0001F4D4",
    'notepage' : "\U0001F4C4",
}

class ProgramConstants:
    version      = "0.6.05"
    version_main = "0.6"
    author       = "Charles Gentry"
    copyright    = u'©2022-2023 Charles Gentry'
    system       = platform.system()
    ismacos      = ( platform.system() == 'Darwin')
    system_name  = 'SheetMusic'
    
class DbKeys():
    """
    Class contains all of the settings for labels and key default values. 
    The home directory is still kept in the profile setting in order to 'bootstrap'

    The system stores 
    """
    VALUE_DEFAULT_DB_FILENAME     = 'sheetmusic.sql'
    VALUE_DEFAULT_DIR   = "~/sheetmusic"
    VALUE_DEFAULT_USER_SCRIPT_DIR = "~/sheetmusic/scripts"
    VALUE_FILE_PREFIX   = 'page'
    VALUE_FILE_TYPE     = 'png'
    VALUE_FILE_RES      = '300'
    VALUE_GSDEVICE      = 'png16m'
    VALUE_KEEP_ASPECT   = True

    VALUE_PAGES_SINGLE  = "single"
    VALUE_PAGES_SIDE_2  = "side_2"
    VALUE_PAGES_SIDE_3  = 'side_3'
    VALUE_PAGES_STACK_2 = "stack_2"
    VALUE_PAGES_STACK_3 = "stack_3"

    VALUE_SMART_PAGES   = True
    VALUE_REOPEN_LAST   = True
    VALUE_SCRIPT_CMD    = '/bin/bash'
    VALUE_SCRIPT_SPLIT  = ';'              ## Split script variables with this char
    VALUE_SCRIPT_VAR    = '-c'
    VALUE_LAST_IMPORT_DIR = '~'
    VALUE_RECENT_SIZE_MIN = 5
    VALUE_RECENT_SIZE_MAX = 20
    VALUE_SHOW_FILEPATH = True
    VALUE_RECENT_SIZE_DEFAULT = 10
    VALUE_SHEETMUSIC_DOC        = 'sheetmusic_doc'
    VALUE_SHEETMUSIC_INDEX      = "index.doc"
    VALUE_RENDER_PDF            = False
    
    ###
    #       STORED IN ONLY IN QPREFERENCES
    ###
    SETTING_DEFAULT_PATH_MUSIC_DB    = 'dbPath'
    SETTING_DEFAULT_MUSIC_FILENAME   = 'dbFile'

    ###
    #       STORED IN System or BookSettings
    ###
    SETTING_PAGE_LAYOUT        = 'layout'         ## Page layout (1/2)
    SETTING_KEEP_ASPECT        = 'aspectRatio'    ## Keep aspect ratio when resizing
    SETTING_SMART_PAGES        = 'smartPages'     ## Use alternate pages for two page displays

    ###
    #       STORED ONLY IN System table
    ###
    SETTING_DEFAULT_IMGFORMAT    = 'gsdevice'       ## Which ghostscript device will we use 
    SETTING_DEFAULT_PATH_MUSIC  = 'sheetmusicPath' ## Where is the music folder?
    SETTING_PATH_USER_SCRIPT    = 'userScriptDir'  ## Where to store user scripts?
    SETTING_PAGE_EDITOR         = 'pageEditor'     ## Page editor
    SETTING_PAGE_EDITOR_SCRIPT  = 'pageEditorScript'  ## Script for page editor
    SETTING_DEFAULT_SCRIPT      = 'script'         ## What we will run for conversion
    SETTING_DEFAULT_SCRIPT_VAR  = 'scriptvar'      ## What 'extra' variables we will run
    SETTING_FILE_PREFIX         = 'pagePrefix'     ## sheet music output prefix: e.g. "page" for "page-nnn."
    SETTING_FILE_TYPE           = 'fileType'       ## File extension (type)
    SETTING_FILE_RES            = 'resolution'     ## Output resolution
    SETTING_BOOK_DEFAULT_GENRE  = 'genre'          ## Default genre selection
    SETTING_PDF_SCRIPT          = 'pdfScript'      ## The PDF conversion script template
    SETTING_LAST_BACKUP         = 'last_backup'    ## Where we stored the last backup
    SETTING_LOGGING_ENABLED     = 'logging_enabled'## Logging enabled 1-9 are levels 0 is None.
    SETTING_VERSION             = 'version'        ## Database Version (current)
    SETTING_RENDER_PDF          = 'viewer_pdf'

    #       book settings
    SETTING_LAST_BOOK_NAME      = 'book'            ## Last book opened.
    SETTING_LAST_BOOK_REOPEN    = 'reopen'          ## Should we reopen? BOOL (text)
    SETTING_MAX_RECENT_SIZE     = 'size_booklist'   ## How many should show in 'Open Recent' file menu
    SETTING_SHOW_FILEPATH       = 'recentFilepath'
    SETTING_USE_TOML_FILE       = 'use_toml_file'   ## Read/Write toml file for configuration
    
    #       window settings
    SETTING_WIN_GEOMETRY        = 'geometry'
    SETTING_WIN_STATE           = 'state'
    SETTING_WIN_POS             = 'position'
    SETTING_WIN_SIZE            = 'size'
    SETTING_WIN_ISMAX           = 'ismaximized'
    SETTING_WIN_STATUS_ENABLED  = 'statusbar'
    SETTING_WINDOW_STATE_SAVED  = 'windowState'

    #       keyboard settings
    SETTING_PAGE_PREVIOUS       = 'previousPage'
    SETTING_PAGE_NEXT           = 'nextPage'
    SETTING_FIRST_PAGE_SHOWN    = 'pageShownFirst'
    SETTING_LAST_PAGE_SHOWN     = 'pageShownLast'
    SETTING_BOOKMARK_PREVIOUS   = 'previousBookmark'
    SETTING_BOOKMARK_NEXT       = 'nextBookmark'

    SETTING_LAST_IMPORT_DIR     = 'importDir'
    SETTING_USE_PDF_INFO        = 'useInfoPDF'
    SETTING_NAME_IMPORT         = 'useInfoName'
    VALUE_NAME_IMPORT_PDF       = 9
    VALUE_NAME_IMPORT_FILE_0    = 0           # Minimal cleanup only (bad chars)
    VALUE_NAME_IMPORT_FILE_1    = 1           # Just use filename but get rid of characters
    VALUE_NAME_IMPORT_FILE_2    = 2           # Try and tidy up the filename more

    SETTING_IMPORT_SCRIPT       = 'importScript'
    
    VALUE_DEFAULT_COMPOSER      = 'Unknown'
    VALUE_DEFAULT_GENRE         = 'Unknown'

    VALUE_PDF                   = 'pdf'
    VALUE_PNG                   = 'png'

    ###
    #       Settings for DbSettings only
    ###
    SETTING_EDIT_HISTORY        = 'history'     ## You need to store this as 'history_pagename'
    SETTING_EDIT_HISTORY_FORMAT = 'history_"{0:03d}'

    ###
    #       END DATABASE
    ###

    primaryKeys = {
        'Book':         ['book'],
        'BookSetting':  ['book_id'],
        'Composer':     ['name'],
        'Bookmark':     ['book_id'],
        'Genre':        ['name'],
    }

    ### QSETTINGS_DICT is what is stored in the QSettings system prefs
    QSETTINGS_DICT = {
            SETTING_DEFAULT_PATH_MUSIC_DB  : VALUE_DEFAULT_DIR,
            SETTING_DEFAULT_MUSIC_FILENAME : VALUE_DEFAULT_DB_FILENAME,
    }
    
    ## PREF_SYS_KEYS is what we store but user can't alter
    PREF_SYS_KEYS = [
        SETTING_WIN_GEOMETRY,
        SETTING_WIN_STATE,
        SETTING_WIN_POS,
        SETTING_WIN_SIZE,
        SETTING_WIN_ISMAX,
        SETTING_WIN_STATUS_ENABLED,
    ]


class ImportNameSetting:
    forImportName   = { "Only cleanup illegal characters from name": DbKeys.VALUE_NAME_IMPORT_FILE_0,
                        "Use filename with minimal cleanup":         DbKeys.VALUE_NAME_IMPORT_FILE_1,
                        "Use filename with maximum cleanup and Title Name":              DbKeys.VALUE_NAME_IMPORT_FILE_2}

    def __init__(self):
        try:
            import pypdf
            self.useInfoPDF = "pypdf"
            self.forImportName["Use PDF to fill in name"] = DbKeys.VALUE_NAME_IMPORT_PDF 
        except:
            self.useInfoPDF = None
            
            
class LOG :
    disabled    = 0
    debug       = 1
    info        = 2
    warning     = 3
    critical    = 4

LOGSTR = { LOG.debug: 'debug', LOG.info: 'info', LOG.warning: 'warning', LOG.critical: 'critical' }

class BOOK :
    """
    This will work for both Book and Bookview, but only the view has composer and genre and local_* fields
    """
    id              = 'id'
    name            = 'book'
    book            = 'book'
    title           = 'book'
    composer        = 'composer'
    composer_id     = 'composer_id'
    genre           = 'genre'
    genre_id        = 'genre_id'
    source          = 'source'          # Location of original
    source_type     = 'source_type'     # What type is it? png or pdf
    location        = 'location'        # Location of display material
    link            = 'link'            # optional: url link
    version         = 'version'
    author          = 'author'          # optional
    publisher       = 'publisher'       # optional
    totalPages      = 'total_pages'
    aspectRatio     = 'aspectRatio'
    lastRead        = 'last_read'
    numberStarts    = 'numbering_starts'
    numberEnds      = 'numbering_ends'
    nameDefault     = 'name_default'
    dateAdded       = 'date_added'
    dateUpdated     = 'date_updated'
    dateRead        = 'date_read'
    fileModified    = 'date_file_modified'
    fileCreated     = 'date_file_created'
    pdfCreated      = 'date_pdf_created'
    pdfModified     = 'date_pdf_modified'


        
class BOOKMARK:
    """
        Use this for either bookmarkview or bookmark
    """
    book            = 'book'        ### Book name
    book_id         = 'book_id'     ### Book ID
    id              = 'id'          ### bookmark ID
    name            = 'bookmark'    ### bookmark name
    page            = 'page'        ### bookmark starting page
    value           = 'page'        ### alias for starting page

class BOOKSETTING:
    book            = 'book'        ### Book name
    book_id         = 'book_id'     ### Book ID
    id              = 'id'          ### bookmark ID
    name            = 'bookmark'    ### setting name
    value           = 'value'       ### setting value
    dateAdded       = 'date_added'
    dateUpdated     = 'date_updated'
    localAdded      = 'local_added'
    localUpdated    = 'local_updated'
    dimensions      = 'dimensions'  ## Class pdfclass
    maxWidth        = 'max_width'   ## Unscaled size values
    maxHeight       = 'max_height'

class BOOKPROPERTY:
    """
        BookProperty are values that MAY be in the book or, if None, will be in System
    """
    layout          = 'layout'
    fileType        = 'fileType'

class NOTE:
    id       = "id"
    note     = "note"
    location = "location"
    size     = "size"
    book_id  = "book_id"
    page     = "page"
    seq      = "sequence"
    
