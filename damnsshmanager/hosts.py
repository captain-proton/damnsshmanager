import os
import pathlib
import pwd
from typing import Optional

from loguru import logger

from damnsshmanager.config import Config
from damnsshmanager.model import Host
from damnsshmanager.storage import PickleStore

_store = PickleStore(pathlib.Path(Config.app_dir, 'hosts.pickle'))

__msg = Config.messages


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
    username = kwargs.get('username')
    if not username:
        username = pw_name
    port = kwargs.get('port', 22)

    host = Host(alias=alias, addr=addr, username=username, port=port)
    try:
        _store.add(host, sort=lambda h: h.alias)
        logger.info(__msg.get('added.host', host=host))
    except IOError:
        logger.error(__msg.get('err.msg.dump.error', _store.object_file))


def delete(alias: str):

    deleted = _store.delete(lambda h: h.alias == alias)
    if deleted is not None:
        for h in deleted:
            logger.info(__msg.get('deleted', str(h)))
    else:
        logger.info(__msg.get('err.msg.no.item', alias))


def get_host(alias: str) -> Optional[Host]:
    return _store.unique(key=lambda h: h.alias == alias)


def get_all_hosts() -> list:
    return list(_store.get())
