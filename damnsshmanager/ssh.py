import socket
import subprocess

from damnsshmanager.hosts import Host
from damnsshmanager.localtunnel import LocalTunnel
from errno import EINTR


def test(host: Host):
    errors = []
    # number of successful created sockets
    num_sockets = 0
    for res in socket.getaddrinfo(host.addr, host.port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        # print('       af: %s' % af)
        # print(' socktype: %s' % socktype)
        # print('    proto: %s' % proto)
        # print('canonname: %s' % canonname)
        # print('       sa: %s' % str(sa))
        try:
            s = socket.socket(af, socktype, proto)
            s.settimeout(1)
            num_sockets += 1
        except OSError as msg:
            errors.append(msg)
            s = None
        if s is not None:
            try:
                s.connect(sa)
            except OSError as msg:
                errors.append(msg)
                s.close()
    # a connection could not be established if an error was created for
    # each created socket
    if len(errors) >= num_sockets:
        raise OSError({'msg': 'could not open socket',
                       'errors': errors})


def connect(host: Host, ltun=None):
    cmd = 'ssh -p {port:d}'
    cmd = cmd.format(port=host.port)

    if ltun is not None and isinstance(ltun, LocalTunnel):
        cmd = ' '.join([cmd, '-L {lport:d}:{tun_addr}:{rport:d}'])
        cmd = cmd.format(lport=ltun.lport, tun_addr=ltun.tun_addr,
                         rport=ltun.rport)

    cmd = ' '.join([cmd, '{user}@{hostname}'])
    cmd = cmd.format(user=host.username, hostname=host.addr)
    subprocess.call(cmd, shell=True)


def retry_on_signal(function):
    """Retries function until it doesn't raise an EINTR error"""
    while True:
        try:
            return function()
        except EnvironmentError as e:
            if e.errno != EINTR:
                raise
