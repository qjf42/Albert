# coding: utf-8
'''斗图专用，搜表情技能'''

import json
import numpy as np
import parsel
from .base import BaseSkill
from ..enums import EnumResponseType, EnumResponseError
from ..interfaces import BaseRequest, SkillResponse, LexicalResult, IntentSlots, Session
from ..utils.downloader import Downloader
from ..utils.time_utils import DateTime


class DoutuSkill(BaseSkill):
    '''斗图专用，搜表情技能'''
    def __init__(self, conf, logger):
        super().__init__(conf, logger)
        self._dl = Downloader()

    def __call__(self,
                 req: BaseRequest,
                 lexical_res: LexicalResult,
                 intent_slots: IntentSlots,
                 session: Session) -> SkillResponse:
        ret = SkillResponse()
        query = intent_slots.get_slot_values('query')[0]
        try:
            img_url = self._search_sogo(query)
            # img_url = self._search_dbbqb(query)
        except Exception as e:
            return ret.set_error(EnumResponseError.SKILL_ERROR, str(e))
        return ret.set_score(1).set_response(img_url, EnumResponseType.IMG)

    def _search_dbbqb(self, query) -> str:
        url = 'http://www.dbbqb.com/s'
        html = self._dl.download(url, params={'w': query}, json=False)
        doc = parsel.Selector(text=html)
        items = doc.css('a.jss148')[:5]
        ids = [_.get().rsplit('/', 1)[-1].split('.')[0] for _ in items.xpath('.//@href')]
        # alts = [_.get() for _ in items.xpath('.//img//@alt')]
        if not ids:
            raise Exception('没搜到表情。。')

        rand_idx = np.random.randint(len(ids))
        img_src = f'http://image.bee-ji.com/{ids[rand_idx]}'
        # img_alt = alts[rand_idx]
        return img_src

    def _search_sogo(self, query) -> str:
        url = 'https://pic.sogou.com/pics/json.jsp'
        ts = DateTime().timestamp(ms=True)
        params = {
            'callback': f'jQuery311030979365987315033_{ts-1}',
            'query': query + ' 表情',
            'st': 5, 'start': 0, 'xml_len': 60,
            'reqFrom': 'wap_result',
            '_': ts,
        }
        res = self._dl.download(url, params=params, json=False)    # jsonp
        items = json.loads(res.split('(', 1)[1][:-2]).get('items', [])
        if not items:
            raise Exception('没搜到表情。。')
        items = items[:5]
        img_src = np.random.choice(items)['oriPicUrl']
        return img_src
