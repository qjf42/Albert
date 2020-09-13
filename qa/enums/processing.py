# coding: utf-8
'''处理方式'''

from enum import Enum


class EnumProcessorType(Enum):
    MATCHING = 'matching'                       # 语义匹配
    S2S = 'seq2seq'                             # 闲聊seq2seq
    EXTRACTIVE_SUMMARIZER = 'summary_ext'       # 抽取式摘要
    ABSTRACTIVE_SUMMARIZER = 'summary_seq2seq'  # 生成式摘要
    KBQA_ENTITY = 'kbqa_entity'                 # KBQA抽取实体
    KBQA_S2S = 'kbqa_seq2seq'                   # KBQA自由问答
    MRC_SPAN = 'mrc_span'                       # MRC抽取片段
    MRC_S2S = 'mrc_seq2seq'                     # MRC自由问答
