import pwd
import os

from collections import namedtuple
from damnsshmanager.config import Config
from damnsshmanager.storage import Store

_saved_objects_file = os.path.join(Config.app_dir, 'hosts.pickle')
_store = Store(_saved_objects_file)

__msg = Config.messages

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
        return __msg.get('alias.required')
    if 'addr' not in kwargs:
        return __msg.get('addr.required')
    host = get_host(kwargs['alias'])
    if host is not None:
        return __msg.get('alias.present', host.alias)
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

    host = Host(alias=alias, addr=addr, username=username, port=port)
    added = _store.add(host, sort=lambda h: h.alias)
    if added:
        print(__msg.get('added.host', host=host))


def delete(alias: str):

    deleted = _store.delete(lambda h: h.alias != alias)
    if deleted is not None:
        for h in deleted:
            print(__msg.get('deleted', str(h)))
    else:
        print(__msg.get('err.msg.no.item', alias))


def get_host(alias: str):
    return _store.unique(key=lambda h: h.alias == alias)


def get_all_hosts() -> list:
    return _store.get()
