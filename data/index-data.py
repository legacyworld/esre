
from tqdm import tqdm
from elasticsearch import Elasticsearch, helpers
import argparse
from dotenv import load_dotenv
import os
load_dotenv()
import json

parser = argparse.ArgumentParser()
# required args
parser.add_argument('--index_name', dest='index_name',
                    required=False, default='esre')
parser.add_argument('--file', dest='file',
                    required=False, default='data.json')

args = parser.parse_args()


def data_generator(file_json, index, pipeline):
    for doc in file_json:
        doc['_run_ml_inference'] = True
        yield {
            "_index": index,
            #'pipeline': "esre",
            'pipeline': "japanese-text-embeddings",
            "_source": doc,
        }

if "cloud_id" in os.environ:
    cloud_id = os.environ['cloud_id']
    if "esapi_key" in os.environ:
        esapi_key = os.environ['esapi_key']
        es = Elasticsearch(cloud_id=cloud_id, api_key=esapi_key,request_timeout=10)
        print("api key used")
    elif os.environ.keys() >= {'cloud_pass','cloud_user'}:
        cloud_pass = os.environ['cloud_pass']
        cloud_user = os.environ['cloud_user']
        es = Elasticsearch(cloud_id=cloud_id, basic_auth=(cloud_user, cloud_pass),request_timeout=10)
        print("basic authentication")
    else:
        print("Define cloud_pass/cloud_user or esapi_key")
        exit()
else:
    print("Define cloud_id")
    exit()

print(es.info())
# es = Elasticsearch(
#     cloud_id=args.cloud_id,
#     basic_auth=(args.es_user, args.es_password),
#     request_timeout=600
# )

print("Indexing documents, this might take a while...")
with open(args.file, 'r') as file:
    file_json = json.load(file)
total_documents = len(file_json)
progress_bar = tqdm(total=total_documents, unit="documents")
success_count = 0

for response in helpers.streaming_bulk(client=es, actions=data_generator(file_json, args.index_name, args.index_name)):
    if response[0]:
        success_count += 1
    progress_bar.update(1)
    progress_bar.set_postfix(success=success_count)

progress_bar.close()

# Calculate the success percentage
success_percentage = (success_count / total_documents) * 100
print(f"Indexing completed! Success percentage: {success_percentage}%")
print("Done indexing documents!")
