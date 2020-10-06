# coding: utf-8

import json
import redis
from collections import deque
from ..utils import time_utils
from ..enums import EnumRequestSrcType
from ..interfaces import Session


class RedisClient(redis.Redis):
    '''通过redis的hashmap存储session结构'''
    def __init__(self, redis_conf, session_conf):
        super().__init__(host=redis_conf['host'], port=redis_conf['port'])
        self.session_key = session_conf['session_key']

    def _get_key(self, src: EnumRequestSrcType, key: str):
        return f'{self.session_key}:{src.value}:{key}'

    def get(self, src: EnumRequestSrcType, key: str) -> Session:
        sess_key = self._get_key(src, key)
        utterances, ts = self.hmget(sess_key, ['utterances', 'timestamps'])
        if not ts:
            return Session()
        utterances = json.loads(utterances)
        ts = json.loads(ts)
        return Session(deque(utterances), deque(ts))

    def set(self, src: EnumRequestSrcType, key: str, sess: Session, expire: int) -> None:
        # session为空或未更新
        if not sess or not sess.updated_fields:
            return
        sess_key = self._get_key(src, key)
        sess_dic = sess.to_dict()
        sess_dic = {k: json.dumps(sess_dic[k], ensure_ascii=False) for k in sess.updated_fields}
        with self.pipeline() as pipe:
            pipe.multi()
            pipe.hmset(sess_key, sess_dic)
            pipe.expire(sess_key, expire)
            pipe.execute()


class SessionManager:
    '''Session查询和更新工具'''
    def __init__(self, session_conf, redis_conf):
        self._redis = RedisClient(redis_conf, session_conf)
        self.max_turn = session_conf['max_turn']
        self.max_expire = session_conf['max_expire']

    def get(self, src: EnumRequestSrcType, key: str) -> Session:
        '''获取session
        Args:
            src: 请求来源
            key: 可以是user_id或是chatgroup_id
        Returns:
            `interfaces.Session`
        '''
        sess = self._redis.get(src, key)
        min_ts = time_utils.DateTime().timestamp() - self.max_expire
        sess.clip(max_turn=self.max_turn, min_ts=min_ts)
        return sess

    def set(self, src: EnumRequestSrcType, key: str, sess: Session) -> None:
        '''设置session
        Args:
            src: 请求来源
            key: 可以是user_id或是chatgroup_id
            sess: interfaces.Session
        '''
        sess.clip(max_turn=self.max_turn)
        self._redis.set(src, key, sess, self.max_expire)

    def persist(self):
        pass
