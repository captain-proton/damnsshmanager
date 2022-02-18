import argparse
import sys

from loguru import logger

import damnsshmanager.hosts as hosts
from damnsshmanager import localtunnel as lt
from damnsshmanager.config import Config
from damnsshmanager.ssh import ssh_connectors
from damnsshmanager.ssh.factory import SSHConnectorFactory
from damnsshmanager.ssh.test import test_connection
from damnsshmanager.storage import UniqueException

__msg = Config.messages


def add(args):
    """Add a new ssh connection to the database

    Args:
        args (_type_): _description_
    """
    args = vars(args)
    module = args['module']
    try:
        module.add(**args)
    except KeyError as err:
        logger.error(err)


def delete(args):
    _type = args.type
    mod = None
    if _type == 'host':
        mod = hosts
    elif _type == 'ltun':
        mod = lt
    else:
        host = hosts.get_host(args.alias)
        ltun = lt.get_tunnel(args.alias)
        items = [_ for _ in [host, ltun] if _ is not None]
        if len(items) > 1:
            logger.error(__msg.get('err.msg.multi', args.alias))
        elif len(items) == 0:
            logger.error(__msg.get('err.msg.no.item', args.alias))
        else:
            if host is not None:
                mod = hosts
            elif ltun is not None:
                mod = lt
    if mod is not None:
        mod.delete(args.alias)


def check_hosts():
    objs = hosts.get_all_hosts()
    if objs is None:
        logger.error(__msg.get('no.hosts'))
        return

    __log_heading(__msg.get('available.hosts'))
    for obj in objs:
        try:
            test_connection(obj)
            __log_host_info(obj, __msg.get('up'),
                            status_color='\x1b[6;30;42m')
        except OSError:
            __log_host_info(obj, __msg.get('down'),
                            status_color='\x1b[0;30;41m')


def connect(args):
    _type = args.type
    factory = SSHConnectorFactory()
    connector = factory.create(args.connector)
    if _type == 'host':
        host = hosts.get_host(args.alias)
        if host is None:
            logger.error(__msg.get('err.msg.no.host.alias', args.alias))
            return
        connector.connect(host)
    elif _type == 'ltun':
        ltun = lt.get_tunnel(args.alias)
        if ltun is None:
            logger.error(__msg.get('err.msg.no.tun.alias', args.alias))
            return
        host = hosts.get_host(ltun.gateway)
        connector.connect(host, ltun=ltun)
    else:
        try:
            host = hosts.get_host(args.alias)
            ltun = lt.get_tunnel(args.alias)
            items = [_ for _ in [host, ltun] if _ is not None]
            if len(items) > 1:
                logger.error(__msg.get('err.msg.multi', args.alias))
            elif len(items) == 0:
                logger.error(__msg.get('err.msg.no.item', args.alias))
            else:
                host = host if not ltun else hosts.get_host(ltun.gateway)
                connector.connect(host, ltun=ltun)
        except UniqueException as err:
            logger.error(err)


def list_objects(args):
    _type = args.type
    if _type == 'host':
        all_hosts = hosts.get_all_hosts() or []
        header = __msg.get('fmt.host.header', 'Alias', 'Username', 'Address',
                           'Port')
        logger.info(header)
        logger.info(__divider(header))
        for h in all_hosts:
            logger.info(__msg.get('fmt.host', host=h))
    elif _type == 'ltun':
        tunnels = lt.get_all_tunnels() or []
        header = __msg.get('fmt.tunnel.header', 'Alias', 'Gateway',
                           'Local Port', 'Destination', 'Remote Port')
        logger.info(header)
        logger.info(__divider(header))
        for _type in tunnels:
            logger.info(__msg.get('fmt.tunnel', tunnel=_type))


def __divider(value):
    return '-'.join(['' for _ in range(len(value))])


def __log_host_info(host: hosts.Host, status: str, status_color=None):
    msg = '[{color}{status:^10s}{end_color}] {alias:>15s}' \
          ' => \x1b[0;33m{username:s}\x1b[0m' \
          '@\x1b[0;37m{addr:s}\x1b[0m' \
          ':{port:d}'
    if status_color is not None:
        color, end_color = status_color, '\x1b[0m'
    else:
        color, end_color = '', ''
    logger.info(msg.format(color=color,
                           end_color=end_color,
                           status=status,
                           alias=host.alias,
                           addr=host.addr,
                           username=host.username,
                           port=host.port))


def __log_heading(heading: str):
    logger.info(''.join(['-' for _ in range(79)]))
    logger.info(f' {heading:<s}')
    logger.info(''.join(['-' for _ in range(79)]))


def main():
    parser = argparse.ArgumentParser(description=__msg.get('app.desc'))

    sub_parsers = parser.add_subparsers()

    add_parser = sub_parsers.add_parser('add', help=__msg.get('add.help'))
    add_parser.add_argument('alias', type=str, help=__msg.get('alias.help'))
    add_parser.add_argument('addr', type=str,
                            help=__msg.get('addr.help'))
    add_parser.add_argument('-u', '--username', type=str,
                            help=__msg.get('username.help'))
    add_parser.add_argument('-p', '--port', type=int, default=22,
                            help=__msg.get('port.help'))
    add_parser.set_defaults(func=add, module=hosts)

    ltun_parser = sub_parsers.add_parser('ltun', help=__msg.get('ltun.help'))
    ltun_parser.add_argument('alias', type=str, help=__msg.get('alias.help'))
    ltun_parser.add_argument('gateway', type=str,
                             help=__msg.get('gateway.alias.help'))
    ltun_parser.add_argument('remote_port', type=int,
                             help=__msg.get('remote.port.help'))
    ltun_parser.add_argument('--local_port', type=int,
                             help=__msg.get('local.port.help'))
    ltun_parser.add_argument('--destination', type=str, default='localhost',
                             help=__msg.get('tun.destination.help'))
    ltun_parser.set_defaults(func=add, module=lt)

    del_parser = sub_parsers.add_parser('del', help=__msg.get('del.help'))
    del_parser.add_argument('alias', type=str, help=__msg.get('alias.help'))
    del_parser.add_argument('-t', '--type', choices=['host', 'ltun'],
                            help=__msg.get('del.type.help'))
    del_parser.set_defaults(func=delete)

    list_parser = sub_parsers.add_parser('list', help=__msg.get('list.help'))
    list_parser.add_argument('-t', '--type', choices=['host', 'ltun'],
                             default='host',
                             help=__msg.get('list.type.help'))
    list_parser.set_defaults(func=list_objects)

    connect_parser = sub_parsers.add_parser('c',
                                            help=__msg.get('connect.help'))
    connect_parser.add_argument('alias', type=str,
                                help=__msg.get('alias.help'))
    connect_parser.add_argument('-t', '--type', choices=['host', 'ltun'],
                                help=__msg.get('connect.type.help'))
    connect_parser.add_argument('-c', '--connector', choices=ssh_connectors.keys(),
                                default=list(ssh_connectors.keys())[0],
                                help=__msg.get('connector.type.help'))
    connect_parser.set_defaults(func=connect)

    args = parser.parse_args()
    num_args = len(vars(args).keys())
    if num_args == 0:
        parser.print_help()
        check_hosts()
    else:
        args.func(args)


def configure_logging():
    logger.remove()
    fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} {message}"
    logger.add(sys.stderr, format=fmt, level="INFO")


if __name__ == '__main__':
    configure_logging()
    main()
