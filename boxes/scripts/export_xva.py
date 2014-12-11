import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def export_xva(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.source_vm)

    lib.export_xva(xenhost, vm_uuid, args.target_xva)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Export a VM as an appliance"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('source_vm', help='Source VM')
    parser.add_argument('target_xva', help='Target name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    export_xva(parser.parse_args())

