import argparse
import logging
import time

from boxes.scripts import lib
from boxes import Server


def start_vm(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.vm_name)

    lib.start_vm(xenhost, vm_uuid)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Start a VM"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='VM name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    start_vm(parser.parse_args())
