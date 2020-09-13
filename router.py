#coding: utf-8

from .enums import EnumIntent, EnumSkill
from .skills import BaseSkill, SkillFactory
from .conf import get_skill_conf


class Router:
    '''将意图路由到具体的技能'''
    def __init__(self, skill_log_conf):
        # 意图 => 技能
        self.intent2skill = {
            EnumIntent.QA: EnumSkill.QA,
            EnumIntent.DOUTU: EnumSkill.DOUTU,
            EnumIntent.RANDOM_RESTAURANT: EnumSkill.RANDOM_RESTAURANT,
        }
        self.skill_factory = SkillFactory(skill_log_conf)

    def route(self, intent: EnumIntent) -> BaseSkill:
        # QA作为兜底
        skill = self.intent2skill.get(intent, EnumSkill.QA)
        conf = get_skill_conf(skill)
        return self.skill_factory.get_skill(skill, conf)
