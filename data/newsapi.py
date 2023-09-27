import requests, json, sys
from dotenv import load_dotenv
import os
load_dotenv('../.env')
newsapi_key = os.environ['newsapi_key']

headers = {'X-Api-Key': newsapi_key}
url = 'https://newsapi.org/v2/everything'
params = {
    'q': sys.argv[1],
    'sortBy': 'publishedAt',
    'pageSize': 100
}

response = requests.get(url, headers=headers, params=params)
jsonStr = response.json()
with open(sys.argv[2], 'w', encoding='utf-8') as file:
  json.dump(jsonStr['articles'], file, indent=2, ensure_ascii=False)