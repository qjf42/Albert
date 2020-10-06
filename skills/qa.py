# coding: utf-8
'''问答技能'''

from typing import List
from .base import BaseSkill
from ..enums import EnumResponseError
from ..interfaces import BaseRequest, SkillResponse, LexicalResult, IntentSlots, Session
from ..utils.downloader import Downloader
from ..utils import time_utils


class QASkill(BaseSkill):
    '''问答技能'''
    def __init__(self, conf, log_conf):
        super().__init__(conf, log_conf)
        self._qa_cli = Downloader()
        self.qa_service_url = f"http://{conf['qa_service']['ip']}:{conf['qa_service']['port']}/ask"

    def __call__(self,
                 req: BaseRequest,
                 lexical_res: LexicalResult,
                 intent_slots: IntentSlots,
                 session: Session) -> SkillResponse:
        ret = SkillResponse()
        ts = time_utils.DateTime().timestamp()
        try:
            # 请求qa服务
            qa_res = self._ask_qa(req.utterance, lexical_res, list(session.utterances))
            response = qa_res['response']
            skill_result = qa_res['skill_result']
            # 更新session
            session.extend_utterances([req.utterance, response['value']], [ts, ts])
            # 返回
            return ret.set_score(skill_result['score'])\
                      .set_skill_result(skill_result)\
                      .set_response(response)
        except Exception as e:
            return ret.set_error(EnumResponseError.SKILL_ERROR, str(e))

    def _ask_qa(self, query: str, lexical_res: LexicalResult, history: List[str]):
        try:
            res = self._qa_cli.download(
                self.qa_service_url,
                req_type='POST',
                json_data={
                    'query': query,
                    'lexical_res': lexical_res.to_dict(),
                    'history': history,
                },
                json=True
            )
            assert res['success'], res['err_msg']
            return res['data']
        except Exception as e:
            raise Exception('QAService error: %s.' % e)
