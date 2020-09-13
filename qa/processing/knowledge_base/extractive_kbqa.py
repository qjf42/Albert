# coding: utf-8

from ..base import ProcessorBase
from ...enums import EnumProcessorType
from ...interfaces import RetrievalData, ProcessorResult
from ....interfaces import LexicalResult


class ExtractiveKBQA(ProcessorBase):
    def __init__(self, conf):
        super().__init__(conf)
        self.res_type = EnumProcessorType.KBQA_ENTITY

    def process(self,
                query: str, query_lexical_res: LexicalResult,
                retrieval_data: RetrievalData) -> ProcessorResult:
        kb_graph = retrieval_data.data
        return ProcessorResult(self.res_type, 'model', kb_graph.entities[0], 1.)
