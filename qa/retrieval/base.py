# coding: utf-8

from ...interfaces import LexicalResult
from ..interfaces import RetrievalData


class RetrieverBase:
    def __init__(self, conf):
        self.max_retrieval_num = conf['max_retrieval_num']

    def retrieve(self, query: str, lexical_res: LexicalResult) -> RetrievalData:
        raise NotImplementedError
