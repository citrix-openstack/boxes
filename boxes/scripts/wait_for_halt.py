import argparse
import logging
import time

from boxes.scripts import lib
from boxes import Server


def wait_for_halt(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.vm_name)

    while not lib.vm_halted(xenhost, vm_uuid):
        print "VM [{vm_name}] is not halted, sleeping".format(
            vm_name=args.vm_name)
        time.sleep(5)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Wait until a VM is halted"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='VM name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    wait_for_halt(parser.parse_args())
