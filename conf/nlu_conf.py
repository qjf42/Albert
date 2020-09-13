# coding: utf-8

from ..enums import EnumIntent


NLU_CONF = {
    'lexical': {
        'wordseg': {
            'segger': 'jieba',  # jieba/thulac
            't2s': True,        # jieba暂不支持
        },
    },
    'template': {
        EnumIntent.DOUTU: {
            'dict_file': 'dict/template/doutu.dict',
            'template_file': 'dict/template/doutu.tpl',
        },
        EnumIntent.RANDOM_RESTAURANT: {
            'dict_file': 'dict/template/restaurant.dict',
            'template_file': 'dict/template/restaurant.tpl',
        },
    },
}
