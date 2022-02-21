import subprocess
from dataclasses import dataclass
from typing import Optional

from ..hosts import Host
from ..localtunnel import LocalTunnel
from .ssh_connector import SSHConnector


@dataclass
class NativeConnector(SSHConnector):

    def connect(self, host: Host, ltun: Optional[LocalTunnel]) -> None:
        cmd = 'ssh -p {port:d}'
        cmd = cmd.format(port=host.port)

        if ltun is not None and isinstance(ltun, LocalTunnel):
            cmd = ' '.join([cmd, '-L {lport:d}:{destination}:{rport:d}'])
            cmd = cmd.format(lport=ltun.lport, destination=ltun.destination,
                             rport=ltun.rport)

        cmd = ' '.join([cmd, '{user}@{hostname}'])
        cmd = cmd.format(user=host.username, hostname=host.addr)
        subprocess.call(cmd, shell=True)
