"""This module contains classes to open a ssh connection
with the paramiko library"""
import os
import socket
import sys
import threading
from dataclasses import dataclass, field
from typing import Any, Optional, TextIO

import paramiko
import sshtunnel
from loguru import logger
from paramiko import PKey
from paramiko.py3compat import u as to_unicode

from damnsshmanager.config import Config
from damnsshmanager.model import LocalTunnel, Host
from damnsshmanager.ssh.channel import SSHChannel

_msg = Config.messages


@dataclass
class ParamikoChannel(SSHChannel):
    """This connector uses the paramiko library to connect this host
    to a remote machine. The connection is kept open to provide
    an interactive shell."""

    channel: Optional[paramiko.Channel] = None
    input_src: TextIO = sys.stdin
    pkey: Optional[PKey] = None
    known_hosts_path: str = os.path.expanduser("~/.ssh/known_hosts")

    def open(self, host: Host, ltun: Optional[LocalTunnel] = None) -> None:
        """Open a new ssh connection to the remote host using an
        optional local ssh tunnel.

        Args:
            host (Host): target host to connect to
            ltun (Optional[LocalTunnel]): optional local tunnel that is
            used on the connection.
        """
        with paramiko.SSHClient() as client:

            try:
                client.load_host_keys(self.known_hosts_path)
            except IOError:
                logger.error(
                    _msg.get("err.msg.io.known_hosts", self.known_hosts_path))

            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(host.addr, port=host.port,
                               pkey=self.pkey,
                               username=host.username)

                tun = None
                if ltun is not None and isinstance(ltun, LocalTunnel):
                    tun = sshtunnel.open_tunnel((host.addr, host.port),
                                                ssh_username=host.username,
                                                remote_bind_address=(
                                                    ltun.destination, ltun.rport),
                                                local_bind_address=('', ltun.lport))
                logger.info(_msg.get("new.interactive.shell"))
                self.channel = client.invoke_shell()
                self.open_interactive_shell(self.channel)
                if tun:
                    tun.close()
            except paramiko.BadHostKeyException:
                logger.error(
                    _msg.get("err.msg.invalid.server.host.key",
                             self.known_hosts_path))
                raise
            except paramiko.AuthenticationException:
                logger.error(_msg.get("err.msg.ssh.auth", host.addr))
                raise
            except socket.error:
                logger.error(_msg.get("err.msg.socket"))
                raise

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
    _saved_tty_attrs: Any = field(init=False)

    def __enter__(self):
        import termios
        import tty

        self._saved_tty_attrs = termios.tcgetattr(self.input_src)

        tty.setraw(self.input_src.fileno())
        tty.setcbreak(self.input_src.fileno())

    def __exit__(self, exc_type, exc_value, trace):
        import termios
        termios.tcsetattr(self.input_src, termios.TCSADRAIN,
                          self._saved_tty_attrs)

    def open(self):
        """Open a interactive channel that constantly reads and writes
        character from the terminals. Data from the remote site is written
        to local stdout.
        """
        import select

        with self:

            self.ssh_channel.settimeout(0.0)

            stop = False
            while not stop:
                r_list, _, _ = select.select(
                    [self.ssh_channel, self.input_src], [], [])
                if self.ssh_channel in r_list:
                    try:
                        input_data = to_unicode(self.ssh_channel.recv(1024))
                        if not input_data:
                            input_data = _msg.get("bye.bye")
                            stop = True

                        if input_data:
                            sys.stdout.write(input_data)
                            sys.stdout.flush()
                    except socket.timeout:
                        logger.error(_msg.get("err.msg.socket.timeout"))

                if self.input_src in r_list:
                    input_data = self.input_src.read(1)
                    logger.debug(f'read {input_data!r} from stdin,'
                                 ' type of char {type(input_char)!r}')
                    if not input_data:
                        stop = True
                    else:
                        self.ssh_channel.send(input_data.encode())


@dataclass
class DefaultChannel:

    chan: paramiko.Channel

    def open(self):

        data = _msg.get("default.chan.open.msg")
        if data:
            sys.stdout.write(data)
        writer = threading.Thread(target=DefaultChannel.writeloop,
                                  args=(self.chan,))
        writer.start()

        try:
            while True:
                stdin_char = sys.stdin.read(1)
                if not stdin_char:
                    break
                self.chan.send(stdin_char.encode(encoding='utf-8'))
        except EOFError:
            # user hit ^Z or F6
            logger.info(_msg.get("user.closed.connection"))

    @staticmethod
    def writeloop(chan):
        """The write loop reads input from given channel
        and writes received data to standard out.

        Args:
            chan (paramiko.Channel): channel to read from
        """
        stop = False
        while not stop:
            data = to_unicode(chan.recv(256))

            if not data:
                data = _msg.get("bye.bye")
                stop = True

            if not data:
                data = 'Missing message "bye.bye"'

            sys.stdout.write(data)
            sys.stdout.flush()
