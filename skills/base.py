#coding: utf-8

from ..interfaces import BaseRequest, SkillResponse, LexicalResult, IntentSlots, Session


class BaseSkill:
    '''技能的基类'''
    def __init__(self, conf, logger):
        self.logger = logger

    def __call__(self,
                 req: BaseRequest,
                 lexical_res: LexicalResult,
                 intent_slots: IntentSlots,
                 session: Session) -> SkillResponse:
        raise NotImplementedError
