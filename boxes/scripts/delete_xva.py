import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def delete_xva(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    lib.delete_xva(xenhost, args.xva_name)

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Delete an XVA"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('xva_name', help='Name of the XVA')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    delete_xva(parser.parse_args())

