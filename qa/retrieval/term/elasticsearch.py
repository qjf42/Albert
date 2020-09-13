# coding: utf-8

from typing import List
import numpy as np
from elasticsearch import Elasticsearch
from ..base import RetrieverBase
from ...enums import EnumRetrievalSource
from ...interfaces import Doc, RetrievalData
from ....interfaces import LexicalResult


class ESRetriever(RetrieverBase):
    def __init__(self, conf):
        super().__init__(conf)
        self._es_cli = Elasticsearch([{'host': conf['host'], 'port': conf['port']}])
        self.index = conf['index_single_dialog']

    def retrieve(self, query: str, lexical_res: LexicalResult) -> RetrievalData:
        docs = self._search(query)
        return RetrievalData(EnumRetrievalSource.TERM, docs)

    def _search(self, query: str) -> List[Doc]:
        try:
            es_res = self._es_cli.search(self.index, {'query': {'match': {'query': query}}})
            hits = es_res.get('hits', {}).get('hits', [])
        except Exception as e:
            raise Exception('Elasticsearch error: %s.' % e)
        assert hits, 'Empty search results.'

        ret = []
        for hit in hits[:self.max_retrieval_num]:
            hit_query = hit['_source']['query']
            answer = hit['_source']['answer']
            score = hit['_score']
            ret.append(Doc(hit_query, answer, score))
        return ret
