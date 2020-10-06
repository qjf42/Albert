#coding: utf-8

from .env import ENV
from ..enums import EnumSkill, EnumEnv


QA_CONF = {
    'qa_service': {
        'ip': '127.0.0.1',
        'port': 5501 if ENV == EnumEnv.PROD else 5511,
    },
}

SKILL_CONF_MAP = {
    EnumSkill.QA: QA_CONF,
}


def get_skill_conf(skill: EnumSkill):
    return SKILL_CONF_MAP.get(skill)
