#!/bin/bash
#
# Conversion script from PDF to pages
# version 0.2
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# NOTE: This is an early test and shows how to import using passed params. 
# The program has much more extensive functions.

trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

#:title Import PDF to Sheetmusic
#:comment This program will run the free utility Ghostscript to read and convert PDFs 
#:comment into one-page images.
#:require debug ontop
#:system  music pdf-res pdf-type pdf-device 
#:width   600
#:height  700

#:dialog "type='file' label='PDF File to convert' tag='SOURCE_FILE'option='require' width='120'"
#:dialog "type='dir' label='Select directory for conversion' option='require' width='120' tag='TARGET_DIR'"
#:dialog "type='title' label='Import PDF to system'"
#:dialog "type='size' width='600'"


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

## Roll-you-own getopts. Not as efficient but it always ignores errors (which some versions don't)
## options:
##  -s source file      - var   $SOURCE_FILE
##  -t target directory - var   $TARGET_DIR (name only)


while (( $# ))
do
    case $1 in
    -s  )
        shift; SOURCE_FILE="$1"
        ;;
    -t )
        shift; TARGET_DIR="$1"
        ;;
     *)  ;;
    esac
    shift
done

dir_exists  "${MUSIC_DIR}"   "-M directory"
require_var "${PDF_DEVICE}"  "-G ghostscript-device"
require_var "${IMG_RES}"     "-E output-resolution"
require_var "${IMG_TYPE}"    "-I output-type"
file_exists "${SOURCE_FILE}" "-s Source PDF file"
require_var "${TARGET_DIR}"  "-t new-music-directory"

${DEBUG} cd       "${MUSIC_DIR}"
${DEBUG} mkdir -p "${TARGET_DIR}"

${DEBUG} gs -dSAFER -dBATCH -dNOPAUSE -dDeskew \
  -r"${IMG_RES}"  \
  -sDEVICE="${PDF_DEVICE}" \
  -sOutputFile="${TARGET_DIR}/page-%03d.${IMG_TYPE}" "${SOURCE_FILE}"  || exit 9

cd "${TARGET_DIR}"
if [ -z "${DEBUG}" ]; then
cat <<END_GHOSTSCRIPT

============================================
Output is in ${TARGET_DIR}
============================================

Total disk space taken:

END_GHOSTSCRIPT
ls *.${IMG_TYPE} | sort | xargs du -ch
fi
. ${INCLUDE_SYSTEM}/finish.sh