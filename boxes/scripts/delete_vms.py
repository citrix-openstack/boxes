import argparse
import logging

from boxes.scripts import lib
from boxes import Server


def delete_vm(xenhost, vm_uuid):
    vdi_uuids = lib.vdis_of(xenhost, vm_uuid)

    xenhost.run(
        'xe vm-uninstall vm={vm_uuid} force=true'.format(
            vm_uuid=vm_uuid))

    for vdi_uuid in vdi_uuids:
        uuid = xenhost.run('xe vdi-list --minimal uuid={vdi_uuid}'.format(
            vdi_uuid=vdi_uuid))

        if uuid:
            xenhost.run('xe vdi-destroy uuid={uuid}'.format(
                uuid=uuid))


def delete_vms(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuids = xenhost.run(
        'xe vm-list name-label={vm_name} --minimal'.format(
            vm_name=args.vm_name
        )
    )

    for vm_uuid in vm_uuids.split(','):
        delete_vm(xenhost, vm_uuid)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Delete a VM and all it's hard drives "
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='Name of the VM')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    delete_vms(parser.parse_args())

