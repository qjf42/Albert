# coding: utf-8

import logging
from .env import ENV 
from ..enums import EnumEnv


BOT_LOG_CONF = {
    'log_name': 'BOT',
    'log_level': logging.DEBUG if ENV == EnumEnv.DEV else logging.INFO,
    'log_file': 'log/main.log',
    'log_format': '%(levelname)s\t%(asctime)s\t%(remote_addr)s\t%(url)s : %(message)s',
}


NLU_LOG_CONF = {
    'log_name': 'NLU',
    'log_level': logging.DEBUG if ENV == EnumEnv.DEV else logging.INFO,
    'log_file': 'log/nlu.log',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}


SKILL_LOG_CONF = {
    'log_name': 'SKILLS',
    'log_level': logging.DEBUG if ENV == EnumEnv.DEV else logging.INFO,
    'log_file': 'log/skills.log',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
