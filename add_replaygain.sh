#!/bin/bash

set -e

if [[ "$#" -ne 1 ]]
then
    echo "Pass root dir as argument."
    exit 1
fi

ROOT_DIR="$1"

pushd "$ROOT_DIR" >/dev/null

for d in */
do
    pushd "$d" >/dev/null
    if ls *.flac >/dev/null
    then
        if metaflac --show-tag=REPLAYGAIN_REFERENCE_LOUDNESS 01*flac | grep REPLAYGAIN > /dev/null
        then
            true
        else
            echo "writing replaygain metadata for $(pwd)"
            metaflac --add-replay-gain *.flac
        fi
    fi
    popd >/dev/null
done

popd

