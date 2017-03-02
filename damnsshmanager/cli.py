import argparse
import logging

from . import db


def add(args):
    args = vars(args)
    db.add(**args)


def delete(args):
    db.delete(args.alias)


def list_hosts():
    hosts = db.get_all_hosts()
    if hosts is None:
        print('no hosts saved')
    else:
        for h in hosts:
            print(h)


def main():
    desc = 'This is one simple damn ssh manager. The intend of this thing is' \
           ' to provide really simple use of the linux command line tool ssh' \
           ' that is NOT able to provide a ssh managing instance. Of course' \
           ' that would be named ssh-manager or something.'
    parser = argparse.ArgumentParser(description=desc)

    sub_parsers = parser.add_subparsers()

    add_parser = sub_parsers.add_parser('add')
    add_parser.add_argument('alias', type=str)
    add_parser.add_argument('host', type=str)
    add_parser.add_argument('-u', '--username', type=str)
    add_parser.add_argument('-p', '--port', type=int, default=22)
    add_parser.set_defaults(func=add)

    del_parser = sub_parsers.add_parser('del')
    del_parser.add_argument('alias', type=str)
    del_parser.set_defaults(func=delete)

    args = parser.parse_args()
    if len(vars(args).keys()) == 0:
        list_hosts()
    else:
        args.func(args)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

if __name__ == '__main__':
    main()
