import os
from dataclasses import dataclass

from appdirs import user_config_dir

from . import messages


@dataclass
class __Config:

    app_dir: str = ''

    def __init__(self):

        self.app_dir = user_config_dir('damnsshmanager')
        if not os.path.exists(self.app_dir):
            os.mkdir(self.app_dir, mode=0o755)
        self.messages = messages.Messages()


Config = __Config()
