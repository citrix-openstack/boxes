import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def list_vms(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    for vm_name in lib.vm_names(xenhost):
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

