import os
from damnsshmanager.config import Config


def test_valid_config_dir_exists():
    assert os.path.exists(Config.app_dir)


def test_valid_config_dir():
    assert os.path.isdir(Config.app_dir)


def test_valid_config_dir_writeable():
    assert os.access(Config.app_dir, os.W_OK)
