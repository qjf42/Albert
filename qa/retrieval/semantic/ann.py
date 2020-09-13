# coding: utf-8

from typing import List
import numpy as np
from ..base import RetrieverBase
from ...enums import EnumRetrievalSource
from ...interfaces import Doc, RetrievalData
from ....interfaces import LexicalResult


class ANNRetriever(RetrieverBase):
    def __init__(self, conf):
        super().__init__(conf)

        self.index = conf['index_single_dialog']

    def retrieve(self, query: str, lexical_res: LexicalResult) -> RetrievalData:
        emb = self._encode(query)
        docs = self._search(emb)
        return RetrievalData(EnumRetrievalSource.ANN, docs)

    def _encode(self, query: str) -> np.ndarray:
        pass

    def _search(self, emb: np.ndarray) -> List[Doc]:
        return []
