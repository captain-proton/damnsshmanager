import os

from damnsshmanager import messages


class __Config:

    def __init__(self):

        self.home_dir = os.path.expanduser('~')
        self.app_dir = os.path.join(self.home_dir, '.damnsshmanager')
        if not os.path.exists(self.app_dir):
            os.mkdir(self.app_dir, mode=0o755)
        self.messages = messages.Messages()


Config = __Config()
