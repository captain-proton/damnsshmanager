import argparse

from damnsshmanager import db, ssh, messages


def add(args):
    args = vars(args)
    db.add(**args)


def delete(args):
    db.delete(args.alias)


def list_hosts():
    objs = db.get_all_ssh_objects()
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
    host = db.get_host(args.alias)
    if host is None:
        print('no host with alias "%s"' % args.alias)
        return

    ssh.connect(host)


def ltun(args):
    args = vars(args)
    db.ltun(**args)


def __log_host_info(host: db.Host, status: str, status_color=None):
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
    m = messages.Messages()
    parser = argparse.ArgumentParser(description=m.get('app.desc'))

    sub_parsers = parser.add_subparsers()

    add_parser = sub_parsers.add_parser('add', help=m.get('add.help'))
    add_parser.add_argument('alias', type=str, help=m.get('alias.help'))
    add_parser.add_argument('addr', type=str,
                            help=m.get('addr.help'))
    add_parser.add_argument('-u', '--username', type=str,
                            help=m.get('username.help'))
    add_parser.add_argument('-p', '--port', type=int, default=22,
                            help=m.get('port.help'))
    add_parser.set_defaults(func=add)

    ltun_parser = sub_parsers.add_parser('ltun', help=m.get('ltun.help'))
    ltun_parser.add_argument('alias', type=str, help=m.get('alias.help'))
    ltun_parser.add_argument('addr', type=str, help=m.get('addr.help'))
    ltun_parser.add_argument('local_port', type=int,
                             help=m.get('local.port.help'))
    ltun_parser.add_argument('remote_port', type=int,
                             help=m.get('remote.port.help'))
    ltun_parser.add_argument('host', type=str, default='localhost',
                             help=m.get('host.tun.help'))
    ltun_parser.add_argument('-u', '--username', type=str,
                             help=m.get('username.help'))
    ltun_parser.add_argument('-p', '--port', type=int, default=22,
                             help=m.get('port.help'))
    ltun_parser.set_defaults(func=ltun)

    del_parser = sub_parsers.add_parser('del', help=m.get('del.help'))
    del_parser.add_argument('alias', type=str, help=m.get('alias.help'))
    del_parser.set_defaults(func=delete)

    connect_parser = sub_parsers.add_parser('c', help=m.get('connect.help'))
    connect_parser.add_argument('alias', type=str, help=m.get('alias.help'))
    connect_parser.set_defaults(func=connect)

    args = parser.parse_args()
    num_args = len(vars(args).keys())
    if num_args == 0:
        list_hosts()
        print('')
        __log_heading('Commands')
        add_parser.print_usage()
        del_parser.print_usage()
        connect_parser.print_usage()
    else:
        args.func(args)


if __name__ == '__main__':
    main()
