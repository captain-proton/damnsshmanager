import pickle
import os
import socket

from collections import namedtuple
from damnsshmanager.config import Config
from damnsshmanager import hosts


_saved_objects_file = os.path.join(Config.app_dir, 'localtunnels.pickle')


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

    objs = get_all_tunnels()

    # write new host to pickle file
    with open(_saved_objects_file, 'wb') as f:
        if objs is None:
            objs = []
        tun = LocalTunnel(host=host, alias=alias,
                          lport=lport, tun_addr=tun_addr, rport=rport)
        objs.append(tun)
        pickle.dump(objs, f)
        print(Config.messages.get('added.ltun', tunnel=tun))


def get_all_tunnels() -> list:
    if not os.path.exists(_saved_objects_file):
        return None

    with open(_saved_objects_file, 'rb') as f:
        try:
            tunnels = pickle.load(f)
            return tunnels
        except EOFError:
            return None


def delete(alias: str):

    objs = get_all_tunnels()

    with open(_saved_objects_file, 'wb') as f:
        new_tunnels = [t for t in objs if t.alias != alias]
        pickle.dump(new_tunnels, f)
        if len(objs) != len(new_tunnels):
            print('removed local tunnel with alias "%s"' % alias)
        else:
            print('no local tunnel with alias "%s" found' % alias)


def get_tunnel(alias: str):
    objs = get_all_tunnels()
    if objs is not None:

        tun = [o for o in objs if o.alias == alias]
        if len(tun) > 0:
            return tun[0]
    return None
