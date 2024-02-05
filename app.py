from elasticsearch import Elasticsearch, exceptions
from dotenv import load_dotenv
import os
load_dotenv()

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
search_index = os.environ['search_index']
bm25_search_fields = ["title", "description"]
bm25_result_fields = ["description", "url", "category", "title"]

import openai
if os.environ.keys() >= {'openai_api_key','openai_api_type','openai_api_base','openai_api_version','openai_api_engine'}:
    openai.api_key = os.environ['openai_api_key']
    openai.api_type = os.environ['openai_api_type']
    openai.api_base = os.environ['openai_api_base']
    openai.api_version = os.environ['openai_api_version']
    engine = os.environ['openai_api_engine']
else:
    print("Define all openai parameters")
    exit()

def get_text_search_request_body(query, search_fields, result_fields, size=10):
    return {
        '_source': False,
        'fields': result_fields,
        'size': size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": search_fields
            }
        }
    }

def get_vector_search_request_body(query, search_fields, result_fields, size=10):
    return {
        '_source': False,
        'fields': result_fields,
        'size': size,
        "knn": {
            "field": "text_embedding.predicted_value",
            "k": 10,
            "num_candidates": 100,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "cl-tohoku__bert-base-japanese-v3", 
                    "model_text": query
                }
            }
        }
    }

def get_rrf_search_request_body(query, search_fields, result_fields, size=10):
    return {
        '_source': False,
        'fields': result_fields,
        'size': size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": search_fields
            }
        },
        "knn": {
            "field": "text_embedding.predicted_value",
            "k": 10,
            "num_candidates": 100,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "cl-tohoku__bert-base-japanese-v3", 
                    "model_text": query
                }
            }
        },
        "rank": {
            "rrf": {
                "window_size": 50,
                "rank_constant": 20
            }
        }
    }

def get_es_result():
    query = request.args['var1']

    bm25_body = get_text_search_request_body(query,bm25_search_fields,bm25_result_fields)
    bm25_result = es.search(index=search_index, query=bm25_body["query"], fields=bm25_body["fields"], size=bm25_body["size"], source=bm25_body["_source"])
    bm25_documents = bm25_result['hits']['hits'][:10]

    vector_body = get_vector_search_request_body(query,bm25_search_fields,bm25_result_fields)
    vector_result = es.search(index=search_index, knn=vector_body["knn"], fields=vector_body["fields"], size=vector_body["size"], source=vector_body["_source"])
    vector_documents = vector_result['hits']['hits'][:10]

    rrf_body = get_rrf_search_request_body(query,bm25_search_fields,bm25_result_fields)
    rrf_result = es.search(index=search_index, query=bm25_body["query"], knn=rrf_body["knn"], fields=rrf_body["fields"], size=rrf_body["size"], source=rrf_body["_source"])
    rrf_documents = rrf_result['hits']['hits'][:10]

    bm25_all = []
    for hit in bm25_documents[:3]:
        temp_contents = {'url': hit['fields']['url'][0],'title': hit['fields']['title'][0],'description': hit['fields']['description'][0]}
        bm25_all.append(temp_contents)

    vector_all = []
    for hit in vector_documents[:3]:
        temp_contents = {'url': hit['fields']['url'][0],'title': hit['fields']['title'][0],'description': hit['fields']['description'][0]}
        vector_all.append(temp_contents)

    rrf_all = []
    for hit in rrf_documents[:3]:
        temp_contents = {'url': hit['fields']['url'][0],'title': hit['fields']['title'][0],'description': hit['fields']['description'][0]}
        rrf_all.append(temp_contents)

    return {'bm25': bm25_all,'vector': vector_all,'rrf': rrf_all,'openai_answer': ""}

def get_all_results():
    query = request.args['var1']
    response = get_es_result()

    openai_answer = ""
    if request.args['var2'] == "openai":
        prompt = query
        messages = {"message": [{"role": "system", "content": prompt}]}
        completion = completion_with_backoff(engine=engine,temperature=0.2,messages=messages["message"])
        openai_answer = completion["choices"][0]["message"]["content"]
    
    response['openai_answer'] = openai_answer
    return response

def truncate_text(text, max_tokens):
    print(f"text = {text}")
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    print(f'max token = {tokens[:max_tokens]}')
    return ' '.join(tokens[:max_tokens])

def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

from flask import Flask, render_template, request, Response, stream_with_context
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("base.html")

@app.route('/api/search_results')
def es_search_results():
    all = get_es_result()
    query = request.args['var1']
    return render_template("index.html",all=all,query=query)

@app.route('/api/all_results')
def openai_results():
    all = get_all_results()
    query = request.args['var1']
    return render_template("index.html",all=all,query=query)

@app.route('/api/completions')
def route_api_stream():
    all = get_es_result()
    all['openai_answer'] = request.args['var3']
    query = request.args['var1']

    def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        rv.disable_buffering()
        return rv

    def stream():
        max_tokens = 1024
        max_context_tokens = 4000
        safety_margin = 5
        prompt=""
        documents = all[request.args['var2']]
        for item in documents:
            prompt += f"Description: {item['description']}"
        prompt += f"\nQuestion: {query}"
        truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)
        messages = {"message": [{"role": "system", "content": "Given the following extracted parts of a long document and a question, create a final answer. If you don't know the answer, just say '検索対象からは回答となる情報が見つかりませんでした'. Don't try to make up an answer."},{"role": "system", "content": truncated_prompt}]}
        completion = completion_with_backoff(engine=engine,temperature=0.2,messages=messages["message"],stream=True)
        for line in completion:
            if len(line['choices']) > 0:
                chunk = line['choices'][0].get('delta', {}).get('content', '')
                if chunk:
                    yield chunk.strip()
    return Response(stream_with_context(stream_template("index.html",query=query,all=all,content=stream())))

if __name__ == "__main__":
    app.run(port=4000, debug=True, host = "0.0.0.0")