#
#:title MacOS Preview page editor
#:os macos
# Edit the page in the system utility Preview. This loads up and waits for preview to end.
# requires parm PAGE to be set
args=( "$@" )
while (( ${#args[@]} ))
do
    OPT=${args[@]:0:1}
    ARG=${args[@]:1:1}
    case ${OPT} in
        -PAGE)
            PAGE="${args[@]:1:1}"
            SINGLE=$(basename ${PAGE})
            args=("${args[@]:2}")
        ;;
        -BOOK)
            BOOK="${args[@]:1:1}"
            args=("${args[@]:2}")
        ;;
        -TITLE)
            TITLE="${args[@]:1:1}"
            args=("${args[@]:2}")
        ;;
        *) 
        args=("${args[@]:1}")
        ;;
    esac
done

if [ ! -e "${PAGE}" ]; then
    echo "${BOOK} Page ${SINGLE} does not exist." >&2
    exit 9
fi
open -n -W -a Preview "${PAGE}"