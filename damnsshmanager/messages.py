import configparser


class Messages(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('damnfiles/messages.ini')

    def get(self, key, section='DEFAULT'):
        """Loads given key of a section inside the messages catalogue
        """
        if section not in self.config:
            print('section %s does not exist' % section)
            return

        if key not in self.config[section]:
            print('key %s not found in section %s' % (key, section))

        return self.config[section][key]
