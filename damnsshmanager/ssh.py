import socket
import subprocess

from damnsshmanager.db import Host
from errno import EINTR


def test(host: Host):
    errors = []
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
        except OSError as msg:
            errors.append(msg)
            s = None
        if s is not None:
            try:
                s.connect(sa)
            except OSError as msg:
                errors.append(msg)
                s.close()
    if len(errors) > 0:
        raise OSError({'msg': 'could not open socket',
                       'errors': errors})


def connect(host: Host):
    cmd = 'ssh -p {port:d} {user}@{hostname}'
    cmd = cmd.format(port=host.port, user=host.username, hostname=host.addr)
    subprocess.call(cmd, shell=True)


def retry_on_signal(function):
    """Retries function until it doesn't raise an EINTR error"""
    while True:
        try:
            return function()
        except EnvironmentError as e:
            if e.errno != EINTR:
                raise