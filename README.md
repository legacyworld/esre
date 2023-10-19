# ESRE (Elasticsearch Relevance Engine)
This is the sample implementation of RAG (Retrieval Augmented Generation) using Elasticsearch.
NewsAPI contents are used, but you can easily modify to use other data sources.

# How to use
## Requirements
- Docker: 24.0.5
- Docker Compose: v2.20.2
- OpenAPI information
- Elasticsearch cluster on Elastic Cloud
  - This program assumes that Elasticsearch cluster is craeted on Elastic Cloud
- NewsAPI's API Key (Optional)

## Add extensions
Add `analysis-icu` and `analysis-kuromoji`

Follow this link
https://www.elastic.co/guide/en/cloud/current/ec-adding-elastic-plugins.html

## Create .env file
### basic authentication for Elasticsearch
If you include `esapi_key`, API Key access will be used even if you configure `cloud_pass` and `cloud_id`
```
openai_api_key=<openapi key>
openai_api_type=azure
openai_api_base=<openapi base url>
openai_api_version=<openapi version>
openai_api_engine=<openapi engine>
cloud_id=<cloud id of Elasticsearch Cluster>
cloud_pass=<Cloud pass of Elasticsearch Cluster>
cloud_user=<Cloud User. Normally it is elastic>
search_index=<your index name>
newsapi_key=<newsapi key>
```
### API Key authentication for Elasticsearch
If you want to use Elasticsearch API Key, use the following `.env`.
```
openai_api_key=<openapi key>
openai_api_type=azure
openai_api_base=<openapi base url>
openai_api_version=<openapi version>
openai_api_engine=<openapi engine>
cloud_id=<cloud id of Elasticsearch Cluster>
esapi_key=<Elasticsearch API Key>
search_index=<your index name>
newsapi_key=<newsapi key>
```
## Change requirements.txt
Change the version of elasticsearch and other components accordingly

## Build and run Docker container
`docker compose up -d`
## Initialize the environment
This step will do the followings:
1. Upload cl-tohoku/bert-base-japanese-v2 from Hugging Face
2. Create the ingest pipeline to embed the vector
3. Create the mapping

Enter Docker Container and execute `initialize.sh`
### Basic Authentication
```
docker exec -it esre_flask /bin/bash
python ./initialize.sh
```
### API Key Authentication
```
docker exec -it esre_flask /bin/bash
python ./initialize_api.sh
```
## index documents
docker exec -it esre_flask /bin/bash
cd data
./load_all.sh
```

## Access the page
http://localhost:4000

# Use the different models
- Change --hub-model-id in initialize.sh
- Change model_id of ingest pipeline and text_embedding mapping accordingly in create_index.py
- Change knn and rrf query in app.py

# Add more NewsAPI documents
- Modify url of newsapi.py if you want to get different topics (now get everything)
For example
```
docker exec -it esre_flask /bin/bash
cd data
python newsapi.py コロナウイルス ./json/covid.json
load1.sh ./json/covid.json
```
