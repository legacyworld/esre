#!/bin/bash
source ../.env
dir_path="./json"
dirs=`find $dir_path -maxdepth 1 -type f -name *.json`

for dir in $dirs;
do
    python3 index-data.py --index_name=$search_index --file=$dir
done