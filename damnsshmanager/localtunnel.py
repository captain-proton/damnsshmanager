import os
import socket

from collections import namedtuple
from damnsshmanager.config import Config
from damnsshmanager.storage import Store
from damnsshmanager import hosts


_store = Store(os.path.join(Config.app_dir, 'localtunnels.pickle'))


LocalTunnel = namedtuple('LocalTunnel', 'host alias lport tun_addr rport')


def __validate_ltun_args(**kwargs):

    # argument validation
    if 'host' not in kwargs:
        return 'a "host" is required'
    if 'alias' not in kwargs:
        return 'an "alias" is required for this tunnel'
    if 'remote_port' not in kwargs:
        return 'a remote port is required'
    if 'tun_addr' not in kwargs:
        return 'a "tun_addr" (tunnel address) is required'
    host = hosts.get_host(kwargs['host'])
    if host is None:
        return 'a host with alias "%s" is required. create one!'\
               % kwargs['host']
    return None


def __get_open_port(start=49152, end=65535):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    port = 0
    current_port = start
    while port is 0:
        result = sock.connect_ex(('127.0.0.1', current_port))
        if result is 0:
            port = current_port
    sock.close()
    return port


def add(**kwargs):

    err = __validate_ltun_args(**kwargs)
    if err is not None:
        raise KeyError(err)

    # get arguments (defaults)
    host = kwargs['host']
    alias = kwargs['alias']
    tun_addr = kwargs['tun_addr']
    rport = kwargs['remote_port']
    lport = 0
    if 'local_port' in kwargs and kwargs['local_port'] is not None:
        lport = kwargs['local_port']
    else:
        lport = __get_open_port()
        if lport is 0:
            raise OSError(Config.messages.get('err.no.local.port'))

    tun = LocalTunnel(host=host, alias=alias, lport=lport,
                      tun_addr=tun_addr, rport=rport)
    if _store.add(tun):
        print(Config.messages.get('added.ltun', tunnel=tun))


def get_all_tunnels() -> list:
    return _store.get_all_objects()


def delete(alias: str):

    deleted = _store.delete_objects(lambda t: t.alias != alias)
    if deleted is not None:
        for t in deleted:
            print('deleted %s' % str(t))
    else:
        print('no tunnel with alias %s' % alias)


def get_tunnel(alias: str):
    return _store.unique(lambda t: t.alias == alias)
