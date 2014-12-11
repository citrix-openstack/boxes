import argparse
import logging

from boxes import Server


def list_vms(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_names = xenhost.run(
        'xe vm-list is-control-domain=false params=name-label --minimal')

    for vm_name in vm_names.split(','):
        print vm_name


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="List VM names"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    list_vms(parser.parse_args())

