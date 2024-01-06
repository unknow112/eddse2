#!/bin/bash

set -x
SUFFIX='.bz2'
for filename in $(find tmp/datasets -type f -name '*.bz2') ; do
    bzip2 -d -c ${filename} | sort | uniq > ${filename%$SUFFIX}
    rm ${filename}
done
