#!/bin/bash

#
#   Definitions
#

# catalogs structure
CONF="config/wget_data_config.json";
RAW="raw";

# method allowing get data from config file
function getFromConf {
    echo $(cat $CONF | jq -r $1);
}

# variables constant for all script
LINES=$(grep \"uri2\": $CONF | wc -l);
URI1=$(getFromConf '.uri1');


#
#   Script
#

#clear raw catalog
rm $RAW/*

# iterate over all lines
for i in `seq 1 $LINES`
do
    # downloading data from links from config
    wget $URI1$(getFromConf '.data['$i-1'].uri2') -P $RAW
done

