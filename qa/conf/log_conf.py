# coding: utf-8

import logging
from ...enums import EnumEnv
from ...conf import ENV


LOG_CONF = {
    'log_name': 'QA',
    'log_level': logging.DEBUG if ENV == EnumEnv.DEV else logging.INFO,
    'log_file': 'log/main.log',
    'log_format': '%(levelname)s\t%(asctime)s\t%(remote_addr)s\t%(url)s : %(message)s',
}
