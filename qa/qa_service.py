#coding: utf-8

from typing import List

import flask

from ..enums import EnumResponseError
from ..utils import log_utils
from .conf import RETRIEVER_CONF, PROCESSOR_CONF
from .enums import EnumRetrievalSource
from .interfaces import QAResponse, Request
from .retrieval import RetrieverBase, ANNRetriever, BaiduRetriever, ESRetriever, KBRetriever
from .processing import ProcessorBase, SemanticMatcher, Summarizer, ExtractiveKBQA, ExtractiveMRC


class QAService:
    def __init__(self):
        # 问题分析

        # 召回
        self.retrievers: List[RetrieverBase] = [
            ESRetriever(RETRIEVER_CONF['ES']),
            ANNRetriever(RETRIEVER_CONF['ANN']),
            KBRetriever(RETRIEVER_CONF['KB']),
            BaiduRetriever(RETRIEVER_CONF['Baidu']),
        ]

        # 处理
        self.semantic_matcher = SemanticMatcher(PROCESSOR_CONF['matching'])
        self.summarizer = Summarizer(PROCESSOR_CONF['summarizer'])
        self.extractive_kbqa = ExtractiveKBQA(PROCESSOR_CONF['KBQA'])
        self.extractive_mrc = ExtractiveMRC(PROCESSOR_CONF['MRC'])

        # 召回到处理的映射
        self.retrieve2process = {
            EnumRetrievalSource.ANN: self.semantic_matcher,
            EnumRetrievalSource.TERM: self.semantic_matcher,
            EnumRetrievalSource.KB: self.extractive_kbqa,
            EnumRetrievalSource.SEARCH: self.extractive_mrc,
        }
        
    def ask(self, req: Request) -> QAResponse:
        query = req.query
        lexical_res = req.lexical_res
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
                    proc_res = processor.process(retrieved_data, lexical_res)
                    if req.debug:
                        resp.debug = proc_res.debug
                    return resp.set_response(proc_res.answer)\
                               .set_skill_result(proc_res.detail)
                except Exception as e:
                    continue
        return resp.set_error(EnumResponseError.SKILL_ERROR)\
                   .set_response('啥也找不到...')


'''FLASK'''

QA_SERVICE = QAService()
app = flask.Flask(__name__)
log_utils.set_app_logger(app.logger, **QA_LOG_CONF)


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
        'debug': False,
    }
    try:
        params = parse_req(param_options)
    except Exception as e:
        resp = QAResponse().set_error(EnumResponseError.INVALID_PARAMS, str(e))
        return flask.jsonify(resp.to_dict())
    try:
        req = Request(**params) 
        resp = QA_SERVICE.ask(req)
    except Exception as e:
        resp = QAResponse().set_error(EnumResponseError.UNKNOWN_ERROR, str(e))
    return flask.jsonify(resp.to_dict())
