#coding: utf-8

from datetime import datetime


class DateTime:
    '''datetime工具类，适配几种常见的输入输出'''
    def __init__(self, dt_repr=None, ms_timestamp=False):
        if dt_repr is None:
            self.dt = datetime.now()
        elif dt_repr.isnumeric():
            dt_repr = int(dt_repr)
            if ms_timestamp:
                dt_repr /= 1000
            self.dt = datetime.fromtimestamp(dt_repr)
        elif isinstance(dt_repr, str):
            # yyyy-mm-dd HH:MM:SS
            # ES yyyy-mm-ddTHH:MM:DD.(ms)
            dt_repr = dt_repr.split('.')[0].replace('T', ' ').replace('/', '-')
            self.dt = datetime.strptime(dt_repr, '%Y-%m-%d %H:%M:%S')
        elif isinstance(dt_repr, datetime.datetime):
            self.dt = dt_repr

    def timestamp(self, local=True, ms=False) -> int:
        ts = self.dt.timestamp()
        if not local: #gmtime
            ts -= 28800
        if ms:
            ts *= 1000
        return int(ts)

    def datetime(self) -> datetime:
        return self.dt
