from typing import Protocol, Optional

from damnsshmanager.hosts import Host
from damnsshmanager.localtunnel import LocalTunnel


class SSHConnector(Protocol):

    def connect(self, host: Host, ltun: Optional[LocalTunnel]) -> None:
        """Connect via ssh to a host"""
