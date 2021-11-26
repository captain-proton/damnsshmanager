import os
import socket
import tempfile
import pytest

from loguru import logger
import damnsshmanager.localtunnel as tun
import damnsshmanager.hosts as hosts
import damnsshmanager.storage as storage


@pytest.fixture(scope="function")
def stores():
    with tempfile.TemporaryDirectory() as tmpdir:
        hosts_storage_file = os.path.join(tmpdir, 'damnsshmanager.host.test.store')
        tun_storage_file = os.path.join(tmpdir, 'damnsshmanager.tun.test.store')

        hosts._store = storage.Store(hosts_storage_file)
        tun._store = storage.Store(tun_storage_file)

        hosts.add(alias='a', addr='localhost')
        yield hosts._store, tun._store


def test_add(stores):
    tun.add(gateway='a',
            alias='tun',
            remote_port=123,
            destination='localhost')


def test_add_multiple(stores):
    tun.add(gateway='a', alias='tun', remote_port=123, destination='localhost')
    tun.add(gateway='a', alias='tun2', remote_port=456, destination='localhost')
    tun.add(gateway='a', alias='tun3', remote_port=456, destination='localhost')


def test_socket_in_use(stores):
    s = socket.socket()
    addr = ('127.0.0.1', 49152)
    try:
        s.bind(addr)
    except socket.error:
        logger.error(f'Could not bind addr {addr}')
    tun.add(gateway='a', alias='tun', remote_port=123, destination='localhost')
    s.close()


def test_add_invalid_gw(stores):
    with pytest.raises(KeyError):
        tun.add(alias='tun',
                remote_port=123,
                destination='localhost')


def test_add_missing_gw(stores):
    with pytest.raises(KeyError):
        tun.add(alias='tun',
                gateway='b',
                remote_port=123,
                destination='localhost')


def test_add_invalid_alias(stores):
    with pytest.raises(KeyError):
        tun.add(gateway='a',
                remote_port=123,
                destination='localhost')


def test_add_invalid_destination(stores):
    with pytest.raises(KeyError):
        tun.add(gateway='a',
                alias='tun',
                remote_port=123)


def test_add_invalid_rport(stores):
    with pytest.raises(KeyError):
        tun.add(gateway='a',
                alias='tun',
                destination='localhost')


def test_add_all_ports_used(stores):
    sockets = []
    try:
        for port in range(49152, 65536):
            s = socket.socket()
            try:
                s.bind(('127.0.0.1', port))
            except socket.error:
                logger.warning(f'port {port} already in use')
            sockets.append(s)

        with pytest.raises(OSError):
            tun.add(gateway='a',
                    alias='tun',
                    remote_port=123,
                    destination='localhost')
    finally:
        for s in sockets:
            s.close()


def test_duplicate_add(stores):
    with pytest.raises(KeyError):
        kwargs = dict(gateway='a',
                      alias='tun',
                      remote_port=123,
                      destination='localhost')
        tun.add(**kwargs)
        tun.add(**kwargs)


def test_get(stores):
    tun.add(gateway='a',
            alias='tun',
            remote_port=123,
            destination='localhost')
    t = tun.get_tunnel('tun')
    assert t.gateway == 'a'
    assert t.rport == 123
    assert t.destination == 'localhost'


def test_get_all(stores):
    tun.add(gateway='a',
            alias='tun',
            remote_port=123,
            destination='localhost')
    t = list(tun.get_all_tunnels())
    assert len(t) == 1


def test_delete(stores):
    tun.add(gateway='a',
            alias='tun',
            remote_port=123,
            destination='localhost')
    tun.delete('tun')
    t = list(tun.get_all_tunnels())
    assert not t


def test_invalid_delete(stores):
    tun.add(gateway='a',
            alias='tun',
            remote_port=123,
            destination='localhost')
    tun.delete('tunnel')
    t = list(tun.get_all_tunnels())
    assert len(t) == 1
