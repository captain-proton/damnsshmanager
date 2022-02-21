import os
import tempfile
import time
from threading import Thread

import pytest
from paramiko import RSAKey

from damnsshmanager.hosts import Host
from damnsshmanager.ssh.paramiko import ParamikoChannel


@pytest.fixture
def private_key_file() -> str:
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '..', 'damn_key')
    return filename


def test_connect(private_key_file: str):

    private_key = RSAKey.from_private_key_file(private_key_file)
    with tempfile.NamedTemporaryFile() as temp_known_hosts:

        host = Host(alias='testhost', addr='localhost',
                    username='vagrant', port=2222)

        connector = ParamikoChannel(known_hosts_path=temp_known_hosts.name,
                                    pkey=private_key)
        t = Thread(target=lambda: connector.connect(host))
        t.start()
        time.sleep(5)
        connector.channel.send('logout\x0a')
