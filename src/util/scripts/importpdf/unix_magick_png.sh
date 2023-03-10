# unix_magick_png.sh
# Conversion script from PDF to PNG pages
# version 0.2
#
# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
#
# This file starts with an underscore to make it a 'system' and private shell script

trap EndScript SIGHUP SIGINT SIGQUIT SIGABRT SIGKILL

#:title Import PDF to Sheetmusic using Imagemagic
#:comment This program will run the free utility Imagick 
#:comment to read and convert PDFs into one-page images.
#:comment You can install Imagemagic using homebrew:
#:comment brew install imagemagick
#:require debug ontop
#:system  music pdf-res pdf-type pdf-device 
#:width   800
#:height  800
#:os      macos linux bsd

# Dialog only runs during configuration. Key should be stored as 'unix_magick_png.sh'
#:dialog "type='title'    label='ImageMagick Convert settings'"
#:dialog "type='drop'     label='Conversion type' tag='IMG_FORMAT'  option='include' dropdown='RGB Color;Grayscale' data='RGB;Gray' value='Gray'"
#:dialog "type='drop'     label='Resolution'      tag='IMG_RES'     option='include' dropdown='150;200;300;600' value='150'"
#:dialog "type='text'     label='Options for GS'  tag='IMG_OPTIONS' option='include ro' value='-quality 100 '"
#: dialog "type='text'     label='Image Type'      tag='IMG_TYPE'    option='include' value='png'  option='-quality 100 -antialias'"
#:dialog "type='text'     label='ScriptName'      tag='IMG_SCRIPT'  option='include ro' value='unix_magick_png.sh' "
#:dialog "type='size'     width='1024'"

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
OUTPUT_FILE=page-%03d.png

dir_exists "${TARGET_DIR}" ""

${DEBUG} cd "${TARGET_DIR}" || error_handler "Could not change to ${MUSIC_DIR}/${TARGET_DIR}" 9 __LINENO__

cat <<START_HEADER

==========================================================================
Read From . '${SOURCE_FILE}'
Write To . .'${MUSIC_DIR}/${TARGET_DIR}
Colorspace . ${IMG_FORMAT}   Resolution . . ${IMG_RES}
==========================================================================

START_HEADER

convert  \
  -verbose \
  -density "${IMG_RES}"  \
  -antialias \
  "${SOURCE_FILE}" \
  -resize 2048x \
  -quality 100 \
  -colorspace Gray \
  -depth 8 \
  "${OUTPUT_FILE}"

if [ -z "${DEBUG}" ]; then
cat <<END_MSG

============================================
Output is in ${TARGET_DIR}
============================================

Total disk space taken:

END_MSG

ls *.${IMG_TYPE} | sort | xargs du -ch
fi
. ${INCLUDE_SYSTEM}/finish.sh