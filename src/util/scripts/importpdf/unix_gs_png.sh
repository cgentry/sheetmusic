# unix_gs_png.sh
# Conversion script from PDF to PNG pages
# version 0.2
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file starts with an underscore to make it a 'system' and private shell script

trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

#:title Import PDF to Sheetmusic using Ghostscript
#:comment This program will run the free utility Ghostscript to read and convert PDFs 
#:comment into one-page images.
#:require debug ontop
#:system  music pdf-res pdf-type pdf-device 
#:width   800
#:height  800
#:os      macos linux bsd

# Dialog only runs during configuration. Key should be stored as 'unix_gs_png.sh'
#:dialog "type='title'    label='Ghostscript settings'"
#:dialog "type='dropdown' label='Conversion type' tag='IMG_FORMAT'  dropdown='24bit RGB Color;Grayscale' data='png16m;pnggray' value='pnggray'"
#:dialog "type='dropdown' label='Resolution'      tag='IMG_RES'     dropdown='150;200;300' value='200' "
#:dialog "type='text'     label='Options for GS'  tag='IMG_OPTIONS' value='-dSAFER -dBATCH -dNOPAUSE -dDeskew -dShowAnnots=false -dGraphicsAlphaBits=4'"
#:dialog "type='text'     label='Image Type'      tag='IMG_TYPE'    value='png'  option='ro'"

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi

. ${INCLUDE_SYSTEM}/start.sh "$@" 

## Make sure to pass SOURCE_FILE and TARGET_DIR as parameters. (Parsed in parameters.sh)
dir_exists  "${MUSIC_DIR}"   "Environment variable"
require_var "${IMG_FORMAT}"  "-G ghostscript-device"
require_var "${IMG_RES}"     "-E output-resolution"
require_var "${IMG_TYPE}"    "-I output-type"
file_exists "${SOURCE_FILE}" "-SOURCE_FILE Source PDF file"
require_var "${TARGET_DIR}"  "-TARGET_DIR new-music-directory"

${DEBUG} cd       "${MUSIC_DIR}"
${DEBUG} mkdir -p "${TARGET_DIR}" 

dir_exists "${TARGET_DIR}" ""

${DEBUG} cd "${TARGET_DIR}" || error_handler "Could not change to ${MUSIC_DIR}/${TARGET_DIR}" 9 __LINENO__

cat <<START_GHOSTSCRIPT

==========================================================================
Read From . '${SOURCE_FILE}'
Write To . .'${MUSIC_DIR}/${TARGET_DIR}
==========================================================================

START_GHOSTSCRIPT
GS_FONTPATH=/System/Library/Fonts
${DEBUG} gs -dSAFER -dBATCH -dNOPAUSE -dDeskew -dShowAnnots=false \
  -dGraphicsAlphaBits=4 \
  -r"${IMG_RES}"  \
  -sDEVICE="${IMG_FORMAT}" \
  -sOutputFile="page-%03d.${IMG_TYPE}" \
  "${SOURCE_FILE}"  || exit 9

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