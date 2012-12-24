import argparse
import logging

import textwrap

from boxes import Server, disconnect_all
from boxes.scripts import lib


def command(user, password, host, release_name, install_repo, preseed_file, vmname):
    template = 'Ubuntu Lucid Lynx 10.04 (64-bit)'

    xenhost = Server(host, user, password)
    xenhost.disable_known_hosts = True

    template_uuid = lib.template_uuid(xenhost, template)

    vm = lib.clone_template(xenhost, template_uuid, vmname)

    xenhost.run(
        'xe vm-param-set uuid={0} is-a-template=false'
        .format(vm))

    xenhost.run(
        'xe vm-param-set uuid={0} name-description="{1}"'
        .format(vm, vmname))

    pool = xenhost.run(
        'xe pool-list --minimal')

    sr = xenhost.run(
        'xe pool-param-get uuid={0} param-name=default-SR'
        .format(pool))

    vdi = xenhost.run(
        'xe vdi-create name-label="boot" '
        'sr-uuid={0} type=system virtual-size=8GiB'
        .format(sr))

    xenhost.run(
        'xe vbd-create vm-uuid={0} vdi-uuid={1} device=0 bootable=true'
        .format(vm, vdi))

    xenhost.run(
        'xe vm-param-set uuid={0} other-config:install-repository={1}'
        .format(vm, install_repo))

    xenhost.run(
        'xe vm-param-set uuid={0} other-config:debian-release={1}'
        .format(vm, release_name))

    domain = 'somedomain'
    xenhost.run(
        textwrap.dedent(r"""
        xe vm-param-set uuid={0} PV-args="-- quiet console=hvc0 \
        partman/default_filesystem=ext3 \
        locale=en_GB \
        console-setup/ask_detect=false \
        keyboard-configuration/layoutcode=gb \
        netcfg/choose_interface=eth0 \
        netcfg/get_hostname={1} \
        netcfg/get_domain={2} \
        mirror/udeb/suite={4} \
        mirror/suite={4} \
        auto url={3}"
        """.format(vm, vmname, domain, preseed_file, release_name)))

    bridge_name = 'xenbr0'

    net = xenhost.run(
        'xe network-list bridge={0} --minimal'
        .format(bridge_name))

    xenhost.run(
        'xe vif-create network-uuid={0} vm-uuid={1} device=0'
        .format(net, vm))

    xenhost.run(
        'xe vm-start uuid={0}'
        .format(vm))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Install a debian -like vm in XenServer')
    parser.add_argument('user', help='XenServer user')
    parser.add_argument('password', help='XenServer password')
    parser.add_argument('host', help='Host')
    parser.add_argument('release_name', help='Codename for the VM (precise)')
    parser.add_argument('install_repo', help='Install repository to use')
    parser.add_argument('preseed_file', help='Preseed file to use')
    parser.add_argument('vmname', help='Name for the virtual machine')

    args = parser.parse_args()

    try:
        command(
            args.user, args.password, args.host, args.release_name,
            args.install_repo, args.preseed_file, args.vmname
        )
    finally:
        disconnect_all()
