# coding: utf-8

from ..base import RetrieverBase
from ...enums import EnumRetrievalSource
from ...interfaces import KBGraph, RetrievalData
from ....interfaces import LexicalResult


class KBRetriever(RetrieverBase):
    def __init__(self, conf):
        super().__init__(conf)

    def retrieve(self, query: str, lexical_res: LexicalResult) -> RetrievalData:
        g = self._search(query)
        return RetrievalData(EnumRetrievalSource.KB, g)

    def _search(self, query: str) -> KBGraph:
        return None
