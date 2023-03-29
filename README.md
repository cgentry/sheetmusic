# sheetmusic version 0.6.02
A graphical program to display sheet music on a monitor

WARNING: 0.6.x may be unstable. 

# Overview
The purpose of this program is to display music and allow easy navigation. It will either display 1 page, or 2 pages side-by-side. Bookmarks can be added for any page without limits. I wanted to write this because most of the programs I've tried are ok but I've wanted additional features. Since I've been coding in a variety of languages I decided to pick up Python and try my hand.

Features:
* Navigation that you can change, e.g. up arrow or left arrow for previous page.
* Bookmarks can be added to any page and given a simple name.
* You can add page offsets that indicate both the begining of the book (after introductions) and the offset where page numbers appear.
* A built-in tool can convert PDFs into a format that the program can use.
* Always remember the last book and page and can re-open when you restart the program.

The main program is set to default to PNGs for display purposes. It can convert PDFs, using ghostscript, into separate pages. A batch conversion can be started and the program will prompt for output names as each conversion finishes.

# 0.6.02 [unstable]
Yet more bug fixes in PDF display and tighten up some of the sloppy code. This commit
has a ton of debug statements and is just a commit to ensure it doesn't get lost.

# 0.6.01 [unstable]
Started adding in support for direct PDF displays. this is a very unstable branch.

# 0.5.18 (unstable)
Overhauled how we do imports to get ready for PDF links. This is a major change
from 0.5.18. Added mixins, tests, split code, started to add PDF import funcions.

# 0.5.18
Fixd more bugs. Cleanup some tests which were screwed up.
* added in an import of images in a directory that have been scanned.
  This lets you run a scanner for hi-res PNG directly into a directory
  rather than a PDF and then output the stored images.
* Added an import into library function for the images.
  Can now copy the images from the PNG-scanned directory into the
  sheetmusic directory. Just a consolidation feature
* Started a 'check consistancy' function for making sure DB
  is correct. Not yet finished.

# 0.5.17
Version should be more stable and less prone to falling over.
Need to continue finding/fixing bugs.
* Many bug fixes: Bookmark, Book properties, Notes, Reopen, Refresh
* Add in preference for using/hiding filenames on 'Recent file' list
* Internal fixes for code to continue making it more compliant
* General cleanup

# 0.5.16 (unstable)
* Fix book property name changes
* Fix default page layout property

# 0.5.15 (unstable)
* Reorg the Bookmarks and move to their own menu
* Fix bug in bookmark functions
* More cleanup of naming convention

# 0.5.14 (unstable)
* Tied in OS-specific feature for import
* Removed import setup from Preferences and moved to 'File' menu
* Begun creating multiple import options. Found that the 'Preview' option does produce better images ... sometimes.
* Allows selection of import options per-import


# 0.5.13 (unstable)
* Making major changes to how we run PDF imports: having different scripts for differnt systems
* Adding script filters for OS systems
* started altering how we store import settings. Won't be finished for at least one more version
  
# 0.5.12
* Change the way scripts are invoked. Now most parms are set in the environment rather than as CLI options.
* Bug cleanup
* Update scripts and infor script for ENV vars.
* Allow scripts to be killed rather than letting them just run.
* change the way buttons are used when scripts are run.
* More code cleanup
* Still a bit unstable. Certainly ALPHA status

# 0.5.11
* Move PDF functions to util/pdfinfo.py. Allows using either pypdf or pypdf2 for scanning
  - This can also be enhanced in the future to support other libraries.
* Add in ability to run page editor using external scripts:
  - add in 'RunSilentRunDeep' to have non-interactive scripts
  - add in scripts for gimp and Preview (macos) under util;scripts;pageedit
  - start new script tag (#:os) for OS specific scripts (not yet implemented)
  - alter util/toollist.py to check any directory
  - add in preference setting for new page editor function
* Start change of code for PageLabelWidget to try and enhance resolution
  - Split some code off from PageLabelWidget
  - Start moving pixmap functions out of qdil/book into PagelabelWidget
* More code cleanup
* Still a bit unstable.


# 0.5.10
* Fix scripting error and do some testing with zsh (aim for compat with bash)
* some code cleanup

# 0.5.9
* Fix bug in simpledialog for filenames
* remove some debug print statements
* bit more code cleanup

# 0.5.8
* Fix page flipping so it runs a bit more logically.

# 0.5.7
* Fixed import of documents
* Still noticed page flipping isn't working correctly.

# 0.5.6
* Fixed page numbering.
* Added in tool tip
TODO:
* Using UTF8 special characters for notes, vertical bars, etc. Add in override capability.

# 0.5.5
* Added in notes for pages
* Fixed spacing and display of notes in status bar
* Add more shortcut keys
* Changed 'Book page' to 'Book' and always show absolute page number in left statusbar
BUGS:
* Noticed broken page numbering in status.

# 0.5.4
* Fix Preferences (broken references)
* Add in make.sh to build a Mac application. this does not sign it so only local build/run happens.
* Start work on having build for LINUX. It currently doesn't work.
* More bug fixes.

# 0.5.3
* Bug cleaning: fix windows size restore, fix scripting includes, add more documentation

# 0.5.2:
Major changes:
* Revised how scripts are run.
* Making more scripts for previous coded functions: check PDF and backup.
* Major cleanup on number of modules
* Started making it conform to Python naming convention rather than mixing styles
* Cleanup sections of old code
TODO:
* Finish cleanup of names
* remove obsolete code that has been moved to scripts
* Cleanup code and review - again.
* Make 'build' versions to run on LINUX and MacOS (all testing currently on MacOS)
* Add page notes

# 0.4.2:
Major changes:
* Altered import to use script instead of hard code
* Added ability to display simple message pane
* Added scripts to display new information
Fix:
* Fix problem wihen original source is moved
* Page change functions now working
* Numerous small fixes

Todo:
* General fixes for bugs

# 0.4.0:
Major changes made:
* Added 3 pages for both side-by-side and stacked
* Added 'script runner' becasue I got tired of coding tools.
	script runner finds and loads scripts without a lot of coding
	Written, currently, for unix-based systems. Tested on MacOS and will test on Linux
* Added script to fix messed up PDF files using ghostscript.
* fixed numerous bugs
NEW BUGS:
Current program flips pages incorrectly or pages don't display. Broken when page 3 support added.
TO DO:
Fix page bug
Add page note ability
Add more tool scripts

# 0.3.6:
* Added in notes, then tore it all apart. Fickle me.
* Notes have been moved to separate table
* Save note locations and size (to restore pages)
* Setup for notes on a page basis, not just for book
* fix some of the broken tests
* fix a bug in the qdb/utils
* Add in icon in status bar for notes.
  
# 0.2.5:
* Help is now included
* Restructure into src/build/dis directories
* Restructure and cleanup main view code
* Rip out a lot of useless stuff that is 'lingering'
* add in page widget to handle pages
* add in stacked view
* starting to add in 'notes' for book
  
# Future
There are specific enhancements planned for the program.
* Provide packages for Windows / Linux and MacOS
* Allow annotation to occur directly in the program.
* Use PDFs directly.
* update help within the program.
  
Other enhancements will come as I need them.

# Written in:
Python 3
Qt PySide 6

