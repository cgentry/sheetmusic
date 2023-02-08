# This file is part of SheetMusic
# Copyright: 2022,2023 by Chrles Gentry
# Licensed under GPL 3.0
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