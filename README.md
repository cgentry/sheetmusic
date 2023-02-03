# sheetmusic version 0.5.4
A graphical program to display sheet music on a monitor

WARNING: 0.5.4 may be very unstable. a large number of structural changes have been made which should be corrected in 0.5.3

# Overview
The purpose of this program is to display music and allow easy navigation. It will either display 1 page, or 2 pages side-by-side. Bookmarks can be added for any page without limits. I wanted to write this because most of the programs I've tried are ok but I've wanted additional features. Since I've been coding in a variety of languages I decided to pick up Python and try my hand. 

Features:
* Navigation that you can change, e.g. up arrow or left arrow for previous page.
* Bookmarks can be added to any page and given a simple name.
* You can add page offsets that indicate both the begining of the book (after introductions) and the offset where page numbers appear.
* A built-in tool can convert PDFs into a format that the program can use.
* Always remember the last book and page and can re-open when you restart the program.

The main program is set to default to PNGs for display purposes. It can convert PDFs, using ghostscript, into separate pages. A batch conversion can be started and the program will prompt for output names as each conversion finishes. 

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

