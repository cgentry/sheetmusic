#!/bin/bash
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
# Licensed under GPL 3.0
#
#:title   Database: Cleanup and compress
#:comment This will compact the database, if possible.
#:system  dbfile
#:require noframe ontop simple
#:width 1024
#:heigth 920

#:BEGIN template.sh
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

#:END template.sh
file_exists "${DBFILE}"     "DBFILE"
file_size ${DBFILE}
OLD_SIZE=${FSIZE}
sqlite3 "${DBFILE}" 'VACUUM;'

file_size ${DBFILE}
NEW_SIZE=${FSIZE}
cat <<END_STATS
   
-------------------------------
      Database compacted.
-------------------------------
OLD SIZE: ${OLD_SIZE}
NEW SIZE: ${NEW_SIZE} 
   
.
END_STATS