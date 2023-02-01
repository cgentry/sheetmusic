#!/bin/bash
#
# Conversion script from PDF to pages
# version 0.2
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

EndScript()
{
    echo "Conversion ending."
}
#:title Import PDF to Sheetmusic
#:comment This program will run the free utility Ghostscript to read and convert PDFs 
#:comment into one-page images.
#:require debug
#:system  music pdf-res pdf-type pdf-device
#:width   600
#:height  700
#:require ontop

SCRIPT_DIR=`cd $(dirname $0) && pwd`
SCRIPT=$(basename $0)
INCLUDE_SYSTEM="${SCRIPT_DIR}/include"

DOES_NOT_EXIST="does not exist. Quiting import process."

. ${INCLUDE_SYSTEM}/start.sh "$@"
. ${INCLUDE_SYSTEM}/debug.sh "$@"
. ${INCLUDE_SYSTEM}/info.sh  "$@"

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