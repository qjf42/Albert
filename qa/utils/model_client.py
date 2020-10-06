# coding: utf-8

from typing import Any, Dict
from ..conf import MODEL_SERVICE_CONF
from ...utils.downloader import Downloader


class ModelClient(Downloader):
    '''ModelServer的客户端'''
    def __init__(self, timeout: float = 1, retry: int = 3, **kwargs):
        super().__init__(timeout=timeout, retry=retry)
        self.url = f"http://{MODEL_SERVICE_CONF['ip']}:{MODEL_SERVICE_CONF['port']}/infer"

    def request(self, model_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        data = params.copy()
        data['model_name'] = model_name
        ret = self.download(self.url, data=data, json=True)
        assert ret['success'], ret['err_msg']
        return ret['data']
