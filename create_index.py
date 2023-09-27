from elasticsearch import Elasticsearch, exceptions
from dotenv import load_dotenv
import os
load_dotenv()

cloud_id = os.environ['cloud_id']
cloud_pass = os.environ['cloud_pass']
cloud_user = os.environ['cloud_user']
es = Elasticsearch(cloud_id=cloud_id, basic_auth=(cloud_user, cloud_pass),request_timeout=10)
print(es.info())
search_index = os.environ['search_index']
#search_index = 'esre_test'
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