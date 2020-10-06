# coding: utf-8
'''请求体'''

import re
from ..utils import time_utils
from ..enums import EnumRequestSrcType


__all__ = ['BaseRequest', 'RequestFactory']


class BaseRequest:
    src_type = None
    def __init__(self, msg: str,
                 user_id: str = None, user_name: str = None, chatgroup_id = None,
                 debug: bool = False):
        self.user_id = user_id
        self.user_name = user_name
        self.chatgroup_id = chatgroup_id
        self.time = time_utils.DateTime().timestamp()
        self._parse(msg)

        self.debug = debug

    def _parse(self, msg):
        self.utterance = msg.strip()
        self.at_users = []

    def to_dict(self):
        ret = {
            'src_type': self.src_type.value,
            'user_id': self.user_id,
        }
        if self.user_name:
            ret['user_name'] = self.user_name
        if self.chatgroup_id:
            ret['chatgroup_id'] = self.chatgroup_id
        return ret


class NLURequest(BaseRequest):
    src_type = EnumRequestSrcType.NLU
    def __init__(self, msg: str, debug: bool=False):
        super().__init__(msg, debug=debug)


class CmdLineRequest(BaseRequest):
    src_type = EnumRequestSrcType.CMD
    def __init__(self, msg: str, debug: bool=False):
        super().__init__(msg, user_id='我', debug=debug)


PAT_WECHAT_AT = re.compile('(@([^\s]+)\s+)')
class WechatRequest(BaseRequest):
    src_type = EnumRequestSrcType.WECHAT

    def _parse(self, msg):
        global PAT_WECHAT_AT
        self.at_users = [_.group(2) for _ in PAT_WECHAT_AT.finditer(msg)]
        self.utterance = PAT_WECHAT_AT.sub('', msg).strip()


class DingdingRequest(BaseRequest):
    src_type = EnumRequestSrcType.DINGDING


class RequestFactory:
    @staticmethod
    def get_request(src_type: EnumRequestSrcType, 
                    msg: str, user_id: str = None, user_name: str=None, chatgroup_id=None,
                    debug: bool=False) -> BaseRequest:
        if src_type == EnumRequestSrcType.NLU:
            return NLURequest(msg, debug=debug)
        elif src_type == EnumRequestSrcType.CMD:
            return CmdLineRequest(msg, debug=debug)
        elif src_type == EnumRequestSrcType.WECHAT:
            assert user_id is not None
            return WechatRequest(msg, user_id, user_name, chatgroup_id, debug=debug)
        elif src_type == EnumRequestSrcType.DINGDING:
            assert user_id is not None
            return DingdingRequest(msg, debug=debug)
