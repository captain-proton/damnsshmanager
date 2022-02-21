from typing import Optional, Protocol

from ..hosts import Host
from ..localtunnel import LocalTunnel


class SSHConnector(Protocol):

    def connect(self, host: Host, ltun: Optional[LocalTunnel]) -> None:
        """Connect via ssh to a host"""
