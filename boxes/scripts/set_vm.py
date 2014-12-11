import argparse
import logging
import time

from boxes.scripts import lib
from boxes import Server


def set_disk(xenhost, vm_uuid, args):
    vdis = lib.vdis_of(xenhost, vm_uuid)
    if len(vdis) != 1:
        raise SystemExit('The vm has more than one disks')

    vdi, = vdis

    xenhost.run(
        'xe vdi-resize uuid={vdi_uuid} disk-size={size}GiB'.format(
            vdi_uuid=vdi, size=args.disk_size))


def set_mem(xenhost, vm_uuid, args):
    xenhost.run(
        'xe vm-memory-limits-set uuid={vm_uuid}'
        ' static-min={mem_size}'
        ' static-max={mem_size}'
        ' dynamic-min={mem_size}'
        ' dynamic-max={mem_size}'.format(
            vm_uuid=vm_uuid, mem_size='{mem_size}MiB'.format(
                mem_size=args.mem_size)))


def set_mac(xenhost, vm_uuid, args):
    network = xenhost.run(
        'xe vif-list vm-uuid={vm_uuid} params=network-uuid --minimal'.format(
            vm_uuid=vm_uuid))

    device = xenhost.run(
        'xe vif-list vm-uuid={vm_uuid} params=device --minimal'.format(
            vm_uuid=vm_uuid))

    old_vif = xenhost.run(
        'xe vif-list vm-uuid={vm_uuid} --minimal'.format(vm_uuid=vm_uuid))

    xenhost.run('xe vif-destroy uuid={old_vif}'.format(old_vif=old_vif))
    xenhost.run(
        'xe vif-create network-uuid={network}'
        ' device={device}'
        ' mac={mac_address}'
        ' vm-uuid={vm_uuid}'.format(
            network=network,
            device=device,
            mac_address=args.mac_address,
            vm_uuid=vm_uuid)
    )




def set_vm(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    vm_uuid = lib.vm_by_name(xenhost, args.vm_name)

    args.operation(xenhost, vm_uuid, args)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Set parameters of a VM"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('vm_name', help='VM name')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_disk = subparsers.add_parser('disk', help='set disk')
    parser_disk.add_argument('disk_size', help='set disk size in GiB', type=int)
    parser_disk.set_defaults(operation=set_disk)

    parser_mem = subparsers.add_parser('mem', help='set memory')
    parser_mem.add_argument('mem_size', help='Memory size in MiB', type=int)
    parser_mem.set_defaults(operation=set_mem)

    parser_mac = subparsers.add_parser('mac', help='set mac address')
    parser_mac.add_argument('mac_address', help='New MAC address')
    parser_mac.set_defaults(operation=set_mac)

    set_vm(parser.parse_args())
