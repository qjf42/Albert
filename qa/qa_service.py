#coding: utf-8

from typing import Dict, List

import flask

from ..enums import EnumResponseError
from ..utils import log_utils
from .conf import RETRIEVER_CONF, PROCESSOR_CONF, LOG_CONF
from .enums import EnumRetrievalSource, EnumProcessorType
from .interfaces import QAResponse, Request
from .retrieval import (
    RetrieverBase,
    ANNRetriever,
    BaiduRetriever,
    ESRetriever,
    KBRetriever
)
from .processing import (
    ProcessorBase,
    Seq2Seq,
    SemanticMatcher,
    Summarizer,
    ExtractiveKBQA,
    ExtractiveMRC
)


class QAService:
    def __init__(self):
        # 问题分析

        # 召回
        self.retrievers: List[RetrieverBase] = [
            # ESRetriever(RETRIEVER_CONF['ES']),
            # ANNRetriever(RETRIEVER_CONF['ANN']),
            # KBRetriever(RETRIEVER_CONF['KB']),
            # BaiduRetriever(RETRIEVER_CONF['Baidu']),
        ]

        # 处理
        self.semantic_matcher = SemanticMatcher(PROCESSOR_CONF[EnumProcessorType.MATCHING])
        self.summarizer = Summarizer(PROCESSOR_CONF[EnumProcessorType.EXTRACTIVE_SUMMARIZER])
        self.extractive_kbqa = ExtractiveKBQA(PROCESSOR_CONF[EnumProcessorType.KBQA_ENTITY])
        self.extractive_mrc = ExtractiveMRC(PROCESSOR_CONF[EnumProcessorType.MRC_SPAN])
        self.s2s_processor = Seq2Seq(PROCESSOR_CONF[EnumProcessorType.S2S])

        # 召回到处理的映射
        self.retrieve2process: Dict[EnumRetrievalSource, ProcessorBase] = {
            EnumRetrievalSource.ANN: self.semantic_matcher,
            EnumRetrievalSource.TERM: self.semantic_matcher,
            EnumRetrievalSource.KB: self.extractive_kbqa,
            EnumRetrievalSource.SEARCH: self.extractive_mrc,
        }
        
    def ask(self, req: Request) -> QAResponse:
        query = req.query
        lexical_res = req.lexical_res
        history = req.history
        resp = QAResponse()
        if req.debug:
            resp.add_debug('request', req.to_dict())
        if not query:
            return resp.set_error(EnumResponseError.EMPTY_UTTERANCE)\
                       .set_response('你说什么？')

        # 问题分析

        # 召回
        for retriever in self.retrievers:
            retrieved_data = retriever.retrieve(query, lexical_res)
            if retrieved_data.data:
                # 处理
                processor = self.retrieve2process[retrieved_data.src_type]
                try:
                    proc_res = processor.process(query, lexical_res, retrieved_data)
                    if req.debug:
                        resp.debug = proc_res.debug
                    return resp.set_response(proc_res.answer)\
                               .set_skill_result(proc_res.detail)
                except Exception as e:
                    continue
        # 闲聊兜底
        try:
            proc_res = self.s2s_processor.process(query, history=history)
            if req.debug:
                resp.debug = proc_res.debug
            return resp.set_response(proc_res.answer)\
                       .set_skill_result(proc_res.detail)
        except Exception as e:
            return resp.set_error(EnumResponseError.SKILL_ERROR, f'兜底错误，啥也找不到..., {e}')


'''FLASK'''

QA_SERVICE = QAService()
app = flask.Flask(__name__)
log_utils.set_app_logger(app.logger, **LOG_CONF)


def parse_req(options):
    ret = {}
    req = flask.request
    data = req.get_json(silent=True) or {}
    for key, required in options.items():
        val = req.args.get(key, data.get(key, req.form.get(key)))
        if val is None and required:
            raise ValueError(f'Parameter [{key}] is missing.')
        ret[key] = val
    return ret


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    param_options = {
        'query': True,
        'lexical_res': True,
        'history': False,
        'debug': False,
    }
    try:
        params = parse_req(param_options)
        req = Request(**params)
    except Exception as e:
        resp = QAResponse().set_error(EnumResponseError.INVALID_PARAMS, str(e))
        return flask.jsonify(resp)
    try:
        resp = QA_SERVICE.ask(req)
    except Exception as e:
        resp = QAResponse().set_error(EnumResponseError.UNKNOWN_ERROR, str(e))
    return flask.jsonify(resp)
