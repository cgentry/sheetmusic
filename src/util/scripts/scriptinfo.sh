#!/bin/bash
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
# Licensed under GPL 3.0
#
#:title   ~ Information for scripting
#:comment This will provide information about scripts and the environment they run in.
#:system  music os python pythonrun qt scriptrun version userscripts
#:require noframe ontop simple
#:width 1024
#:heigth 920

#:BEGIN template.sh
## the following should work for bash and zsh.Scripting exected by
## Standard parms passed:
##      -S system-side script include directory

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 

#:END template.sh
echo "<pre>"
cat <<END_SCRIPTING_INFO
=================================================================================
. . . . . . . . . . . . . . . SCRIPTING INFORMATION . . . . . . . . . . . . . . . 
=================================================================================
User Scripts are in .   (SCRIPT_USER) . . ${SCRIPT_USER}   
User Includes are in    (INCLUDE_USER). . ${INCLUDE_USER}  
System Scripts are in . (SCRIPT_SYSTEM) . ${SCRIPT_SYSTEM}
System Includes are in  (INCLUDE_SYSTEM). ${INCLUDE_SYSTEM}
Music stored in . . . . (MUSIC_DIR)  . .  ${MUSIC_DIR}

Python program . . . .  (PYTHON_RUN) . .  ${PYTHON_RUN}
Python version . . . . .(PYTHON_VERSION)  ${PYTHON_VERSION}

Scripting program . . . (SCRIPT_PGM) . .  ${SCRIPT_PGM}    VERSION: ${SCRIPT_VERSION}
Scripting executed by . (SCRIPT_RUN). . . ${SCRIPT_RUN}

QT Version . . . . . . .(QT_VERSION) . .  ${QT_VERSION}
System OS  . . . . . . .(SYSTEM_OS)  . .  ${SYSTEM_OS}
System Class . . . . .  (SYSTEM_CLASS) .  ${SYSTEM_CLASS}

Sheetmusic Version . . . . . . . . . . .  ${SHEETMUSIC_VERSION}

N.B.: Also set are: 
    SCRIPT_DIR,  current script's directory 
    INCLUDE_DIR, current script's include directory
    
END_SCRIPTING_INFO
. ${INCLUDE_SYSTEM}/dump_include.sh
. ${INCLUDE_SYSTEM}/dump_env.sh
. ${INCLUDE_SYSTEM}/dump_parms.sh

echo "</pre>"

. ${INCLUDE_SYSTEM}/finish.sh