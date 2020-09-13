# coding: utf-8
'''召回数据来源'''

from enum import Enum


class EnumRetrievalSource(Enum):
    TERM = 'term'       # 文档索引
    ANN = 'ANN'         # 向量索引
    KB = 'KB'           # 知识库
    SEARCH = 'search'   # 搜索
