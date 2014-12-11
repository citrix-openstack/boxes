import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def import_xva(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    if args.source_xva not in lib.xvas(xenhost):
        raise SystemExit('No xva found with name [{source_xva}]'.format(
            source_xva=args.source_xva))
    if lib.no_vm_with_name(xenhost, args.target_vm):
        lib.import_xva(xenhost, args.source_xva, args.target_vm)
    else:
        raise SystemExit('VM [{target_vm}] already exists'.format(
            target_vm=args.target_vm))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Import an appliance as a VM"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('source_xva', help='Source VM')
    parser.add_argument('target_vm', help='Target name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    import_xva(parser.parse_args())
