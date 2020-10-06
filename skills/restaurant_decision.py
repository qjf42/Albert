#coding: utf-8
'''随机选一个地方吃饭'''

import random
from .base import BaseSkill
from ..interfaces import BaseRequest, SkillResponse, LexicalResult, IntentSlots, Session


class RestaurantDecisionSkill(BaseSkill):
    '''随机选一个地方吃饭，配置项为data/restaurants.txt'''
    def __init__(self, conf, logger):
        super().__init__(conf, logger)
        self.restaurants = []
        with open('data/restaurants.txt') as f:
            for line in f:
                if not line.strip() or line[0] == '#':
                    continue
                name, pref = line.strip().split()
                self.restaurants += [name] * int(pref)

    def __call__(self,
                 req: BaseRequest,
                 lexical_res: LexicalResult,
                 intent_slots: IntentSlots,
                 session: Session) -> SkillResponse:
        choice = self._random_choice()
        return SkillResponse().set_score(1).set_response(choice)

    def _random_choice(self):
        posts = ['走起', '吃吗', '走一个', '走一波', '吃不吃', '']
        return random.choice(self.restaurants) + random.choice(posts)
