# standard.sh
#:usage Always include at the begining of the script.

set -Ee

error_handler(){
# $1 - Error text
# $2 - Exit code
# $3 - Script (sub)
# $4 - Line number
    cat <<END_ERROR_TEXT
Fatal Error:
    Error:  $1
    Script: ${SCRIPT}
    File:   $(basename $3)
    Line:   $4

.    
END_ERROR_TEXT

echo "Terminating script."
echo "."
    exit $2
}

require_var(){
# Simple check for an empty variable
# require_var "{{VAR}}" "-v var"    
    if [ -z "$1" ]; then
        echo "Variable not passed with ${2}" >&2
        exit 10
    fi
}

dir_exists(){
#   check_dir "{{VAR}}" "VAR"
    require_var "$1" "$2"
    if [ ! -d "$1" ]; then
        echo "Directory ${1} does not exist." >&2
        exit 1
    fi
}

file_exists(){
    require_var "$1" "$2"
    if [ ! -e "$1" ]; then
        echo "File $1 does not exist." >&2
        exit 2
    fi
    if [ ! -r "$1" ]; then
        echo "File ${1} is not readable." >&2
        exit 3
    fi
}

file_size(){
    # first parm is file to size.
    FSIZE=`${PYTHON} -c 'import os;import sys;print("{:,}".format(os.path.getsize(sys.argv[1])));'  "${1}"`
}

## Get THIS script directory and THIS include directory
## Note that SCRIPT_USER and INCLUDE_USER are set using -U option
SCRIPT_DIR=`dirname $0`
INCLUDE_DIR="${SCRIPT_DIR}/include"
if [ ! -e  £{INCLUDE_DIR} ]; then
    INCLUDE_DIR=${INCLUDE_SYSTEM}
fi
SCRIPT_SYSTEM=`dirname ${INCLUDE_SYSTEM}`

. ${INCLUDE_SYSTEM}/parameters.sh "$@"
. ${INCLUDE_SYSTEM}/debug.sh     "$@" 

PYTHON="echo Can't find program 'python': "
for python_try in python3 python; do
    if  [ -x "$(command -v ${python_try})" ]; then
        PYTHON=${python_try}
        break
    fi
done
