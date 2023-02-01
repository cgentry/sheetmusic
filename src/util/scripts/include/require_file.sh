# require input
#:usage Ensure filename has been passed if required. Sets FILE_NAME and FILE_DIR
# SETS:
#   FILE_PATH - File dir + name
#   FILE_NAME - File name only
#   FILE_DIR  - File directory only
#
#   INPUT TAGS can be: -f (simple) -FILE (longer) or -FILE_1 (autogen from simplescript)

FILE_PATH=""

while (( $# ))
do
    case $1 in
    -f  )
        shift
        FILE_PATH="$1"
        break
        ;;
    -FILE)
        shift; FILE_PATH="$1"
        ;;
    -FILE_1)
        shift; FILE_PATH="$1"
        ;;    
     *)  ;;
    esac
    shift
done

if [ "${FILE_PATH}" = "" ]; then
    error_handler "File name must be passed" 10 'require_file.sh' ${LINENO}
fi

if [ ! -f "${FILE_PATH}" ]; then
    error_handler "File '${FILE_PATH}' does not exist" 11 'require_file.sh' ${LINENO}
fi
FILE_NAME=$(basename "${FILE_PATH}")
FILE_DIR=$(dirname   "${FILE_PATH}")

if [ "${DEBUG}" != "" ]; then
cat <<FILE_PATH_DEBUG
Input verified:
     FILE: ${FILE_PATH}
     NAME: ${FILE_NAME}

FILE_PATH_DEBUG
fi