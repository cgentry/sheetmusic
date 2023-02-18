#:usage Dump out all env variables 
cat <<DUMP_ENV

=================================================================================
. . . . . . . . . . . . . PASSED ENVIRONMENT VARIABLES  . . . . . . . . . . . . . 
=================================================================================

DUMP_ENV
DUMP_ENV_BORDER='--------------------' 
if [ "${SHEETMUSIC_ENV}" != "" ]; then
    printf '%20s = %s\n' 'KEY' 'VALUE'
    printf '%20s = %s\n' $DUMP_ENV_BORDER $DUMP_ENV_BORDER
    for KEY in $(echo $SHEETMUSIC_ENV | tr ":" "\n" | sort )
    do
    # NOTE: Currently only ZSH compatible. needs to check
        printf '%20s = %s\n' ${KEY} ${(P)KEY}
        #echo "KEY: ${KEY}   = ${(P)KEY}"
    done
else
    set
fi
cat <<END_DUMP_ENV

END OF ENVIRONMENT LIST

END_DUMP_ENV