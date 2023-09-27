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
  
## Create .env file
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

## Build and run Docker container
`docker compose up -d`
## Create Elasticsearch index with kuromoji analyzer and Dense Vector embedding
Enter Docker Container and execute `create_index.py`
```
docker exec -it esre_flask /bin/bash
python create_index.py
```
You can do this by using Kibana Dev Tools, too. Copy `body` contents and paste it in Dev Tools.

## index documents
```
docker exec -it esre_flask /bin/bash
cd data
./load_all.sh
```

## Access the page
http://localhost:4000
