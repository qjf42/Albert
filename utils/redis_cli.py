#coding: utf-8

import json
from typing import List
import redis
from .message import ChatroomUsers, Message
from ..utils import time_utils
from ..conf import CONF


class RedisClient(redis.Redis):
    def __init__(self):
        super().__init__(host='127.0.0.1', port=6379)
        self.key_rec_msg_queue = CONF['redis']['key_rec_msg_queue']
        self.key_rec_sub_kw = CONF['redis']['key_rec_sub_kw']
        self.key_rec_user_sub_kw = CONF['redis']['key_rec_user_sub_kw']
        self.max_sub_time = 7 * 86400

    def push_msg(self, admin_id: str, msg_list: list):
        qname = f'{self.key_rec_msg_queue}:{admin_id}'
        current_ts = time_utils.DateTime().timestamp()
        msg_dic = {str(msg): current_ts for msg in msg_list}
        return self.zadd(qname, msg_dic, nx=True)

    def pull_msg(self, admin_id: str,
            top: int=5, max_time_window: int=300) -> List[Message]:
        current_ts = time_utils.DateTime().timestamp()
        lb = current_ts - max_time_window
        qname = f'{self.key_rec_msg_queue}:{admin_id}'
        with self.pipeline() as pipe:
            pipe.multi()
            # 1. 清掉队列中的过期消息
            pipe.zremrangebyscore(qname, 0, lb - 1)
            # 2. 拿最早的top条
            pipe.zpopmin(qname, top)
            _, items = pipe.execute()
            return [Message.parse(msg) for (msg, ts) in items]

    def _sub_kw_key(self, kw: str, admin_id: str):
        '''倒排key'''
        return f'{self.key_rec_sub_kw}:{kw}:admin_id:{admin_id}'

    def _user_sub_kw_key(self, user_id: str):
        '''正排key'''
        return f'{self.key_rec_user_sub_kw}:{user_id}'

    def add_sub(self, kw: str,
            admin_id: str, chatroom_id: str, user_id: str, user_name: str):
        current_ts = time_utils.DateTime().timestamp()
 
        # 正排key user->kw
        user_kw_key = self._user_sub_kw_key(user_id)
        # 倒排key kw->user
        kw_user_key = self._sub_kw_key(kw, admin_id)

        # 1. 获取当前所有的订阅词
        cur_kw_info = self.zrange(user_kw_key, 0, -1, withscores=True)
        """
        outdated_kw_num = len([t for t in cur_kw_info[1::2] if t <= current_ts - self.max_sub_time])
        kw_info_list = cur_kw_info[::2][outdated_kw_num:]
        MAX_SUB_NUM = 1
        del_kw_num = max(0, len(kw_info_list) + 1 - MAX_SUB_NUM)
        del_kws = [json.loads(kw_info.decode('utf-8'))['kw'] for kw_info in kw_info_list[:del_kw_num]]
        """
        outdated_kw_num = len([t for _, t in cur_kw_info if t <= current_ts - self.max_sub_time])
        kw_info_list = [info for info, _ in cur_kw_info[outdated_kw_num:]]
        MAX_SUB_NUM = 1
        del_kw_num = max(0, len(kw_info_list) + 1 - MAX_SUB_NUM)
        del_kws = [json.loads(kw_info.decode('utf-8'))['kw'] for kw_info in kw_info_list[:del_kw_num]]

        with self.pipeline() as pipe:
            pipe.multi()

            # 2. 从正排中清掉超过最大订阅量的订阅词
            if outdated_kw_num + del_kw_num > 0:
                pipe.zremrangebyrank(user_kw_key, 0, outdated_kw_num + del_kw_num - 1)
            # 3. 从倒排中清掉超过最大订阅量的订阅词
            for del_kw in del_kws:
                rm_value = json.dumps({
                    'chatroom_id': chatroom_id, 'user_id': user_id, 'user_name': user_name,
                })
                pipe.zrem(self._sub_kw_key(del_kw, admin_id), rm_value)
            # 4. 更新正排
            value = json.dumps({
                'kw': kw,
                'admin_id': admin_id,
                'chatroom_id': chatroom_id, 'user_name': user_name,
            })
            pipe.zadd(user_kw_key, {value: current_ts})
            # 5. 更新倒排
            value = json.dumps({
                'chatroom_id': chatroom_id, 'user_id': user_id, 'user_name': user_name,
            })
            pipe.zadd(kw_user_key, {value: current_ts})

            pipe.execute()

    def get_sub(self, kws: List[str], admin_id: str) -> List[ChatroomUsers]:
        # 1. 清掉所有过期的订阅
        with self.pipeline() as pipe:
            current_ts = time_utils.DateTime().timestamp()
            pipe.multi()
            for kw in kws:
                pipe.zremrangebyscore(self._sub_kw_key(kw, admin_id), 0, current_ts - self.max_sub_time)
            pipe.execute()
        # 2. 拿到所有订阅的用户
        with self.pipeline() as pipe:
            pipe.multi()
            for kw in kws:
                pipe.zrange(self._sub_kw_key(kw, admin_id), 0, -1)
            items = pipe.execute()

        ret = {}
        for users in items:
            for user_info in users:
                user_info = json.loads(user_info.decode('utf-8'))
                chatroom_id = user_info['chatroom_id']
                cht = ret.setdefault(chatroom_id, ChatroomUsers(chatroom_id))
                cht.user_ids.append(user_info['user_id'])
                cht.user_names.append(user_info['user_name'])
        return list(ret.values())

    def unsub(self, kws: List[str], admin_id: str, user_id: str) -> List[str]:
        # 正排key user->kw
        user_kw_key = self._user_sub_kw_key(user_id)
        # 1. 正排，获取所有订阅
        all_kw_info = self.zrange(user_kw_key, 0, -1, withscores=False)
        all_kws = [json.loads(kw_info.decode('utf-8'))['kw'] for kw_info in all_kw_info]
        hit_ids = [i for i, kw in enumerate(all_kws) if kw in kws]
        hit_kws = [all_kws[i] for i in hit_ids] or all_kws
        del_all = set(all_kws) == set(all_kws)
        # 2. 获取倒排记录
        rev_rec_dic = {}
        for kw in hit_kws:
            kw_user_key = self._sub_kw_key(kw, admin_id)
            rec = self.zrange(kw_user_key, 0, -1)
            for user_info in rec:
                if json.loads(user_info.decode('utf-8'))['user_id'] == user_id:
                    rev_rec_dic.setdefault(kw_user_key, []).append(user_info)

        with self.pipeline() as pipe:
            pipe.multi()
            # 3. 删除正排记录
            # 没有命中，取消所有订阅
            if del_all:
                pipe.delete(user_kw_key)
            else:
                for hit_id in hit_ids:
                    pipe.zremrangebyrank(user_kw_key, hit_id, hit_id)
            # 4. 删除倒排记录
            for k, vs in rev_rec_dic.items():
                for v in vs:
                    pipe.zrem(k, v)
            pipe.execute()

        return hit_kws