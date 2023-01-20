#!/bin/bash
#:usage Fill in data from optional '#:system' request: scriptrun version python qt music os
FILE_PATH=""

while (( $# ))
do
    case $1 in
    -D  )
        shift; DBFILE="$1"
        ;;
    -M  )
        shift; MUSIC_DIR="$1"
        ;;
    -S  )
        shift; SYSTEM_OS="$1"
        ;;
    -P  )
        shift; PYTHON_VERSION="$1"
        ;;
    -Q  )
        shift; QT_VERSION="$1"
        ;;
    -R  )
        shift; PYTHON_RUN="$1"
        ;;
    -v )
        shift; SHEETMUSIC_VERSION="$1"
        ;;
    -W  )
        shift;
        ;;
    -Y)
        shift; SCRIPT_RUN="$1"
        ;;
     *)  ;;
    esac
    shift
done

## This is for the BASH version of the shell

if [ "${BASH_VERSION}" != '' ]; then
    SCRIPT_PGM='bash'
    SCRIPT_RUN=$BASH
    SCRIPT_VERSION=$BASH_VERSION
else
    ## ZSH
    if [ "${ZSH_VERSION}" != '' ]; then
        SCRIPT_PGM="${ZSH_NAME}"
        SCRIPT_RUN='(not available)'
        SCRIPT_VERSION="${ZSH_VERSION}"
    else
        SCRIPT_PGM="${shell}"
        SCRIPT_RUN="(not availbe)"
        SCRIPT_VERSION="(not available)"
    fi
fi

