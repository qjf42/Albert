# coding: utf-8

from typing import List, Optional
from ...interfaces import LexicalResult
from ..interfaces import RetrievalData, ProcessorResult


class ProcessorBase:
    def __init__(self, conf):
        pass

    def process(self,
                query: str, query_lexical_res: Optional[LexicalResult] = None,
                retrieval_data: Optional[RetrievalData] = None,
                history: Optional[List[str]] = None) -> ProcessorResult:
        raise NotImplementedError
