#!/usr/bin/env bash

# install dependencies
sudo apt-get install freeglut3-dev
sudo apt-get install jq

# prepare data
bash wget_data.sh
bash build_data.sh

# prepare test
mkdir -p test
rm -rf test/*
cp build/mstcgl/[A-D][A-D][A-D]* test/

# run server
bash ubigraph_server