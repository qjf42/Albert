# coding: utf-8

from typing import List
from .base import ProcessorBase
from ..enums import EnumProcessorType
from ..interfaces import RetrievalData, ProcessorResult
from ...interfaces import LexicalResult


class SemanticMatcher(ProcessorBase):
    def __init__(self, conf):
        super().__init__(conf)
        self.res_type = EnumProcessorType.MATCHING

    def process(self,
                query: str, query_lexical_res: LexicalResult,
                retrieval_data: RetrievalData,
                history: List[str] = None) -> ProcessorResult:
        for doc in retrieval_data.data:
            return ProcessorResult(self.res_type, 'model', doc.doc, 1.)
