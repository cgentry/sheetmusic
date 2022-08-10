# sheetmusic version 0.1.5
A graphical program to display sheet music on a monitor

# Overview
The purpose of this program is to display music and allow easy navigation. It will either display 1 page, or 2 pages side-by-side. Bookmarks can be added for any page without limits. I wanted to write this because most of the programs I've tried are ok but I've wanted additional features. Since I've been coding in a variety of languages I decided to pick up Python and try my hand. 

Features:
* Navigation that you can change, e.g. up arrow or left arrow for previous page.
* Bookmarks can be added to any page and given a simple name.
* You can add page offsets that indicate both the begining of the book (after introductions) and the offset where page numbers appear.
* A built-in tool can convert PDFs into a format that the program can use.
* Always remember the last book and page and can re-open when you restart the program.

The main program is set to default to PNGs for display purposes. It can convert PDFs, using ghostscript, into separate pages. A batch conversion can be started and the program will prompt for output names as each conversion finishes. 

# Future
There are specific enhancements planned for the program.
* Provide packages for Windows / Linux and MacOS
* Allow annotation to occur directly in the program.
* Use PDFs directly.
* Include help within the program.
Other enhancements will come as I need them.

# Written in:
Python 3
Qt PySide 6

