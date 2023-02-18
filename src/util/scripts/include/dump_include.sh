#:usage Dump out include file information
cat <<DUMP_INCLUDE_FILES
=================================================================================
. . . . . . . . . . . . . . INCLUDE FILE INFORMATION . . . . . . . . . . . . . . 
=================================================================================


DUMP_INCLUDE_FILES

INCLUDE_USAGE=$(SEDCMD="s|^${INCLUDE_SYSTEM}/||g"; \
    grep -r '#:usage ' "${INCLUDE_SYSTEM}" | sort | sed -e 's/:#:usage/ . . . . Usage:/g' -e "${SEDCMD}" -e 's|$||g')

echo $INCLUDE_USAGE

cat <<END_DUMP_PARMS

See the help file for more information about scripting syntax.

END_DUMP_PARMS