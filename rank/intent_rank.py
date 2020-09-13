# coding: utf-8
'''意图排序'''

from ..enums import EnumIntent
from ..interfaces import BaseRequest, IntentSlots, SingleTurnNLUResult


class IntentRank:
    '''意图排序'''
    def __init__(self):
        self._intent_priority = {
            EnumIntent.RANDOM_RESTAURANT: 2,
        }

    def rank(self, req: BaseRequest, single_turn_nlu_res: SingleTurnNLUResult) -> None:
        '''简单根据每个意图自定义的分数排序'''
        single_turn_nlu_res.intent_slots_list.sort(
                key=lambda _: self._score_fn(req, _),
                reverse=True)

    def _score_fn(self, req: BaseRequest, intent_slots: IntentSlots) -> float:
        '''简单根据意图的置信分和先验优先级计算'''
        return intent_slots.score * self._intent_priority.get(intent_slots.intent, 1)
