import sys
import textwrap

from boxes import Server
from boxes.scripts import lib


def main():
    user, password, host, release_name, install_repo, preseed_file, vmname = sys.argv[1:]

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
        'xe vdi-create name-label="boot" sr-uuid={0} type=system virtual-size=8GiB'
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
    xenhost.run(textwrap.dedent(r"""
        xe vm-param-set uuid={0} PV-args="-- quiet console=hvc0 \
        partman/default_filesystem=ext3 \
        locale=en_GB \
        console-setup/ask_detect=false \
        keyboard-configuration/layoutcode=gb \
        netcfg/choose_interface=eth0 \
        netcfg/get_hostname={1} \
        netcfg/get_domain={2} \
        auto url={3}"
        """
        .format(vm, vmname, domain, preseed_file)))
    
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
