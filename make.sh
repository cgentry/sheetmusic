#!/bin/bash
##
## Build the program for either MacOS or Linux
##
error_exit(){
   echo Error! $1
   echo "Lineno: ${2}"
   exit 9
}
## Check for py installers
for PGM in pyi-makespec pyinstaller ; do
   echo Checking ${PGM} ...
   if [ ! $(command -v ${PGM} 2>/dev/null) ] ; then
      echo "ERROR: ${PGM} program not found."
      exit 9
   fi
done
echo "Installer programs checked."

## Check python program
for PGM in python3 python ; do
   if [ $(command -v ${PGM} 2>/dev/null) ] ; then
      PY=${PGM}
      break
   fi
done
[ "${PY}" == "" ] && error_exit 'Python program not found' ${LINENO}

## Check for library pyside6
${PY} -c 'import PySide6'  || error_exit 'No PySide6 library installed.' ${LINENO}
echo PySide6 library checked.


## OK start the build process
CONSOLE="--noconsole"
WINDOWED="--windowed"
DATA=( "--add-data" "src/docs/sheetmusic.qhc:docs/" "--add-data" "src/docs/sheetmusic.qch:docs/" "--add-data" "src/util/scripts:util/scripts" )

## Check for the OS
RTN_DIR=$(pwd)
PYI=( "--clean" )
ICON=( )
SPEC_OPTIONS=()

unamestr=$(uname)
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'FreeBSD' ]]; then
   platform='freebsd'
elif [[ "$unamestr" == 'Darwin' ]]; then
   platform='macos'
   SPEC_OPTIONS+=("--noconsole" "--osx-bundle-identifier" "com.organmonkey.sheetmusic"  )
   # ICON=( "--icon" "src/images/sheetmusic.icns" "--add-binary" "src/images/sheetmusic.icns:images/sheetmusic.icns" )
   ICON=( "--icon" "src/images/sheetmusic.icns" )
else
   error_exit "Unknown system: ${unamestr}" ${LINENO}
fi

TARGET_DIR="${RTN_DIR}/${platform}"

trap  "{ cd $RTN_DIR; }" EXIT

rm src/sheetmusic.spec  2>/dev/null
cat <<MAKE_SPEC

==============================================
=            pyi-makespec                    =
==============================================
echo pyi-makespec  -n "SheetMusic" ${ICON[@]} ${DATA[@]} ${SPEC_OPTIONS[@]} src/sheetmusic.py || error_exit "Could not make spec file" ${LINENO}


MAKE_SPEC
pyi-makespec  -n "SheetMusic" ${ICON[@]} ${DATA[@]} ${SPEC_OPTIONS[@]} src/sheetmusic.py || error_exit "Could not make spec file" ${LINENO}


sh ./src/gen-docs.sh
rm -r ${TARGET_DIR} 2>/dev/null
cat <<MAKE_PGM

==============================================
=            pyinstaller                     =
==============================================
echo pyinstaller   ${PYI[@]} --workpath ${TARGET_DIR}/build --distpath ${TARGET_DIR}/dist        ./sheetmusic.spec


MAKE_PGM
pyinstaller   ${PYI[@]} --workpath ${TARGET_DIR}/build --distpath ${TARGET_DIR}/dist        ./sheetmusic.spec

