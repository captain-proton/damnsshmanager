import pickle
import pwd
import os

from collections import namedtuple
from damnsshmanager.config import Config

_saved_objects_file = os.path.join(Config.app_dir, 'hosts.pickle')

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


def __test_host_args(**kwargs):

    # argument validation
    if 'alias' not in kwargs:
        return 'an "alias" is required'
    if 'addr' not in kwargs:
        return 'an "addr" is required'
    host = get_host(kwargs['alias'])
    if host is not None:
        return 'a host with alias "%s" is already present' % host.alias
    return None


def add(**kwargs):

    err = __test_host_args(**kwargs)
    if err is not None:
        raise KeyError(err)

    # get arguments (defaults)
    alias = kwargs['alias']
    addr = kwargs['addr']
    pwuid = pwd.getpwuid((os.getuid()))
    pw_name = None
    if len(pwuid) > 0:
        pw_name = pwuid[0]
    username = __get('username', kwargs, default=pw_name)
    port = __get('port', kwargs, default=22)

    objs = get_all_hosts()

    # write new host to pickle file
    with open(_saved_objects_file, 'wb') as f:
        if objs is None:
            objs = []
        objs.append(Host(alias=alias, addr=addr, username=username,
                         port=port))
        pickle.dump(objs, f)


def delete(alias: str):

    objs = get_all_hosts()

    with open(_saved_objects_file, 'wb') as f:
        new_hosts = [h for h in objs if h.alias != alias]
        pickle.dump(new_hosts, f)
        if len(objs) != len(new_hosts):
            print('removed host with alias "%s"' % alias)
        else:
            print('no host with alias "%s" found' % alias)


def get_host(alias: str):
    objs = get_all_hosts()
    if objs is not None:

        host = [o for o in objs if o.alias == alias]
        if len(host) > 0:
            return host[0]
    return None


def get_all_hosts() -> list:
    if not os.path.exists(_saved_objects_file):
        return None

    with open(_saved_objects_file, 'rb') as f:
        try:
            hosts = pickle.load(f)
            return hosts
        except EOFError:
            return None
