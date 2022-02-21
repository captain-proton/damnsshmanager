from typing import List

from damnsshmanager.config import Config
from damnsshmanager.ssh.native import NativeChannel
from damnsshmanager.ssh.paramiko import ParamikoChannel

from .channel import SSHChannel

_msg = Config.messages
_provider = {
    'system': NativeChannel,
    'application': ParamikoChannel
}


def provider() -> List[str]:
    return list(_provider)


def create_channel(provider_name: str) -> SSHChannel:
    creator_fn = _provider.get(provider_name)
    if creator_fn is None:
        raise ValueError(_msg.get('err.msg.unknown.connector', provider_name))
    return creator_fn()
