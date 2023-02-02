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

## the following should work for bash and zsh.
## Standard parms passed:
##      -S system-side script include directory
args=( "$@" )
while (( ${#args[@]} ))
do
    if [ "${args[0]}" == '-S' ]; then
        INCLUDE_SYSTEM="${args[@]:1:1}"
        break
    fi
    args=("${args[@]:1}")
done

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 
INCLUDE_USAGE=$(SEDCMD="s|^${INCLUDE_SYSTEM}/||g"; \
    echo "<code>" ; \
    grep -r '#:usage ' "${INCLUDE_SYSTEM}" | sort | sed -e 's/:#:usage/ . . . . Usage:/g' -e "${SEDCMD}" -e 's|$||g')


cat <<END_SCRIPTING_INFO
<pre>
=================================================================================
. . . . . . . . . . . . . . . SCRIPTING INFORMATION . . . . . . . . . . . . . . . 
==================================================================================
User Scripts are in .   (SCRIPT_USER) . . ${SCRIPT_USER}   
User Includes are in    (INCLUDE_USER). . ${INCLUDE_USER}  
System Scripts are in . (SCRIPT_SYSTEM) . ${SCRIPT_SYSTEM}
System Includes are in  (INCLUDE_SYSTEM). ${INCLUDE_SYSTEM}
Scripting program . . . . . . . . . . . . ${SCRIPT_PGM}    VERSION: ${SCRIPT_VERSION}
Scripting exected by  . . . . . . . . . . ${SCRIPT_RUN}
QT Version . . . . . . . . . . . . . . .  ${QT_VERSION}
Python version . . . . . . . . . . . . .  ${PYTHON_VERSION}
Python program . . . . . . . . . . . . .  ${PYTHON_RUN}

System OS  . . . . . . . . . . . . . . .  ${SYSTEM_OS}
Sheetmusic Version . . . . . . . . . . .  ${SHEETMUSIC_VERSION}
Music stored in directory  . . . . . . .  ${MUSIC_DIR}

N.B.: Also set are: 
    SCRIPT_DIR,  current script's directory 
    INCLUDE_DIR, current script's include directory
=================================================================================
. . . . . . . . . . . . . . INCLUDE FILE INFORMATION . . . . . . . . . . . . . . 
==================================================================================

$INCLUDE_USAGE

See the help file for more information about scripting syntax.
</pre>

END_SCRIPTING_INFO

. ${INCLUDE_SYSTEM}/finish.sh