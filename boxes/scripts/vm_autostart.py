import argparse
import logging
import time

from boxes.scripts import lib
from boxes import Server


logger = logging.getLogger(__name__)


def autostart_vm(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.vm_name)

    logger.info('Enabling auto_poweron on default pool')
    pool = xenhost.run('xe pool-list --minimal').strip()
    xenhost.run(
        'xe pool-param-set uuid={pool} other-config:auto_poweron=true'.format(
            pool=pool))

    logger.info('Enabling auto_poweron on guest')
    xenhost.run(
        'xe vm-param-set uuid={vm_uuid} other-config:auto_poweron=true'.format(
            vm_uuid=vm_uuid))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Auto-start a VM on the hypervisor's start"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='VM name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    autostart_vm(parser.parse_args())
