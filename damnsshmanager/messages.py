import configparser
from dataclasses import dataclass
from pkg_resources import resource_string
from loguru import logger


@dataclass
class Messages(object):

    config: configparser.ConfigParser = None

    def __init__(self):
        content = resource_string(__name__, 'damnfiles/messages.ini')
        content = content.decode('utf-8')

        self.config = configparser.ConfigParser()
        self.config.read_string(content)

    def get(self, key, *args, section='DEFAULT', **kwargs):
        """Loads given key of a section inside the messages catalogue
        """
        if section not in self.config:
            logger.error('Section %s does not exist' % section)
            return

        if key not in self.config[section]:
            logger.error('Key %s not found in section %s' % (key, section))
            return None

        msg = self.config[section][key]
        return msg.format(*args, **kwargs)
