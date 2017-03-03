import argparse

from damnsshmanager import db, ssh


def add(args):
    args = vars(args)
    db.add(**args)


def delete(args):
    db.delete(args.alias)


def list_hosts():
    hosts = db.get_all_hosts()
    if hosts is None:
        print('no hosts saved')
        return

    __log_heading('Available hosts')
    for h in hosts:
        try:
            ssh.test(h)
            __log_host_info(h, 'UP', status_color='\x1b[6;30;42m')
        except OSError:
            __log_host_info(h, 'DOWN', status_color='\x1b[0;30;41m')


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
    desc = 'This is one simple damn ssh manager. The intend of this thing is' \
           ' to provide really simple use of the linux command line tool ssh' \
           ' that is NOT able to provide a ssh managing instance. Of course' \
           ' that would be named ssh-manager or something.'
    parser = argparse.ArgumentParser(description=desc)

    sub_parsers = parser.add_subparsers()

    add_parser = sub_parsers.add_parser('add')
    add_parser.add_argument('alias', type=str,
                            help='unique identifier to use to add/del/connect')
    add_parser.add_argument('addr', type=str,
                            help='Any inet address that is used to connect')
    add_parser.add_argument('-u', '--username', type=str,
                            help='username parameter to connect to the host.'
                                 ' By default this is the login name'
                                 ' (os.getlogin())')
    add_parser.add_argument('-p', '--port', type=int, default=22,
                            help='port that target host uses for ssh'
                                 ' (22 by default)')
    add_parser.set_defaults(func=add)

    del_parser = sub_parsers.add_parser('del')
    del_parser.add_argument('alias', type=str,
                            help='unique identifier to use to add/del/connect')
    del_parser.set_defaults(func=delete)

    args = parser.parse_args()
    if len(vars(args).keys()) == 0:
        list_hosts()
        print('')
        __log_heading('Commands')
        add_parser.print_usage()
        del_parser.print_usage()
    else:
        args.func(args)


if __name__ == '__main__':
    main()
