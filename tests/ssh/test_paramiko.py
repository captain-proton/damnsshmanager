import sys
from typing import TextIO

from damnsshmanager.hosts import Host
from damnsshmanager.ssh import ParamikoConnector


def test_connect():
    host = Host(alias='testhost', addr='localhost',
                username='robey', port=2200)
    connector = ParamikoConnector()
    connector.connect(host)
    comm = TextIO()
    comm.write('yes')
