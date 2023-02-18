#:usage Dump out all variables passed in a tidy form. Use for debugging
cat <<DUMP_PARMS

=================================================================================
. . . . . . . . . . . . . . . . PASSED PARAMETERS . . . . . . . . . . . . . . . . 
=================================================================================


DUMP_PARMS

args=( "$@" )
while (( ${#args[@]} ))
do
    OPT=${args[@]:0:1}
    ARG=${args[@]:1:1}
    if [ "${OPT:0:1}" = '-' ]; then
        if [ "${OPT}" = '-X' ]; then
            echo "${OPT} [debug mode]"
        else
            echo "${OPT}" "${ARG}"
            args=("${args[@]:1}")
        fi
    else
        echo "${OPT}"
    fi
    args=("${args[@]:1}")
done
cat <<END_DUMP_PARMS

END OF PARAMETER LIST

END_DUMP_PARMS