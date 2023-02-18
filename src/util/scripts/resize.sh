# (c) 2023 Charles Gentry
# Part of SheetMusic system.
#
#:os macos
#:title   Resize all pages
#:comment This will find the largest width and height within a PICKER that 
#:comment has been converted and will make them all the same size.

#:picker  label='Select the PICKER to resize'
#:require debug


if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 

#:END template.sh

if [ ! -e "${PICKER}" ]; then
	echo "ERROR: no book selected."
fi

ARC=resample-archive.gzip
DIR_RESIZE=resized
GOBACK=$(pwd)
OUTFILE="/tmp/sheetmusic-resize.txt"

trap cleanup SIGINT SIGTERM EXIT
trap badstuff ERR
cleanup()
{
	rm -f ${OUTFILE}
	cd ${GOBACK}
	rm -rf ${DIR_RESIZE}
}

badstuff(){
	echo Error occured! Script will cleanup and exit.
	echo AT: "${LINENO}" "$BASH_COMMAND"
	cleanup
}

cat <<STARTUP_MSG
============================================================
		Begin processing files in directory
	${PICKER}
============================================================

STARTUP_MSG

cd "${PICKER}"
NUM_FILES=$(ls page*png | wc -l )
if [ ${NUM_FILES} -eq 0 ]; then
	echo No files to process.
	exit 0
fi
file page*.png | grep -Eo "[[:digit:]]+ *x *[[:digit:]]+" > ${OUTFILE}
export OUTFILE


# Get the width and height values. We use the largest ones.
WIDE=$(cat ${OUTFILE} | cut -w -f1 | sort | tail -1 )
HIGH=$(cat ${OUTFILE} | cut -w -f3 | sort | tail -1 )

echo Resize all images to ${WIDE} by ${HIGH}
echo Number of different widths:  $(cat ${OUTFILE} | cut -w -f1 | sort | uniq | wc -l  )
echo Number of different heights: $(cat ${OUTFILE} | cut -w -f3 | sort | uniq | wc -l  )

## RESIZE
# We are going to make an archive of the current, then process the files
# ${DEBUG} rm -f ${ARC} 2>/dev/null
# ${DEBUG} zip ${ARC} page*.png >/dev/null

${DEBUG} mkdir ${DIR_RESIZE}
${DEBUG} sips --resampleWidth ${WIDE} --resampleHeight ${HIGH} page*.png --out ${DIR_RESIZE}
${DEBUG} cp -vf ${DIR_RESIZE}/page*png ./
${DEBUG} rm -rfv ${DIR_RESIZE}

. ${INCLUDE_SYSTEM}/finish.sh





