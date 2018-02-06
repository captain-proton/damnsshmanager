import argparse

from damnsshmanager import hosts, ssh
from damnsshmanager import localtunnel as lt
from damnsshmanager.config import Config as conf
from damnsshmanager.storage import UniqueException

__msg = conf.messages


def add(args):
    args = vars(args)
    module = args['module']
    try:
        module.add(**args)
    except KeyError as e:
        print(e)


def delete(args):
    t = args.type
    mod = None
    if t == 'host':
        mod = hosts
    elif t == 'ltun':
        mod = lt
    else:
        host = hosts.get_host(args.alias)
        ltun = lt.get_tunnel(args.alias)
        items = [_ for _ in [host, ltun] if _ is not None]
        if len(items) > 1:
            print('multiple definitions for alias "%s" found' % args.alias)
        elif len(items) == 0:
            print('not item found for alias %s' % args.alias)
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
        print('no ssh objects saved')
        return

    __log_heading('Available ssh objects')
    for obj in objs:
        try:
            ssh.test(obj)
            __log_host_info(obj, 'UP', status_color='\x1b[6;30;42m')
        except OSError:
            __log_host_info(obj, 'DOWN', status_color='\x1b[0;30;41m')


def connect(args):

    t = args.type
    if t == 'host':
        host = hosts.get_host(args.alias)
        if host is None:
            print('no host with alias "%s"' % args.alias)
            return
        ssh.connect(host)
    elif t == 'ltun':
        ltun = lt.get_tunnel(args.alias)
        if ltun is None:
            print('no local tunnel with alias "%s"' % args.alias)
            return
        host = hosts.get_host(ltun.host)
        ssh.connect(host, ltun=ltun)
    else:
        try:
            host = hosts.get_host(args.alias)
            ltun = lt.get_tunnel(args.alias)
            items = [_ for _ in [host, ltun] if _ is not None]
            if len(items) > 1:
                print('multiple definitions for alias "%s" found' % args.alias)
            elif len(items) == 0:
                print('not item found for alias %s' % args.alias)
            else:
                host = host if not ltun else hosts.get_host(ltun.host)
                ssh.connect(host, ltun=ltun)
        except UniqueException as e:
            print(e.message)


def list_objects(args):
    t = args.type
    if t == 'host':
        all_hosts = hosts.get_all_hosts() or []
        header = __msg.get('fmt.host.header', 'Alias', 'Username', 'Address',
                           'Port')
        print(header)
        print(__divider(header))
        for h in all_hosts:
            print(__msg.get('fmt.host', host=h))
    elif t == 'ltun':
        tunnels = lt.get_all_tunnels() or []
        header = __msg.get('fmt.tunnel.header', 'Alias', 'Host', 'Local Port',
                           'Tunnel Address', 'Remote Port')
        print(header)
        print(__divider(header))
        for t in tunnels:
            print(__msg.get('fmt.tunnel', tunnel=t))


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
    print(msg.format(color=color,
                     end_color=end_color,
                     status=status,
                     alias=host.alias,
                     addr=host.addr,
                     username=host.username,
                     port=host.port))


def __log_heading(heading: str):

    print(''.join(['-' for _ in range(79)]))
    print(' {heading:<s}'.format(heading=heading))
    print(''.join(['-' for _ in range(79)]))


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
    ltun_parser.add_argument('host', type=str,
                             help=__msg.get('host.alias.help'))
    ltun_parser.add_argument('remote_port', type=int,
                             help=__msg.get('remote.port.help'))
    ltun_parser.add_argument('--local_port', type=int,
                             help=__msg.get('local.port.help'))
    ltun_parser.add_argument('--tun_addr', type=str, default='localhost',
                             help=__msg.get('host.tun.help'))
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
    connect_parser.set_defaults(func=connect)

    args = parser.parse_args()
    num_args = len(vars(args).keys())
    if num_args == 0:
        parser.print_help()
        print('')
        check_hosts()
    else:
        args.func(args)


if __name__ == '__main__':
    main()
