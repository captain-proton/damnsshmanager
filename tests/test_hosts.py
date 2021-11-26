import os
import tempfile
import pytest

import damnsshmanager.hosts as hosts
from damnsshmanager.storage import Store


@pytest.fixture(scope="function")
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_file = os.path.join(tmpdir, 'damnsshmanager.test.store')
        hosts._store = Store(storage_file)
        yield hosts._store


def test_add(store):
    hosts.add(alias='a', addr='127.0.0.1')


def test_invalid_add(store):

    with pytest.raises(KeyError):
        hosts.add()


def test_invalid_alias(store):

    with pytest.raises(KeyError):
        hosts.add(addr='localhost')


def test_invalid_addr(store):

    with pytest.raises(KeyError):
        hosts.add(alias='a')


def test_duplicate_add(store):
    hosts.add(alias='a', addr='127.0.0.1')
    with pytest.raises(KeyError):
        hosts.add(alias='a', addr='127.0.0.1')


def test_get(store):
    hosts.add(alias='a', addr='127.0.0.1')
    host = hosts.get_host('a')
    assert host.addr == '127.0.0.1'


def test_delete(store):
    hosts.add(alias='a', addr='127.0.0.1')
    hosts.delete('a')
    host = hosts.get_host('a')
    assert host is None


def test_delete_unknown(store):
    hosts.add(alias='a', addr='127.0.0.1')
    hosts.delete('b')
    all_hosts = hosts.get_all_hosts()
    assert len(all_hosts) == 1
