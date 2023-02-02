#!/bin/bash
RTN=$( cd $(dirname $0); pwd; )

trap "{ cd $RTN; }" EXIT

cd $RTN/docs/
qhelpgenerator sheetmusic.qhcp -o sheetmusic.qhc
