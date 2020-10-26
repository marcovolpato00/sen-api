import os
from typing import Optional
import configparser

from loguru import logger


__all__ = [
    'Config',
    'CONFIG_BASE_PATH',
    'CONFIG_FILE_NAME'
]


CONFIG_BASE_PATH = os.path.expanduser('~/.config/sen-api')
CONFIG_FILE_NAME = 'config.ini'


class Config(object):
    def __init__(self, base_path=CONFIG_BASE_PATH, config_file_name=CONFIG_FILE_NAME):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        self.base_path = base_path
        self.path = os.path.join(base_path, config_file_name)
        self._config = configparser.ConfigParser()

    def load(self) -> bool:
        """
        :return: True if config loaded successfully
        """
        if not os.path.isfile(self.path):
            logger.debug('Configuration file not found, skipping')
            return False
        self._config = configparser.ConfigParser()
        with open(self.path, 'r') as f:
            logger.debug('Reading configuration file...')
            self._config.read_file(f)
        return True

    def write(self, section: str, values: dict):
        logger.debug('Writing config...')
        for key in values.keys():
            if not self._config.has_section(section):
                self._config.add_section(section)
            self._config[section][key] = values[key]
        with open(self.path, 'w') as f:
            self._config.write(f)

    def get_value(self, section: str, value: str, fallback=None) -> Optional:
        return self._config.get(section, value, fallback=fallback)
