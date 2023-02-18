# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
# Licensed under GPL 3.0
#
#:BEGIN template.sh

if [ ! -e ${INCLUDE_SYSTEM}/start.sh ] ; then
    echo "ERROR! Can't include ${INCLUDE_SYSTEM}/start.sh"
    exit 99 
fi
. ${INCLUDE_SYSTEM}/start.sh "$@" 

#:END template.sh