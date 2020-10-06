#coding: utf-8

from ...conf import ENV
from ...enums import EnumEnv

MODEL_SERVICE_CONF = {
    'ip': '127.0.0.1',
    'port': 5502 if ENV == EnumEnv.PROD else 5512
}