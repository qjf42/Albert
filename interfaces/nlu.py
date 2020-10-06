# coding: utf-8
'''NLU相关的数据结构和接口'''

from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
from ..enums import EnumIntent


@dataclass
class Token:
    '''词'''
    word: str   # 值
    pos: str    # 词性
    start: int  # char start
    end: int    # char end


@dataclass
class Entity:
    '''实体'''
    value: str  # 值
    type: str   # 实体类型
    start: int  # 对应的token start
    end: int    # 对应的token end


@dataclass
class LexicalResult:
    # 普通粒度切词
    tokens: List[Token]
    # NER
    entities: List[Entity] = field(default=None)
    # 细粒度切词
    search_tokens: List[Token] = field(default=None)
    keywords: List[str] = field(default=None)
   
    @classmethod
    def from_dict(cls, dic: Dict[str, List]):
        return cls(
            tokens=[Token(**p) for p in dic['tokens']],
            entities=[Entity(**p) for p in dic.get('entities', [])] or None,
            search_tokens=[Token(**p) for p in dic.get('search_tokens', [])] or None,
            keywords=dic.get('keywords', []) or None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Slot:
    key: str
    value: str
    start: int  # span start
    end: int    # span end


@dataclass
class IntentSlots:
    '''意图槽位'''
    intent: EnumIntent
    slots: List[Slot]
    score: float

    def get_slot_values(self, key: str) -> List[str]:
        return [slot.value for slot in self.slots if slot.key == key]

    @classmethod
    def from_dict(cls, dic: Dict[str, Any]):
        return cls(
            intent=EnumIntent.from_value(dic['intent']),
            slots=[Slot(**p) for p in dic['slots']],
            score=dic['score'],
        )


@dataclass
class SingleTurnNLUResult:
    '''单轮对话NLU结果'''
    parser_name: str
    intent_slots_list: List[IntentSlots] = field(default_factory=list)
    debug: Dict[str, Any] = field(default_factory=dict)

    def add_intent_slots(self, intent_slots: IntentSlots):
        self.intent_slots_list.append(intent_slots)
        return self

    def add_debug(self, k, v, append=False):
        if append:
            self.debug.setdefault(k, []).append(v)
        else:
            self.debug[k] = v
        return self

    @classmethod
    def from_dict(cls, dic: Dict[str, Any]):
        return cls(
            parser_name=dic['parser_name'],
            intent_slots_list=[IntentSlots.from_dict(p) for p in dic.get('intent_slots_list', [])],
            debug=dic.get('debug', {}),
        )


@dataclass
class MultiTurnNLUResult:
    '''TODO 多轮对话NLU结果'''
    intent_slots_dic: Dict[EnumIntent, IntentSlots] = field(default_factory=dict)
    debug: Dict[str, Any] = field(default_factory=dict)

    def get_intent_slots(self, intent: EnumIntent) -> IntentSlots:
        return self.intent_slots_dic.get(intent)

    def update_intent_slots(self, intent_slots: IntentSlots):
        self.intent_slots_dic[intent_slots.intent] = intent_slots
        return self

    def remove(self, intent: EnumIntent):
        del self.intent_slots[intent]
        return self

    def add_debug(self, k, v, append=False):
        if append:
            self.debug.setdefault(k, []).append(v)
        else:
            self.debug[k] = v
        return self

    @classmethod
    def from_dict(cls, dic: Dict[str, Any]):
        intent_slots_list = [IntentSlots.from_dict(p) for p in dic.get('intent_slots_list', [])]
        return cls(
            intent_slots_dic={v.intent: v for v in intent_slots_list},
            debug=dic.get('debug', {}),
        )
