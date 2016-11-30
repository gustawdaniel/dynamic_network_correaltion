#!/usr/bin/env bash

# catalogs structure
RAW=raw;
BUILD=build;

# clear build for idempotency
rm -rf $BUILD/*;

# loop over archives in raw
for FILE in $RAW/*.zip
do
#    create directory in build and unzip there file from raw
    NAME=$(basename $FILE .zip);
    echo $NAME;
    mkdir -p $BUILD/$NAME;
    unzip -q $FILE -d $BUILD/$NAME;
done