# coding: utf-8

from ..enums import EnumSkill
from .base import BaseSkill
from .doutu import DoutuSkill
from .qa import QASkill
from .restaurant_decision import RestaurantDecisionSkill
from ..utils.log_utils import get_logger


# 技能enum => 技能类
SKILL_MAP = {
    EnumSkill.QA: QASkill,
    EnumSkill.DOUTU: DoutuSkill,
    EnumSkill.RANDOM_RESTAURANT: RestaurantDecisionSkill,
}


class SkillFactory:
    '''技能实例的工厂类'''
    def __init__(self, log_conf):
        self._single_instances = {}
        self.logger = get_logger(**log_conf)

    def get_skill(self, enum_skill: EnumSkill, skill_conf) -> BaseSkill:
        '''单例工厂方法'''
        if enum_skill in self._single_instances:
            return self._single_instances[enum_skill]
        ins = SKILL_MAP[enum_skill](skill_conf, self.logger)
        self._single_instances[enum_skill] = ins
        return ins
