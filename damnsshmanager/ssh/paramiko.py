import os
import socket
import sys
from dataclasses import dataclass
from typing import Optional

import paramiko
import sshtunnel
from loguru import logger
from paramiko.py3compat import u as to_unicode

from damnsshmanager.config import Config
from damnsshmanager.hosts import Host
from damnsshmanager.localtunnel import LocalTunnel
from damnsshmanager.ssh.ssh_connector import SSHConnector

_msg = Config.messages


class ParamikoConnector(SSHConnector):

    def connect(self, host: Host, ltun: Optional[LocalTunnel]) -> None:
        with paramiko.SSHClient() as client:

            try:
                known_hosts_path = "~/.ssh/known_hosts"
                client.load_host_keys(os.path.expanduser(known_hosts_path))
            except IOError:
                logger.error(_msg.get("err.msg.io.known_hosts", known_hosts_path))

            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(host.addr, port=host.port, username=host.username)

                tun = None
                if ltun is not None and isinstance(ltun, LocalTunnel):
                    tun = sshtunnel.open_tunnel((host.addr, host.port),
                                                ssh_username=host.username,
                                                remote_bind_address=(ltun.destination, ltun.rport),
                                                local_bind_address=('', ltun.lport))
                logger.info(_msg.get("new.interactive.shell"))
                channel = client.invoke_shell()
                self.open_interactive_shell(channel)
                if tun:
                    tun.close()
            except paramiko.ssh_exception.BadHostKeyException:
                logger.error(_msg.get("err.msg.invalid.server.host.key", known_hosts_path))
            except paramiko.ssh_exception.AuthenticationException:
                logger.error(_msg.get("err.msg.ssh.auth", host.addr))
            except socket.error:
                logger.error(_msg.get("err.msg.socket"))

    def open_interactive_shell(self, channel: paramiko.Channel):
        if sys.platform.startswith('linux'):
            channel = PosixChannel(channel)
        else:
            channel = DefaultChannel(channel)

        channel.open()


@dataclass
class PosixChannel:

    chan: socket.socket

    def open(self):
        import select
        import termios
        import tty

        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())

            self.chan.settimeout(0.0)

            stop = False
            while not stop:
                r, w, e = select.select([self.chan, sys.stdin], [], [])
                if self.chan in r:
                    try:
                        x = to_unicode(self.chan.recv(1024))
                        if not x:
                            x = "\r\n*** Bye bye\r\n"
                            stop = True
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                        logger.error(_msg.get("err.msg.socket.timeout"))

                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if not x:
                        stop = True
                    else:
                        self.chan.send(x)
        finally:
            sys_tty = termios.tcgetattr(sys.stdin)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, sys_tty)


class DefaultChannel:

    def open(self):
        pass
