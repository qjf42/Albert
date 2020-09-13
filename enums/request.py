# coding: utf-8
'''请求来源'''

from enum import Enum


class EnumRequestSrcType(Enum):
    NLU = 'nlu'     # NLU only
    CMD = 'cmd'     # 命令行模式
    WECHAT = 'wx'   # 微信
    DINGDING = 'dd' # 钉钉
