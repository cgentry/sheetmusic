#!/bin/bash
# This file is part of SheetMusic
# Copyright: 2022 by Chrles Gentry
# Licensed under GPL 3.0
#
#:title   Scripting File Information
#:comment This will provide information about scripts and the environment they run in.
#:system  music os python pythonrun qt scriptrun version
#:require noframe ontop simple
#:width 1024
#:heigth 920

## the following should work for bash and zsh.
## if not, use the -Z option
SCRIPT_DIR=`cd $(dirname $0) && pwd`
SCRIPT=$(basename $0)
INCLUDE_DIR="${SCRIPT_DIR}/include"

usage(){
    cat <<ENDUSAGE
$0 : Fix PDF files by running them through ghostscript
ENDUSAGE
}

. ${INCLUDE_DIR}/start.sh "$@"
. ${INCLUDE_DIR}/debug.sh "$@"
. ${INCLUDE_DIR}/info.sh  "$@"

INCLUDE_USAGE=$(SEDCMD="s|^${INCLUDE_DIR}/||g"
echo "<code>"
grep -r '#:usage ' "${INCLUDE_DIR}" | sort | sed -e 's/:#:usage/ . . . . Usage:/g' -e "${SEDCMD}" -e 's|$||g')

cat <<END_SCRIPTING_INFO
<pre>
=================================================================================
. . . . . . . . . . . . . . . SCRIPTING INFORMATION . . . . . . . . . . . . . . . 
==================================================================================
Scripts are held in the directory . ${SCRIPT_DIR}
Include scripts are in directory  . ${INCLUDE_DIR}
Scripting program . . . . . . . . . ${SCRIPT_PGM}    VERSION: ${SCRIPT_VERSION}
Scripting exected by  . . . . . . . ${SCRIPT_RUN}
QT Version . . . . . . . . . . . .  ${QT_VERSION}
Python version . . . . . . . . . .  ${PYTHON_VERSION}
Python program . . . . . . . . . .  ${PYTHON_RUN}

System OS . . . . . . . . . . . . . ${SYSTEM_OS}
Sheetmusic Version  . . . . . . . . ${SHEETMUSIC_VERSION}
Music stored in directory . . . . . ${MUSIC_DIR}
=================================================================================
. . . . . . . . . . . . . . INCLUDE FILE INFORMATION . . . . . . . . . . . . . . 
==================================================================================

$INCLUDE_USAGE

=================================================================================
. . . . . . . . . . . . . . INCLUDE FILE INFORMATION . . . . . . . . . . . . . . 
==================================================================================
The scripts can contain a number of directives that the program will follow. Most tags are optional.
ALL TAGS MUST BEGIN WITH #:
Used to control the dialog
    comment . . . Any number of comment lines may appear and will be displayed when the user
                  is prompted to run the script.
    title . . . . Script title.
    dir-prompt .  Request for a directory. This will be the title used for the opener. *NOTE
                  Not passed to the script.
    file-prompt . Request for a file that exists in the system. This will be the title used. *Note
                  The file name is returned wih the flag -f filename
    file-filter . Filter file by criteria. An example for PDF files: '(*.pdf *.PDF)'
    require . . . What input is required. Currently only 'file' and 'dir' are used.
                  If you don't have any requirements, the program will run without a file or dir.
    height . . .  How high do you want the window to be?
    width . . . . How wide do you want the window to be.
    system . . .  used to request information about the system. All tags must be on one line.
             After the tag the following can appear:
            (Values will be set by including info.sh )
             dbfile     - The full path to where the database is located
                          Passed as -D path and set DBFILE
             music      - the full directory path to where music is stored
                          Passed as -M path and set MUSIC_DIR
             os         - The operating system identifier
                          Passed as -S and set SYSTEM_OS
             python     - The python version
                          Passed as -P and set PYTHON_VERSION
             pythonrun  - The location of the python interpreter
                          Passed as -R and set PYTHON_RUN
             qt         - Current version number of QT
                          Passed as -Q and set QT_VERSION
             scriptrun  - The script command

    NOTE: MacOS does not allow the file opening dialog to have a title. Instead, a small window will appear
    in the upper left hand corner of the screen to let you know what is happening.

<b>These are used to pass information to the program</b>
    -d dirname      In response to 'dir-prompt'
    -f filename     In response to 'file-prompt'
    -M musicdir     In response to 'system music'
    -P python ver   In response to 'system python'
    -Q QT Version   In response to 'system qt'
    -R python loc   In response to 'system python'
    -S os-info      In response to 'system os'
    -X              Set when debug is required
    -Y Shell script In response to 'system scriptrun'
    -Z script path  Always sent
    

</pre>
END_SCRIPTING_INFO