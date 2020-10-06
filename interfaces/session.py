# coding: utf-8
'''Session相关的数据结构和接口'''

from collections import deque
from typing import List, Dict, Any, Deque, Set
from dataclasses import dataclass, field, asdict
from .nlu import IntentSlots, MultiTurnNLUResult
from ..enums import EnumIntent
from ..utils import time_utils


@dataclass
class Session:
    # 非任务类对话历史
    utterances: Deque[str] = field(default_factory=deque)
    timestamps: Deque[int] = field(default_factory=deque)
    # 多轮NLU结果(TODO)
    multi_nlu: MultiTurnNLUResult = field(default_factory=MultiTurnNLUResult)
    nlu_timestamps: Dict[EnumIntent, int] = field(default_factory=dict)

    updated_fields: Set[str] = field(default_factory=set)

    def __len__(self):
        return len(self.utterances)

    def __bool__(self):
        return len(self.utterances) > 0

    def popleft_utterances(self, k: int):
        for _ in range(k):
            self.utterances.popleft()
            self.timestamps.popleft()
        if k > 0:
            self.updated_fields |= {'utterances', 'timestamps'}

    def extend_utterances(self, utterances: List[str], timestamps: List[int]):
        self.utterances.extend(utterances)
        self.timestamps.extend(timestamps)
        self.updated_fields |= {'utterances', 'timestamps'}

    def update_multi_nlu(self, intent_slots: IntentSlots = None):
        self.multi_nlu.update_intent_slots(intent_slots)
        self.nlu_timestamps[intent_slots.intent] = time_utils.DateTime().timestamp()
        self.updated_fields |= {'multi_nlu', 'nlu_timestamps'}

    def clip(self, max_turn: int = None, min_ts: int = None) -> None:
        if min_ts is not None:
            try:
                clip_num = next(i for i, ts in enumerate(self.timestamps) if ts >= min_ts)
                self.popleft_utterances(clip_num)
            except:
                self.utterances.clear()
                self.timestamps.clear()
                self.updated_fields |= {'utterances', 'timestamps'}
            intents_to_del = [intent for intent, ts in self.nlu_timestamps.items() if ts < min_ts]
            for intent in intents_to_del:
                self.multi_nlu.remove(intent)
                del self.nlu_timestamps[intent]
            if intents_to_del:
                self.updated_fields |= {'multi_nlu', 'nlu_timestamps'}

        if max_turn is not None:
            self.popleft_utterances(len(self) - max_turn)

    def to_dict(self) -> Dict[str, Any]:
        ret = {}
        for k, v in asdict(self).items():
            # 方便json序列化
            if isinstance(v, deque):
                v = list(v)
            ret[k] = v
        return ret
