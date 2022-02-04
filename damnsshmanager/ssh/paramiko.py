"""This module contains classes to open a ssh connection
with the paramiko library"""
import os
import socket
import sys
from dataclasses import dataclass
from typing import Optional, TextIO

import paramiko
import sshtunnel
from loguru import logger
from paramiko.py3compat import u as to_unicode

from damnsshmanager.config import Config
from damnsshmanager.hosts import Host
from damnsshmanager.localtunnel import LocalTunnel
from damnsshmanager.ssh.ssh_connector import SSHConnector

_msg = Config.messages


@dataclass
class ParamikoConnector(SSHConnector):
    """This connector uses the paramiko library to connect this host
    to a remote machine. The connection is kept open to provide
    an interactive shell."""

    input_src: TextIO = sys.stdin

    def connect(self, host: Host, ltun: Optional[LocalTunnel] = None) -> None:
        """Open a new ssh connection to the remote host using an
        optional local ssh tunnel.

        Args:
            host (Host): target host to connect to
            ltun (Optional[LocalTunnel]): optional local tunnel that is
            used on the connection.
        """
        with paramiko.SSHClient() as client:

            known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
            try:
                client.load_host_keys(known_hosts_path)
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
        """Opens an interactive shell based on the current OS.

        Args:
            channel (paramiko.Channel): channel that is used to read from
            and write into
        """
        if sys.platform.startswith('linux'):
            chan = PosixChannel(channel, self.input_src)
        else:
            chan = DefaultChannel(channel)

        chan.open()


@dataclass
class PosixChannel:
    """A posix channel is able to read and write data from posix terminals.
    This channel can for example be used on linux or mac os systems.

    Arguments:
        ssh_channel (paramiko.Channel): channel which is used to send
        bytes into and read from
    """

    ssh_channel: paramiko.Channel
    input_src: TextIO = sys.stdin

    def open(self):
        """Open a interactive channel that constantly reads and writes
        character from the terminals. Data from the remote site is written
        to local stdout.
        """
        import select
        import termios
        import tty

        try:
            tty.setraw(self.input_src.fileno())
            tty.setcbreak(self.input_src.fileno())

            self.ssh_channel.settimeout(0.0)

            stop = False
            while not stop:
                r_list, _, _ = select.select(
                    [self.ssh_channel, self.input_src], [], [])
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

                if self.input_src in r_list:
                    input_char = self.input_src.read(1)
                    logger.debug(f'read {input_char!r} from stdin,'
                                 ' type of char {type(input_char)!r}')
                    if not input_char:
                        stop = True
                    else:
                        self.ssh_channel.send(input_char.encode())
        finally:
            sys_tty = termios.tcgetattr(self.input_src)
            termios.tcsetattr(self.input_src, termios.TCSADRAIN, sys_tty)


@dataclass
class DefaultChannel:

    chan: paramiko.Channel

    def open(self):
        pass
