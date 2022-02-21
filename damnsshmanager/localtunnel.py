import errno
import os
import socket
from collections import namedtuple
from typing import Iterable

from loguru import logger

from . import hosts
from .config import Config
from .storage import Store

_store = Store(os.path.join(Config.app_dir, 'localtunnels.pickle'))
__msg = Config.messages

LocalTunnel = namedtuple(
    'LocalTunnel', 'gateway alias lport destination rport')


def __validate_ltun_args(**kwargs):

    # argument validation
    if 'gateway' not in kwargs:
        return __msg.get('gateway.required')
    if 'alias' not in kwargs:
        return __msg.get('alias.required')
    if 'remote_port' not in kwargs:
        return __msg.get('remote.port.required')
    if 'destination' not in kwargs:
        return __msg.get('destination.required')
    gateway = hosts.get_host(kwargs['gateway'])
    if gateway is None:
        return __msg.get('gateway.with.alias.required', kwargs['gateway'])
    ltun = get_tunnel(kwargs['alias'])
    if ltun is not None:
        return __msg.get('alias.present', ltun.alias)
    return None


def __get_open_port(start=49152, end=65535, exclude=(0,)):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    port = 0
    current_port = start
    while port == 0 and current_port <= end:
        if current_port in exclude:
            current_port += 1
            continue

        try:
            sock.bind(("127.0.0.1", current_port))
            port = current_port
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                current_port += 1
    sock.close()
    return port


def add(**kwargs):

    err = __validate_ltun_args(**kwargs)
    if err is not None:
        raise KeyError(err)

    # get arguments (defaults)
    gateway = kwargs.get('gateway')
    alias = kwargs.get('alias')
    destination = kwargs.get('destination')
    rport = kwargs.get('remote_port')
    lport = kwargs.get('local_port')
    if not lport:
        lports = [t.lport for t in get_all_tunnels()]
        lport = __get_open_port(exclude=lports)
        if lport == 0:
            raise OSError(__msg.get('err.no.local.port'))

    tun = LocalTunnel(gateway=gateway, alias=alias, lport=lport,
                      destination=destination, rport=rport)
    try:
        _store.add(tun, sort=lambda t: t.alias)
        logger.info(__msg.get('added.ltun', tunnel=tun))
    except IOError:
        logger.error(__msg.get('err.msg.dump.error', _store.objects_file))


def get_all_tunnels() -> Iterable:
    return _store.get()


def get_tunnel(alias: str) -> LocalTunnel:
    return _store.unique(key=lambda t: t.alias == alias)


def delete(alias: str):

    deleted = _store.delete(lambda t: t.alias == alias)
    if deleted is not None:
        for d in deleted:
            logger.info(__msg.get('deleted', str(d)))
    else:
        logger.info(__msg.get('err.msg.no.item', alias))
