"""This module contains classes to open a ssh connection
with the paramiko library"""
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
    """This connector"""

    def connect(self, host: Host, ltun: Optional[LocalTunnel]) -> None:
        with paramiko.SSHClient() as client:

            known_hosts_path = "~/.ssh/known_hosts"
            try:
                client.load_host_keys(os.path.expanduser(known_hosts_path))
            except IOError:
                logger.error(
                    _msg.get("err.msg.io.known_hosts", known_hosts_path))

            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(host.addr, port=host.port,
                               username=host.username)

                tun = None
                if ltun is not None and isinstance(ltun, LocalTunnel):
                    tun = sshtunnel.open_tunnel((host.addr, host.port),
                                                ssh_username=host.username,
                                                remote_bind_address=(
                                                    ltun.destination, ltun.rport),
                                                local_bind_address=('', ltun.lport))
                logger.info(_msg.get("new.interactive.shell"))
                channel = client.invoke_shell()
                self.open_interactive_shell(channel)
                if tun:
                    tun.close()
            except paramiko.BadHostKeyException:
                logger.error(
                    _msg.get("err.msg.invalid.server.host.key", known_hosts_path))
            except paramiko.AuthenticationException:
                logger.error(_msg.get("err.msg.ssh.auth", host.addr))
            except socket.error:
                logger.error(_msg.get("err.msg.socket"))

    def open_interactive_shell(self, channel: paramiko.Channel):
        if sys.platform.startswith('linux'):
            chan = PosixChannel(channel)
        else:
            chan = DefaultChannel(channel)

        chan.open()


@dataclass
class PosixChannel:

    ssh_channel: paramiko.Channel

    def open(self):
        import select
        import termios
        import tty

        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())

            self.ssh_channel.settimeout(0.0)

            stop = False
            while not stop:
                r_list, _, _ = select.select(
                    [self.ssh_channel, sys.stdin], [], [])
                if self.ssh_channel in r_list:
                    try:
                        input_char = to_unicode(self.ssh_channel.recv(1024))
                        if not input_char:
                            input_char = "\r\n*** Bye bye\r\n"
                            stop = True
                        sys.stdout.write(input_char)
                        sys.stdout.flush()
                    except socket.timeout:
                        logger.error(_msg.get("err.msg.socket.timeout"))

                if sys.stdin in r_list:
                    input_char = sys.stdin.read(1)
                    logger.debug(f'read {input_char!r} from stdin,'
                                 ' type of char {type(input_char)!r}')
                    if not input_char:
                        stop = True
                    else:
                        self.ssh_channel.send(input_char.encode())
        finally:
            sys_tty = termios.tcgetattr(sys.stdin)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, sys_tty)


@dataclass
class DefaultChannel:

    chan: paramiko.Channel

    def open(self):
        pass
