# coding: utf-8

from typing import List
from ..base import RetrieverBase
from ...enums import EnumRetrievalSource
from ...interfaces import WebPage, RetrievalData
from ....interfaces import LexicalResult
from ....utils.downloader import Downloader, UA


class BaiduRetriever(RetrieverBase, Downloader):
    def __init__(self, conf):
        RetrieverBase.__init__(conf)
        Downloader.__init__(**conf)

        self.url = 'http://www.baidu.com/s'
        self.max_pages = conf.get('max_pages', 1)
        self.header = {'user-agent': UA}

    def retrieve(self, query: str, lexical_res: LexicalResult) -> RetrievalData:
        docs = []
        for page_idx in range(self.num_pages):
            page = self._search(query, page_idx)
            docs.extehd(self._parse(page))
            if len(docs) >= self.max_retrieval_num:
                break
        docs = [WebPage(query, doc, 1., url) for doc, url in docs]
        return RetrievalData(EnumRetrievalSource.SEARCH, docs)

    def _search(self, query: str, page_idx: int = 0):
        params = {
            'ie': 'utf-8',
            'wd': query,
        }
        if page_idx > 0:
            params['pn'] = page_idx * 10
        return self.download(
            self.url, params=params, headers=self.header,
            retry_handler=self._retry_handler)

    def _parse(self, page: str) -> List[str]:
        ret = []
        # TODO
        for para in enumerate(page):
            if len(ret) >= self.max_retrieval_num:
                break
        return ret

    def _retry_handler(self, res):
        if res.url.startswith('https://webpass.baidu.com/'):
            return True, '被百度墙了'
        return False, None
