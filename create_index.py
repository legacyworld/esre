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
pipeline_id = "japanese-text-embeddings"
body = {
  "description": "Text embedding pipeline",
  "processors": [
    {
      "inference": {
        "model_id": "cl-tohoku__bert-base-japanese-v2",
        "target_field": "text_embedding",
        "field_map": {
          "title": "text_field"
        }
      }
    }
  ]
}
print(es.ingest.put_pipeline(id=pipeline_id,body=body))

body = {
  'settings': {
    'index': {
      'analysis': {
        'char_filter': {
          'normalize': {
            'type': 'icu_normalizer',
            'name': 'nfkc',
            'mode': 'compose'
          }
        },
        'tokenizer': {
          'ja_kuromoji_tokenizer': {
            'mode': 'search',
            'type': 'kuromoji_tokenizer'
          }
        },
        'analyzer': {
          'kuromoji_analyzer': {
            'tokenizer': 'ja_kuromoji_tokenizer',
            'filter': [
              'kuromoji_baseform',
              'kuromoji_part_of_speech',
              'cjk_width',
              'ja_stop',
              'kuromoji_stemmer',
              'lowercase'
            ]
          }
        }
      }
    }
  },
'mappings': {
    'properties': {
      'author': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'category': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'content': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'description': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'publishedAt': {
        'type': 'date'
      },
      'source': {
        'properties': {
          'name': {
            'type': 'text',
            'fields': {
              'keyword': {
                'type': 'keyword',
                'ignore_above': 256
              }
            }
          }
        }
      },
      'text_embedding': {
        'properties': {
          'model_id': {
            'type': 'text',
            'fields': {
              'keyword': {
                'type': 'keyword',
                'ignore_above': 256
              }
            }
          },
          'predicted_value': {
            'type': 'dense_vector',
            'dims': 768,
            'index': True,
            'similarity': 'cosine'
          }
        }
      },
      'title': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'url': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      },
      'urlToImage': {
        'type': 'text',
'analyzer': 'kuromoji_analyzer'
      }
    }
  }
}
print(es.indices.create(index=search_index,body=body))