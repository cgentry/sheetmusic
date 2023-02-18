#!/bin/bash
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
# Licensed under GPL 3.0
#
#:title   PDF: Fix errors in document
#:comment This will take PDF files that have errors, such as bad counters,
#:comment bad metadata, possibly broken fields and try to repair it. It will
#:comment also wipe out any change locks that you have put on. It is not
#:comment guaranteed to be 100% but should correct a number of problems.
#:comment The old file will be saved with the suffix '-old.pdf'
#:dialog  "type='file' label='Select the PDF file to be repaired:' option='require' filter='PDF (*.pdf *.PDF)' width='120' tag='FILE'"
#:dialog  "type='title' label='Fix errors in PDF file'"
#:dialog  "type='size' width='600'"
#: require file debug
#: width 1024
#: heigth 920
#
#:BEGIN template.sh
## the following should work for bash and zsh.
## Standard parms passed:
##      -S system-side script include directory

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 

#:END template.sh
. ${INCLUDE_SYSTEM}/require_file.sh "$@"
. ${INCLUDE_SYSTEM}/unique_file.sh "$@"


TEMP_PATH="${FILE_PATH}-fix.pdf"
unique_file "${FILE_PATH}" "-old.pdf"


cat <<ENDDATA
INPUT FILE:   ${FILE_PATH}
TEMP FILE:    ${TEMP_PATH}
ENDDATA
UNIQUE_NAME=$(basename "${UNIQUE_FILE}")

${DEBUG} gs -o "${TEMP_PATH}" -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress "${FILE_PATH}"   || error_handler "Ghostscript error" 1 . ${LINENO}
${DEBUG} mv "${FILE_PATH}"   "${UNIQUE_FILE}"|| error_handler "Could not move ${FILE_PATH} to ${UNIQUE_FILE}"  2 . ${LINENO}
${DEBUG} mv "${TEMP_PATH}"   "${FILE_PATH}"  || error_handler "Could not move ${TEMP_PATH} to ${FILE_PATH}"    3 . ${LINENO}
cat <<END_FIX_PDF

Fixed PDF file:  '${FILE_NAME}'
Original now  :  '${UNIQUE_NAME}'
END_FIX_PDF
echo .
. ${INCLUDE_SYSTEM}/finish.sh "$@"