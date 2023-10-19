#!/bin/bash
source .env
eland_import_hub_model \
--cloud-id $cloud_id \
--es-api-key $esapi_key \
--hub-model-id cl-tohoku/bert-base-japanese-v2 \
--task-type text_embedding \
--start
python create_index.py