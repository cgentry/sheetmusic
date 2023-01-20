#!/bin/bash
#
#:usage Take a file path and suffix and put a counter in between.
# example:
#   unique_file my_file '.txt'
# It will return one of:
#   my_file.txt
#   my_file-01.txt
# Set UNIQUE_MAX to the maximum number you want to try.

if [ -z "$UNIQUE_MAX"  ]; then
    UNIQUE_MAX=10
fi
unique_file() {
    TARGET_FILE_PFX_UNIQUE=$1
    TARGET_FILE_EXT_UNIQUE=$2
    UNIQUE_FILE="${TARGET_FILE_PFX_UNIQUE}${TARGET_FILE_EXT_UNIQUE}"
    if [ ! -f "${UNIQUE_FILE}" ]; then
        return 0
    fi
    for i in $(seq -f %02g 1 ${UNIQUE_MAX}) ; 
    do
        UNIQUE_FILE="${TARGET_FILE_PFX_UNIQUE}-${i}${TARGET_FILE_EXT_UNIQUE}"
        if [ ! -f "${UNIQUE_FILE}" ]; then
            return 0
        fi
    done
    error_handler "Unique file for '${TARGET_FILE_PFX_UNIQUE}' not found (max #${UNIQUE_MAX}" 15 'unique_file.sh' ${LINENO}
}
