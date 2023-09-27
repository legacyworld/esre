#!/bin/bash

source ../.env
echo $cloud_id
python3 index-data.py --index_name=$search_index --file=$1 --es_password=$cloud_pass --cloud_id=$cloud_id