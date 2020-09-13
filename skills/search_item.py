#coding: utf-8

from typing import List, Tuple
from .base import BaseSkill
from ..nlu import EnumIntent
from ..utils import downloader

from jieba import posseg


class SearchItemSkill(BaseSkill):
    def __init__(self, conf, logger):
        super(SearchItemSkill, self).__init__(conf, logger)
        self.search_api = 'http://{host}:{port}/search'.format(**conf['TheMachine'])
        self.unsub_api = 'http://{host}:{port}/unsub'.format(**conf['TheMachine'])
        self._dl = downloader.Downloader(timeout=5, retry=3)

    def _is_stopword(self, pos):
        """
        m 数量词
        q 量词
        r 代词
        p 介词
        c 连词
        u 助词
        x 虚词
        w 标点
        """
        return pos[0] in 'mqrpcuxw'

    def _align_query_seg(self, slot: str, slot_span: Tuple[int, int], seg_res):
        '''
        对齐slot(query)的切词和整体utterance的切词
        '''
        # XXX
        seg = seg_res['seg']
        try:
            # 如果utterance seg的词位置和slot span不能对齐，则抛异常
            s = next(i for i, tok in enumerate(seg) if tok['start'] == slot_span[0])
            e = next(j for j, tok in enumerate(seg) if tok['end'] == slot_span[1]) + 1
            return [tok['word'] for tok in seg[s:e] if not self._is_stopword(tok['pos'])]
        except:
            # 重新对query切词
            slot_seg = posseg.lcut(slot)
            return [tok.word for tok in slot_seg if not self._is_stopword(tok.flag)]

    def call(self, single_turn_ctx, lexical_res, single_nlu_res):
        ret = self.resp_interface
        query = single_nlu_res.slots['query']
        char_spans = single_nlu_res.char_spans['query']
        keywords = self._align_query_seg(query, char_spans, lexical_res['wordseg'])
        if single_nlu_res.intent == EnumIntent.UNSUBSCRIBE:
            action = 'unsubscribe'
        else:
            action = 'search'
        try:
            data = {
                'keywords': ','.join(keywords),
                'chatroom_id': single_turn_ctx.chatroom_id,
                'user_id': single_turn_ctx.user_id,
                'user_name': single_turn_ctx.user_name,
            }
            api = self.search_api if action == 'search' else self.unsub_api
            api_res = self._dl.download(api, data=data, req_type='POST', json=True)
            api_res['data']['action'] = action
            assert api_res['success'], api_res['err_msg']
        except Exception as e:
            ret['err_msg'] = str(e)
            return ret
        ret['success'] = True
        ret['score'] = 1
        ret['data']['skill_result'] = api_res['data']
        return ret
