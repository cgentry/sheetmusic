# DEBUG INCLUDE FILE
#:usage Output a message indicating debug mode. (Debug is selected on Execute screen)
# (c) Copyright 2023 Charles Gentry

# DEBUG is set by the -X flag in parameters.sh
if [ ! -z "$DEBUG" ]; then

cat << END_DEBUG

======================================================
              Script is in debug mode.
Statements that would have run will start with DEBUG:
======================================================

DEBUG:
END_DEBUG
fi