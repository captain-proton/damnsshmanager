import socket

from damnsshmanager.hosts import Host


def test_connection(host: Host):
    errors = []
    # number of successful created sockets
    num_sockets = 0
    for res in socket.getaddrinfo(host.addr, host.port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
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
