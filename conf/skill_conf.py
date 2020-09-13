#coding: utf-8

from .env import ENV
from ..enums import EnumSkill, EnumEnv


qa_service_port = '5501' if ENV == EnumEnv.PROD else '5511'
QA_CONF = {
    'qa_service_url': f'http://127.0.0.1:{qa_service_port}/ask'
}

SKILL_CONF_MAP = {
    EnumSkill.QA: QA_CONF,
}


def get_skill_conf(skill: EnumSkill):
    return SKILL_CONF_MAP.get(skill)
