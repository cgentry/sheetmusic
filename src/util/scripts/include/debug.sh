# DEBUG INCLUDE FILE
#:usage Handle debug flag (-X) (Debug is selected on Execute screen)
# (c) Copyright 2023 Charles Gentry

DEBUG=''

while (( $# ))
do
    case $1 in
    -X) DEBUG="echo DEBUG: " ;;
     *)  ;;
    esac
    shift
done

if [ ! -z "$DEBUG" ]; then

cat << END_DEBUG

======================================================
              Script is in debug mode.
Statements that would have run will start with DEBUG:
======================================================

DEBUG:
END_DEBUG
fi