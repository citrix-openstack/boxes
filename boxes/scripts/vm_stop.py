import argparse
import logging
import time

from boxes.scripts import lib
from boxes import Server


def stop_vm(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.vm_name)

    lib.stop_vm(xenhost, vm_uuid)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Stop a VM"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='VM name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    stop_vm(parser.parse_args())
