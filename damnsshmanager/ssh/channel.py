from typing import Optional, Protocol

from damnsshmanager.model import LocalTunnel, Host


class SSHChannel(Protocol):
    """A `SSHChannel` defines the behavior how an interactive
    shell should be opened to a remote host.
    """

    def open(self, host: Host, ltun: Optional[LocalTunnel] = None) -> None:
        """Open a new channel to target host opening an optional
        local tunnel.

        Args:
            host (Host): Host where the channel should be opened to
            ltun (Optional[LocalTunnel]): Optional local tunnel for port
            forwarding
        """
