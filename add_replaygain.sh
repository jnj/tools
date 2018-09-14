#!/bin/bash

set -e

if [[ "$#" -ne 1 ]]
then
    echo "Pass letter as argument."
    exit 1
fi

LETTER="$1"

for pd in ${LETTER}*/
do
    pushd "$pd"
    for d in */
    do
        echo "checking $d..."
        pushd "$d" >/dev/null
        if ls *.flac >/dev/null 2>&1
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
done

