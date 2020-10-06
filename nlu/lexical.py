#coding: utf-8
'''词法分析'''

from typing import List, Tuple
from ..utils import log_utils
from ..interfaces import BaseRequest, Token, LexicalResult


class BaseWordSeg:
    def __init__(self, conf, logger):
        self.t2s = conf['t2s']
        self.logger = logger

    def seg(self, s: str) -> List[Token]:
        raise NotImplementedError

    def _tokenize(self, seg_list: List[Tuple[str, str]]) -> List[Token]:
        ret = []
        i = j = 0
        for word, pos in seg_list:
            j += len(word)
            ret.append(Token(word, pos, i, j))
            i = j
        return ret


class ThulacWordSeg(BaseWordSeg):
    def __init__(self, conf, logger):
        super().__init__(conf, logger)
        import thulac
        self._seg = thulac.thulac(T2S=self.t2s)
 
    def seg(self, s: str) -> List[Token]:
         seg_res = self._seg.fast_cut(s)
         return self._tokenize(seg_res)
 

from jieba import posseg, lcut_for_search
class JiebaWordSeg(BaseWordSeg):
    def __init__(self, conf, logger):
        super().__init__(conf, logger)
        if self.t2s:
            self.logger.warning('Jieba does not support t2s currently.')
 
    def seg(self, s: str) -> List[Token]:
        seg_res = posseg.lcut(s)
        return self._tokenize(seg_res)
 
    def seg_search(self, s: str) -> List[Token]:
        seg_res = [(_, None) for _ in lcut_for_search(s)]
        return self._tokenize(seg_res)


class LexicalParser:
    def __init__(self, conf, log_conf):
        self.logger = log_utils.get_logger(**log_conf)
        self._init_wordseg(conf['wordseg'])

    def _init_wordseg(self, wordseg_conf):
        segger_type = wordseg_conf['segger'].lower()
        if segger_type == 'jieba':
            self.wordseg = JiebaWordSeg(wordseg_conf, self.logger)
        elif segger_type == 'thulac':
            self.wordseg = ThulacWordSeg(wordseg_conf, self.logger)
        else:
            raise Exception(f'Unknown segger type "{segger_type}"')

    def parse(self, req: BaseRequest) -> LexicalResult:
        tokens = self.wordseg.seg(req.utterance)
        entities = []
        search_tokens = self.wordseg.seg_search(req.utterance)
        keywords = [tok.word for tok in tokens if not self._is_stopword(tok.pos)]
        return LexicalResult(tokens, entities, search_tokens, keywords)

    def _is_stopword(self, pos):
        """
        m 数量词 q 量词
        r 代词 p 介词 c 连词 u 助词 x 虚词
        w 标点
        """
        return pos[0] in 'mqrpcuxw'
