# coding: utf-8

from .base import BaseSkill
from ..enums import EnumResponseError
from ..interfaces import BaseRequest, SkillResponse, LexicalResult, IntentSlots
from ..utils.downloader import Downloader


class QASkill(BaseSkill):
    def __init__(self, conf, log_conf):
        super().__init__(conf, log_conf)
        self._qa_cli = Downloader()
        self.qa_service_url = conf['qa_service_url']

    def __call__(self,
                 req: BaseRequest,
                 lexical_res: LexicalResult,
                 intent_slots: IntentSlots) -> SkillResponse:
        ret = SkillResponse()
        try:
            qa_res = self._ask_qa(req.utterance, lexical_res)
            return ret.set_score(qa_res['score'])\
                      .set_skill_result(qa_res['detail'])\
                      .set_response(qa_res['response'])
        except Exception as e:
            return ret.set_error(EnumResponseError.SKILL_ERROR, str(e))

    def _ask_qa(self, query: str, lexical_res: LexicalResult):
        try:
            return self._qa_cli.download(
                self.qa_service_url,
                req_type='POST',
                data={'query': query, 'lexical_res': lexical_res.to_dict()},
                json=True
            )
        except Exception as e:
            raise Exception('QAService error: %s.' % e)
