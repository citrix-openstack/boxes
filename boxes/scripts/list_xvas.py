import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def list_xvas(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    for name in lib.xvas(xenhost):
        print name


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="List XVAs on the server"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    list_xvas(parser.parse_args())

