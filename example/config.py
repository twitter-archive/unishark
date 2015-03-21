import logging
import logging.config
import yaml
import os


class Configuration(object):
    def __init__(self):
        self.conf_dir = 'config'
        self._set_logging()

    def _set_logging(self):
        with open(os.path.join(self.conf_dir, 'logging.yaml'), mode='r') as f:
            logging.config.dictConfig(yaml.load(f.read()))