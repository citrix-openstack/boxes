import sys
import boxes

from boxes.scripts import lib


def command(user, password, host, guest):
    xenhost = boxes.Server(host, user, password)
    xenhost.disable_known_hosts = True
    return lib.no_vm_with_name(xenhost, guest)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Return 1 if the guest exists')
    parser.add_argument('host', help='XenServer host name')
    parser.add_argument('guest', help='guest name-label to look up')
    parser.add_argument(
        '--password', help='Password for XenServer', default=None)
    parser.add_argument(
        '--user', help='User for XenServer', default='root')

    args = parser.parse_args()
    user, password, host = args.user, args.password, args.host
    no_vm = command(user, password, host, args.guest)
    if no_vm:
        sys.exit(0)
    sys.exit(1)
