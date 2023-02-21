# macos_preview_200.sh
# Conversion script from PDF to PNG pages using MacOS Preview
# version 0.2
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file starts with an underscore to make it a 'system' and private shell script

trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

#:title Import PDF to Sheetmusic using MacOS Preview
#:comment This program will run the MacOS utility Preview 
#:comment to convert PDFs into one-page images.
#:comment <br/>
#:comment This may render text better than Ghostscript
#:require debug ontop
#:system  music pdf-res pdf-type pdf-device 
#:width   800
#:height  800
#:os      macos

# Dialog only runs during configuration. Key should be stored as 'unix_gs_png.sh'
#:dialog "type='title'    label='Preview conversion settings'"
#:dialog "type='drop'     label='Conversion type' tag='IMG_FORMAT'  option='include required'    value='greyscale' dropdown='color;greyscale'  "
#:dialog "type='text'     label='Resolution'      tag='IMG_RES'     option='include ro'          value='200'"
#:dialog "type='text'     label='Image Type'      tag='IMG_TYPE'    option='include ro'          value='png'"
#:dialog "type='size'     width='400'"

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi

. ${INCLUDE_SYSTEM}/start.sh "$@" 

## Make sure to pass SOURCE_FILE and TARGET_DIR as parameters. (Parsed in parameters.sh)
dir_exists  "${MUSIC_DIR}"    "Environment variable"
require_var "${IMG_FORMAT}"   "Environment variable"
file_exists "${SOURCE_FILE}" "-SOURCE_FILE Source PDF file"
require_var "${TARGET_DIR}"  "-TARGET_DIR new-music-directory"

${DEBUG} cd       "${MUSIC_DIR}"
${DEBUG} mkdir -p "${TARGET_DIR}" 

dir_exists "${TARGET_DIR}" ""

${DEBUG} cd "${TARGET_DIR}" || error_handler "Could not change to ${MUSIC_DIR}/${TARGET_DIR}" 9 __LINENO__

cat <<START_PREVIEW

==========================================================================
Read From . '${SOURCE_FILE}'
Write To . .'${MUSIC_DIR}/${TARGET_DIR}
==========================================================================

START_PREVIEW

if [ "$IMG_FORMAT" = "greyscale" ]; then
${DEBUG} automator ${INCLUDE_SYSTEM}/importpdf/automator/pdf-to-png-grey.workflow
else
${DEBUG} automator ${INCLUDE_SYSTEM}/importpdf/automator/pdf-to-png-rgb.workflow
fi

if [ -z "${DEBUG}" ]; then
cat <<END_PREVIEW

============================================
Output is in ${TARGET_DIR}
============================================

Total disk space taken:

END_PREVIEW

ls *.png | sort | xargs du -ch
fi
. ${INCLUDE_SYSTEM}/finish.sh