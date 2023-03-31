from collections import namedtuple

Host = namedtuple('Host', 'alias addr username port')
LocalTunnel = namedtuple(
    'LocalTunnel', 'gateway alias lport destination rport')
