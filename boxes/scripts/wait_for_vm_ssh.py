import argparse
import logging
import time
import sys

from boxes.scripts import lib
from boxes.scripts import get_guest_ip
from boxes import Server


logger = logging.getLogger(__name__)


def wait_for_vm_ssh(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.source_vm)

    ip_addr = ""

    while True:
        ip_addr = get_guest_ip.get_guest_ip(xenhost, vm_uuid)
        if ip_addr:
            break
        else:
            logger.info("No IP reported yet, sleeping")
            time.sleep(5)

    server = Server(ip_addr, None, None)
    if server.wait_for_ssh_with_retries(
            timeout=1, retry_condition=lambda x: x <10):
        print ip_addr
        sys.exit(0)
    sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Wait until a VM is accessible through ssh"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('source_vm', help='Source VM')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    wait_for_vm_ssh(parser.parse_args())

