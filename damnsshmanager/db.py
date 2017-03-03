import pickle
import os

from collections import namedtuple

_home_dir = os.path.expanduser('~')
_program_dir = os.path.join(_home_dir, '.damnsshmanager')
if not os.path.exists(_program_dir):
    os.mkdir(_program_dir, mode=0o755)
_saved_hosts_file = os.path.join(_program_dir, 'hosts.pickle')

Host = namedtuple('Host', 'alias addr username port')


def __get(key, d, default=None):
    target = dict(d)
    result = [target[k] for k in list(target.keys()) if key == k]
    if len(result) == 0 \
            or result[0] is None \
            or str(result[0]).strip() == '':
        return default
    else:
        return result[0]


def add(**kwargs):

    # argument validation
    if 'alias' not in kwargs:
        print('an "alias" is not required')
        return
    if 'addr' not in kwargs:
        print('an "addr" is not required')
        return
    host = get_host(kwargs['alias'])
    if host is not None:
        print('a host with alias "%s" is already present' % host.alias)
        return

    # get arguments (defaults)
    alias = kwargs['alias']
    addr = kwargs['addr']
    username = __get('username', kwargs, default=os.getlogin())
    port = __get('port', kwargs, default=22)

    hosts = get_all_hosts()

    # write new host to pickle file
    with open(_saved_hosts_file, 'wb') as f:
        if hosts is None:
            hosts = []
        hosts.append(Host(alias=alias, addr=addr, username=username,
                          port=port))
        pickle.dump(hosts, f)


def delete(alias: str):

    hosts = get_all_hosts()

    with open(_saved_hosts_file, 'wb') as f:
        new_hosts = [h for h in hosts if h.alias != alias]
        pickle.dump(new_hosts, f)
        if len(hosts) != len(new_hosts):
            print('removed host with alias "%s"' % alias)
        else:
            print('no host with alias "%s" found' % alias)


def get_host(alias: str):
    hosts = get_all_hosts()
    if hosts is not None:

        optional_host = [h for h in hosts if h.alias == alias]
        if len(optional_host) > 0:
            return optional_host[0]
    return None


def get_all_hosts() -> list:
    if not os.path.exists(_saved_hosts_file):
        return None

    with open(_saved_hosts_file, 'rb') as f:
        try:
            hosts = pickle.load(f)
            return hosts
        except EOFError:
            return None
