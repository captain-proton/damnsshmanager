from damnsshmanager.ssh.ssh_connector import SSHConnector
from damnsshmanager.ssh import ssh_connectors
from damnsshmanager.config import Config


_msg = Config.messages


class SSHConnectorFactory:

    @staticmethod
    def create(connector: str) -> SSHConnector:
        creator_fn = ssh_connectors.get(connector)
        if creator_fn is None:
            raise ValueError(_msg.get('err.msg.unknown.connector', connector))
        return creator_fn()
