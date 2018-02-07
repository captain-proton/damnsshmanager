import configparser
from pkg_resources import resource_string


class Messages(object):
    def __init__(self):
        content = resource_string(__name__, 'damnfiles/messages.ini')
        content = content.decode('utf-8')

        self.config = configparser.ConfigParser()
        self.config.read_string(content)

    def get(self, key, *args, section='DEFAULT', **kwargs):
        """Loads given key of a section inside the messages catalogue
        """
        if section not in self.config:
            print('section %s does not exist' % section)
            return

        if key not in self.config[section]:
            print('key %s not found in section %s' % (key, section))

        msg = self.config[section][key]
        return msg.format(*args, **kwargs)
