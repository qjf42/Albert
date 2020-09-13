1 #coding: utf-8

import sys
from collections import Counter
from glob import iglob
import requests
from tqdm import tqdm

from elasticsearch import Elasticsearch

ES = Elasticsearch([{'host': conf['host'], 'port': conf['port']}])


def create_index():
    url = f'http://127.0.0.1:9200/{ES_INDEX_SINGLE_DIALOG}'
    # delete
    ret = requests.delete(url)
    print(ret.json())
    # create
    data = {
        "settings": {
            "number_of_replicas": 1,
            "analysis": {
                "analyzer": {
                    "jieba": {
                        "tokenizer": "jieba_search",
                        "filter": [
                            "lowercase",
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "query": {
                    "type": "text"
                },
                "answer": {
                    "type": "text"
                },
                "freq": {
                    "type": "float"
                },
            }
        }
    }
    ret = requests.put(url, json=data)
    print(ret.json())


def load_corpus():
    qa_counter = Counter()
    for filename in iglob('chinese_chatbot_corpus/clean_chat_corpus/*.tsv'):
        with open(filename) as f:
            for line in tqdm(f):
                try:
                    q, a = line.strip().split('\t')
                    if len(a) > 30:
                        continue
                    qa_counter[(q, a)] += 1
                except:
                    #print(line)
                    pass
    return qa_counter


def add_doc(q, a, freq):
    doc = {
        'query': q,
        'answer': a,
        'freq': freq,
    }
    ES.index(ES_INDEX_SINGLE_DIALOG, doc)#, doc_type=ES_TYPE_SINGLE_QA)


def main():
    create_index()
    corpus = [(q, a, f) for (q,a), f in load_corpus().items() if f > 3]
    print(f'Corpus loaded, total {len(corpus)} unique qa pairs.')
    for q, a, freq in tqdm(corpus):
        add_doc(q, a, freq)


if __name__ == '__main__':
    main()
