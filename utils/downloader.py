#coding: utf-8

import time
import requests
from typing import Dict, Tuple, Callable


UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'


class Downloader:
    '''http请求工具类'''
    def __init__(self, timeout: float = 1, retry: int = 3, headers: Dict[str, str] = None, **kwargs):
        self.timeout = timeout
        self.retry = retry
        self._session = requests.Session()
        self.headers = headers or {}

    def download(self, url: str, params: Dict = None, data: Dict = None, json_data: Dict = None,
                 req_type: str = 'GET', headers: Dict = None, json: bool = False, 
                 retry_handler: Callable[[requests.Response], Tuple[bool, str]] = None):
        '''
        Args:
            url: url
            params: url参数
            data: 请求体
            json_data: json请求体
            req_type: GET/POST/...
            headers: http headers
            json: bool(default false)，是否返回json
            retry_handler: optional, 回调函数，验证返回是否有效或需要重试，lambda res: (need_retry, msg)
        '''
        headers = headers or self.headers
        # requests中data和json只能有一个，而且content_type不同
        if json_data and data:
            json_data.update(data)
            data = None
        for atmpt in range(1, self.retry + 1):
            try:
                res = self._session.request(req_type.upper(), url,
                                            params=params, data=data, json=json_data,
                                            headers=headers, timeout=self.timeout)
                res.raise_for_status()
                if json:
                    content = res.json()
                else:
                    if res.encoding == 'ISO-8859-1':# or res.apparent_encoding.lower().startswith('gb'):
                        res.encoding = res.apparent_encoding
                    content = res.text
                # res_url = res.url
                if retry_handler is not None:
                    need_retry, msg = retry_handler(res)
                    if need_retry:
                        raise Exception(msg)
                return content
            except Exception as e:
                # logger.warning(f'Failed to download url[{url}], params[{params}], data[{data}], tried {atmpt} times, error: {e}.')
                time.sleep(self.timeout)
        else:
            # logger.warning(f'Failed to download url[{url}], params[{params}], data[{data}], tried {self.retry} times.')
            return
