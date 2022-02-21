from ..config import Config
from . import ssh_connectors
from .ssh_connector import SSHConnector

_msg = Config.messages


class SSHConnectorFactory:

    @staticmethod
    def create(connector: str) -> SSHConnector:
        creator_fn = ssh_connectors.get(connector)
        if creator_fn is None:
            raise ValueError(_msg.get('err.msg.unknown.connector', connector))
        return creator_fn()
