# coding: utf-8

from ...interfaces import LexicalResult
from ..interfaces import RetrievalData, ProcessorResult


class ProcessorBase:
    def __init__(self, conf):
        pass

    def process(self,
                query: str, query_lexical_res: LexicalResult,
                retrieval_data: RetrievalData) -> ProcessorResult:
        raise NotImplementedError
