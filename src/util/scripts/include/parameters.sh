#!/bin/bash
#:usage Sets all named parameters passed to script
# Option -S should be handled in main script

FILE_PATH=""
IMG_RES=300
args=( "$@" )
while (( ${#args[@]} ))
do
    OPT=${args[0]}
    ARG="${args[@]:1:1}"
    case ${OPT} in
    -D  )
        DBFILE=${ARG};  
        args=("${args[@]:2}")
        ;;
    -E  )
        IMG_RES=${ARG};  
        args=("${args[@]:2}")
        ;;
    -G )
        PDF_DEVICE=${ARG};  
        args=("${args[@]:2}")
        ;;
    -I  )
        IMG_TYPE=${ARG};  
        args=("${args[@]:2}")
        ;;
    -M  )
        MUSIC_DIR=${ARG};  
        args=("${args[@]:2}")
        ;;
    -O  )
        SYSTEM_OS=${ARG};  
        args=("${args[@]:2}")
        ;;
    -P  )
        PYTHON_VERSION=${ARG};  
        args=("${args[@]:2}")
        ;;
    -Q  )
        QT_VERSION=${ARG};  
        args=("${args[@]:2}")
        ;;
    -R  )
        PYTHON_RUN=${ARG};  
        args=("${args[@]:2}")
        ;;
    -S ) # HANDLE IN MAIN: INCLUDE_SYSTEM="${args[@]:1:1}
        args=("${args[@]:2}")
        ;;
    -U )
        INCLUDE_USER=${ARG}
        SCRIPT_USER=`dirname ${INCLUDE_USER}`
        args=("${args[@]:2}")
        ;;
    -v )
        SHEETMUSIC_VERSION=${ARG};  
        args=("${args[@]:2}")
        ;;
    -W  )
        ;;

    -X ) 
        DEBUG="echo DEBUG: " 
        args=("${args[@]:1}")
        ;;

    -Y)
        SCRIPT_RUN=${ARG};  
        args=("${args[@]:2}")
        ;;

    -*) # Set the NAME to the ARG
        declare ${OPT:1}=${ARG}
        args=("${args[@]:2}")
        ;;
    *) 
        args=("${args[@]:1}")
        ;;
    esac
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

