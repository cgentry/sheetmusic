#!/bin/bash
RTN=`pwd`
cd docs/
qhelpgenerator sheetmusic.qhcp -o sheetmusic.qhc
cd $RTN
