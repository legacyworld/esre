#!/bin/bash
source ../.env
echo $cloud_id
dir_path="./json"
dirs=`find $dir_path -maxdepth 1 -type f -name *.json`

for dir in $dirs;
do
    python3 index-data.py --index_name=$search_index --file=$dir --es_password=$cloud_pass --cloud_id=$cloud_id
done