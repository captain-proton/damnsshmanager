import subprocess
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

from ..hosts import Host
from ..localtunnel import LocalTunnel
from .channel import SSHChannel


@dataclass
class NativeChannel(SSHChannel):

    _host: Host = field(default=None, init=False)
    _completed_process: subprocess.CompletedProcess = field(
        default=None, init=False)
    _proc_error: subprocess.CalledProcessError = field(
        default=None, init=False)

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, trace):
        if self._completed_process:
            logger.info(f'Connection to {self._host} closed')

        if self._proc_error:
            logger.error(
                f'An error communicating with {self._host}'
                f': {self._proc_error}')

    def open(self, host: Host, ltun: Optional[LocalTunnel] = None) -> None:
        self._host = host
        cmd = 'ssh -p {port:d}'
        cmd = cmd.format(port=host.port)

        if ltun is not None and isinstance(ltun, LocalTunnel):
            cmd = ' '.join([cmd, '-L {lport:d}:{destination}:{rport:d}'])
            cmd = cmd.format(lport=ltun.lport, destination=ltun.destination,
                             rport=ltun.rport)

        cmd = ' '.join([cmd, '{user}@{hostname}'])
        cmd = cmd.format(user=host.username, hostname=host.addr)
        try:
            self._completed_process = subprocess.run(cmd,
                                                     shell=True,
                                                     check=True)
        except subprocess.CalledProcessError as err:
            self._proc_error = err
