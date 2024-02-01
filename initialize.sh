#!/bin/bash
source .env
eland_import_hub_model \
--cloud-id $cloud_id \
-u $cloud_user \
-p $cloud_pass \
--hub-model-id cl-tohoku/bert-base-japanese-v3 \
--task-type text_embedding \
--start
python create_index.py