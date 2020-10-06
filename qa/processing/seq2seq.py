# coding: utf-8

from typing import List, Optional
from .base import ProcessorBase
from ..enums import EnumProcessorType
from ..interfaces import RetrievalData, ProcessorResult
from ...interfaces import LexicalResult
from ..utils import ModelClient


class Seq2Seq(ProcessorBase):
    def __init__(self, conf):
        super().__init__(conf)
        self.res_type = EnumProcessorType.S2S
        self.model_name = 'chitchat'
        self._model_cli = ModelClient(timeout=2, retry=1)

    def process(self,
                query: str, query_lexical_res: Optional[LexicalResult] = None,
                retrieval_data: Optional[RetrievalData] = None,
                history: Optional[List[str]] = None) -> ProcessorResult:
        params = {'utterance': query, 'history': history}
        resp = self._model_cli.request(self.model_name, params)['resp']
        return ProcessorResult(self.res_type, self.model_name, resp, 1.)
