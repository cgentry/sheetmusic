#!/bin/bash
##
## Build the program for either MacOS or Linux
##

RTN_DIR=$(pwd)
unamestr=$(uname)
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'FreeBSD' ]]; then
   platform='freebsd'
elif [[ "$unamestr" == 'Darwin' ]]; then
   platform='macos'
else
   echo Unknown system: ${unamestr}
   exit 9
fi

TARGET_DIR="${RTN_DIR}/${platform}"

trap  "{ cd $RTN_DIR; }" EXIT

sh ./src/gen-docs.sh

rm -r ${TARGET_DIR} 2>/dev/null

pyi-makespec  --windowed --noconsole --add-data src/docs/sheetmusic.qhc:docs/ --add-data src/docs/sheetmusic.qch:docs/ --add-data src/util/scripts:util/scripts src/sheetmusic.py
pyinstaller   --clean    --workpath ${TARGET_DIR}/build --distpath ${TARGET_DIR}/dist        ./sheetmusic.spec

