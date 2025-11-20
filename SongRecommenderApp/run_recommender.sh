#!/bin/sh

export LD_LIBRARY_PATH="/usr/lib"

PYTHON_EXEC="/usr/bin/python3"
SCRIPT_PATH="./recommend.py"

SONG_ARG="$1"
ARTIST_ARG="$2"

$PYTHON_EXEC $SCRIPT_PATH "$SONG_ARG" "$ARTIST_ARG"
