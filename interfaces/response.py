# coding: utf-8
'''服务响应'''

from dataclasses import dataclass, field
from typing import Any, Dict, Union
from ..enums import EnumResponseError, EnumResponseType


@dataclass
class ResponseBase:
    success: bool = True
    err_no: int = EnumResponseError.SUCCESS.err_no
    err_msg: str = None
    data: Dict = field(default_factory=dict)

    def add_data(self, k: str, v: Any):
        # XXX
        if not isinstance(v, (str, int, float, dict, list, tuple)):
            v = str(v)
        self.data[k] = v
        return self

    def set_query(self, query: str):
        return self.add_data('query', query)

    def set_error(self, err: EnumResponseError, err_msg: str = None):
        self.success = err.success
        self.err_no = err.err_no
        self.err_msg = err_msg or err.err_msg
        return self

    @property
    def response(self) -> Dict[str, Any]:
        return self.data.get('response')

    def set_response(self, value: str, type: Union[str, EnumResponseType] = EnumResponseType.TEXT):
        if isinstance(type, EnumResponseType):
            type = type.type
        return self.add_data('response', {
            'type': type,
            'value': value,
        })

    def add_debug(self, k: str, v, append=False):
        debug_info = self.data.setdefault('debug', {})
        # XXX
        if not isinstance(v, (str, int, float, dict, list, tuple)):
            v = str(v)
        if append:
            debug_info.setdefault(k, []).append(v)
        else:
            debug_info[k] = v
        return self


@dataclass
class BotResponse(ResponseBase):
    '''机器人服务返回'''
    pass


@dataclass
class SkillResponse(ResponseBase):
    '''技能返回'''
    score: float = 0.

    def set_score(self, score: float):
        self.score = score
        return self

    def set_skill_result(self, skill_result: Dict[str, Any]):
        return self.add_data('skill_result', skill_result)
