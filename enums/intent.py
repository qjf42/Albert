# coding: utf-8
'''意图'''

from enum import Enum


class EnumIntent(Enum):
    DOUTU = 'doutu'
    RANDOM_RESTAURANT = 'random_restaurant'
    QA = 'QA'

    @classmethod
    def from_value(cls, value: str):
        return next(v for v in cls.__members__.values() if v.value == value)
