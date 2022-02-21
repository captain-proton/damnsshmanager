"""This module contains strategies with which ssh connections
can be opened. `SSHChannel` objects are used to open new new interactive shells
which can be created using the `ssh.provider` module.

Sample usage:
```
chan = ssh.provider.create_channel('system')
connect.open_shell(chan, 'host_alias')
```
"""
from typing import List

from loguru import logger

from damnsshmanager import hosts
from damnsshmanager import localtunnel as lt
from damnsshmanager.config import Config
from damnsshmanager.ssh.provider import SSHChannel
from damnsshmanager.storage import UniqueException

__msg = Config.messages


def host_connector_strategy(channel: SSHChannel, alias: str):
    host = hosts.get_host(alias)
    if host is None:
        logger.error(__msg.get('err.msg.no.host.alias', alias))
        return
    channel.open(host)


def ltun_connector_strategy(channel: SSHChannel, alias: str):
    ltun = lt.get_tunnel(alias)
    if ltun is None:
        logger.error(__msg.get('err.msg.no.tun.alias', alias))
        return
    host = hosts.get_host(ltun.gateway)
    channel.open(host, ltun=ltun)


def default_connector_strategy(channel: SSHChannel, alias: str):
    try:
        host = hosts.get_host(alias)
        ltun = lt.get_tunnel(alias)
        items = [_ for _ in [host, ltun] if _ is not None]
        if len(items) > 1:
            logger.error(__msg.get('err.msg.multi', alias))
        elif len(items) == 0:
            logger.error(__msg.get('err.msg.no.item', alias))
        else:
            host = host if not ltun else hosts.get_host(ltun.gateway)
            channel.open(host, ltun=ltun)
    except UniqueException as err:
        logger.error(err)


_connector_strategies = {
    'host': host_connector_strategy,
    'ltun': ltun_connector_strategy
}


def connector_strategy_types() -> List[str]:
    return list(_connector_strategies)


def _create_connector_strategy(strategy_type: str):
    return _connector_strategies.get(strategy_type, default_connector_strategy)


def open_shell(channel: SSHChannel, alias: str, strategy_type: str = None):
    strategy = _create_connector_strategy(strategy_type)
    strategy(channel, alias)
