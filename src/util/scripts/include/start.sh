# standard.sh
#:usage Always include at the begining of the script. Creates error_handler

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

END_ERROR_TEXT
    exit $2
}