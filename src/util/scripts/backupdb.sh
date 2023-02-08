# (c) 2023 Charles Gentry
# Part of SheetMusic system.
#
#:title   Database: Make a backup
#:comment This will make a backup of the key database file used by sheetmusic.
#:comment The backup will be called 'sheetmusic-backup' and will have the
#:comment extension of '.bak'.

#:dialog  "type='dir' label='Select directory for backup' option='require' width='120' tag='BDIR'"
#:dialog  "type='title' label='Backup Sheetmusic database'"
#:dialog  "type='size' width='600'"
#:system  dbfile
#:require debug

#
#:BEGIN template.sh
## the following should work for bash and zsh.
## Standard parms passed:
##      -S system-side script include directory
args=( "$@" )
while (( ${#args[@]} ))
do
    if [ "${args[0]}" == '-S' ]; then
        INCLUDE_SYSTEM="${args[@]:1:1}"
        break
    fi
    args=("${args[@]:1}")
done

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 

#:END template.sh
. ${SCRIPT_DIR}/include/unique_file.sh "$@"

BACKUP_DIR=${BDIR}
BACKUP_FILE='sheetmusic-backup'
BACKUP_EXT='.bak'
BACKUP="${BDIR}/${BACKUP_FILE}"

file_exists "${DBFILE}"     "DBFILE"
dir_exists  "${BACKUP_DIR}" "BDIR"
unique_file "${BACKUP}"     "${BACKUP_EXT}"
PARM=".backup '"${UNIQUE_FILE}"'"

sqlite3 "${DBFILE}" "${PARM}"

if [ ! -e ${UNIQUE_FILE} ]; then
    error_handler "Backup file was not created: ${UNIQUE_FILE}" 11 $0 $LINENO
fi

cat <<END_BACKUP

Database file: ${DBFILE}
Backup:        ${UNIQUE_FILE}


END_BACKUP


. ${INCLUDE_SYSTEM}/finish.sh