__author__ = 'Ying Ni <yni@twitter.com>'

import logging
import logging.config
import unishark
import yaml


class Configuration(object):
    def __init__(self):
        self._conf_path = './config'
        self._set_logging()

    def _set_logging(self):
        logging.unishark = unishark
        with open(self._conf_path + '/logging.yaml', mode='r') as f:
            logging.config.dictConfig(yaml.load(f.read()))