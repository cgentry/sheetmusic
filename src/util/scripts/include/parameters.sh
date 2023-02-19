#:usage Sets all named parameters passed to script
#runscript will now set some variables in the environment.

# N.B. : This is included by 'start.sh' and doesn't need include in your script.

FILE_PATH=""
IMG_RES=300
DEBUG=""
args=( "$@" )
while (( ${#args[@]} ))
do
    OPT=${args[@]:0:1}
    ARG=${args[@]:1:1}
    case ${OPT} in
    -X)
        DEBUG='echo DEBUG: '
        args=("${args[@]:1}")
        ;;

    -*) # Set the NAME to the ARG
        # This handles "-tags" for you. 
        declare ${OPT:1}="${ARG}"
        args=("${args[@]:2}")
        ;;
    *) 
        args=("${args[@]:1}")
        ;;
    esac
done

## This is for the BASH version of the shell
SCRIPT_PGM="${SHELL}"
SCRIPT_RUN="(not available)"
SCRIPT_VERSION="(not available)"
if [ "${BASH_VERSION}" != '' ]; then
    SCRIPT_PGM='bash'
    SCRIPT_RUN=$BASH
    SCRIPT_VERSION=$BASH_VERSION
else
    ## ZSH
    if [ "${ZSH_VERSION}" != '' ]; then
        SCRIPT_PGM="${ZSH_NAME}"
        SCRIPT_RUN=${SHELL}
        SCRIPT_VERSION="${ZSH_VERSION}"
    fi
fi

