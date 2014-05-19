import argparse
import os
import logging
import StringIO

import textwrap

import boxes
from boxes import Server, disconnect_all
from boxes.scripts import lib


log=logging.getLogger(__name__)


def create_centos(options):
    template = 'CentOS 6 (64-bit)'

    xenhost = Server(options.xshost, options.xsuser, options.xspass)
    xenhost.disable_known_hosts = True

    template_uuid = lib.template_uuid(xenhost, template)

    vm = lib.clone_template(xenhost, template_uuid, options.vmname)

    if args.kickstart is None:
        virt_kickstart_path = os.path.join(
            os.path.dirname(boxes.__file__), "virt-kickstart")
    else:
        virt_kickstart_path = args.kickstart

    with open(virt_kickstart_path, 'rb') as virt_kickstart_file:
        virt_kickstart_contents = virt_kickstart_file.read()

    virt_kickstart_contents = virt_kickstart_contents.replace(
        '@install_repo@', options.install_repo).replace(
        '@rootpwd@', options.rootpwd)

    kickstart_fname = '{0}.kickstart'.format(vm)

    xenhost.put(
        StringIO.StringIO(virt_kickstart_contents),
        "/opt/xensource/www/{0}".format(kickstart_fname))

    kickstart_url = "http://{0}/{1}".format(options.xshost, kickstart_fname)

    xenhost.run(
        'xe vm-param-set uuid={0} is-a-template=false'
        .format(vm))

    xenhost.run(
        'xe vm-param-set uuid={0} name-description="{1}"'
        .format(vm, options.vmname))

    xenhost.run(
        'xe vm-memory-limits-set static-min={0}MiB static-max={0}MiB dynamic-min={0}MiB dynamic-max={0}MiB uuid={1}'
        .format(options.memsize, vm))

    pool = xenhost.run(
        'xe pool-list --minimal')

    sr = xenhost.run(
        'xe pool-param-get uuid={0} param-name=default-SR'
        .format(pool))

    vdi = xenhost.run(
        'xe vdi-create name-label="boot-{vmname}" '
        'sr-uuid={sr} type=system virtual-size={hddsize}GiB'
        .format(sr=sr, hddsize=hddsize, vmname=vmname))

    xenhost.run(
        'xe vbd-create vm-uuid={0} vdi-uuid={1} device=0 bootable=true'
        .format(vm, vdi))

    xenhost.run(
        'xe vm-param-set uuid={0} other-config:install-repository={1}'
        .format(vm, options.install_repo))

    xenhost.run(
        'xe vm-param-set uuid={0} PV-args="ks={1} ksdevice=eth0"'.format(
            vm, kickstart_url)
    )

    net = xenhost.run(
        'xe network-list name-label="{0}" --minimal'
        .format(options.networklabel))

    xenhost.run(
        'xe vif-create network-uuid={0} vm-uuid={1} device=0'
        .format(net, vm))

    xenhost.run(
        'xe vm-start uuid={0}'
        .format(vm))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Install a centos vm in XenServer')
    parser.add_argument('xshost', help='XenServer host')
    parser.add_argument('vmname', help='Name for the virtual machine')
    parser.add_argument(
        'install_repo', help='Distro url used by XenServer')
    parser.add_argument('rootpwd', help='Password for the root user on the new system')
    parser.add_argument('--xspass', help='Password for XenServer')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--hddsize', help='Disk size for vm in Gigabytes (8)', default="8")
    parser.add_argument(
        '--networklabel', help='name-label of the network to connect the server to',
        default="Pool-wide network associated with eth0")
    parser.add_argument(
        '--kickstart', help='Kickstart file to use',
        default=None)
    parser.add_argument(
        '--memsize', help='Memory size in MiB (2048)',
        default="2048")


    args = parser.parse_args()

    log.info("Parameters:%s", args)

    try:
        create_centos(args)
    finally:
        disconnect_all()
