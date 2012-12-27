import argparse
import logging

import textwrap

from boxes import Server, disconnect_all
from boxes.scripts import lib


def command(user, xspass, host, suite, install_repo, preseed_file,
            vmname, hddsize, mac, fstype, usrpwd, packages, timezone, ntpserver, username,
            httpmirrorhost, httpmirrordirectory):
    template = 'Ubuntu Lucid Lynx 10.04 (64-bit)'

    xenhost = Server(host, user, xspass)
    xenhost.disable_known_hosts = True

    template_uuid = lib.template_uuid(xenhost, template)

    vm = lib.clone_template(xenhost, template_uuid, vmname)

    xenhost.put(preseed_file, "/opt/xensource/www/{0}.preseed".format(vm))

    preseed_url = "{0}/{1}.preseed".format(host, vm)

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
        'sr-uuid={0} type=system virtual-size={1}GiB'
        .format(sr, hddsize))

    xenhost.run(
        'xe vbd-create vm-uuid={0} vdi-uuid={1} device=0 bootable=true'
        .format(vm, vdi))

    xenhost.run(
        'xe vm-param-set uuid={0} other-config:install-repository={1}'
        .format(vm, install_repo))

    xenhost.run(
        'xe vm-param-set uuid={0} other-config:debian-release={1}'
        .format(vm, suite))

    domain = 'somedomain'
    xenhost.run(
        textwrap.dedent(r"""
        xe vm-param-set uuid={0} PV-args="-- quiet console=hvc0 \
        locale=en_GB \
        keyboard-configuration/layoutcode=gb \
        netcfg/choose_interface=eth0 \
        netcfg/get_hostname={1} \
        netcfg/get_domain={2} \
        mirror/suite={4} \
        mirror/udeb/suite={4} \
        partman/default_filesystem={5} \
        passwd/user-password={6} \
        passwd/user-password-again={6} \
        pkgsel/include={7} \
        time/zone={8} \
        clock-setup/ntp-server={9} \
        passwd/username={10} \
        mirror/http/hostname={11} \
        mirror/http/directory={12} \
        auto url={3}"
        """.format(vm, vmname, domain, preseed_url, suite, fstype, usrpwd, packages, timezone, ntpserver, username,
            httpmirrorhost, httpmirrordirectory)))

    bridge_name = 'xenbr0'

    net = xenhost.run(
        'xe network-list bridge={0} --minimal'
        .format(bridge_name))

    additional_net_options = "mac={0}".format(mac) if mac else ""

    xenhost.run(
        'xe vif-create network-uuid={0} vm-uuid={1} device=0 {2}'
        .format(net, vm, additional_net_options))

    xenhost.run(
        'xe vm-start uuid={0}'
        .format(vm))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Install a debian -like vm in XenServer')
    parser.add_argument('host', help='XenServer host')
    parser.add_argument('preseed_file', help='Preseed file to use')
    parser.add_argument('vmname', help='Name for the virtual machine')
    parser.add_argument('usrpwd', help='Password for the user on the new system')
    parser.add_argument(
        '--hddsize', help='Disk size for vm in Gigabytes (8)', default="8")
    parser.add_argument(
        '--mac', help='MAC address for vm', default="")
    parser.add_argument(
        '--fstype', help='Type of filesystem (ext4)', default="ext4")
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')
    parser.add_argument(
        '--packages', help='Comma separated list of additional packages', default="")
    parser.add_argument(
        '--timezone', help='Timezone for the new system (Europe/London)', default="Europe/London")
    parser.add_argument(
        '--ntpserver', help='NTP server to use (0.us.pool.ntp.org)', default="0.us.pool.ntp.org")
    parser.add_argument(
        '--username', help='Name for the user on the new system (ubuntu)', default="ubuntu")
    parser.add_argument(
        '--suite', help='Suite to install (precise)', default="precise")
    parser.add_argument(
        '--install_repo', help='Distro url used by XenServer (http://archive.ubuntu.com/ubuntu)',
        default="http://archive.ubuntu.com/ubuntu")
    parser.add_argument(
        '--httpmirrorhost', help='http mirror host used during installation (archive.ubuntu.com)',
        default="archive.ubuntu.com")
    parser.add_argument(
        '--httpmirrordirectory', help='http mirror directory used during installation (/ubuntu)',
        default="/ubuntu")
    parser.add_argument(
        '--aptcachernghost', help='A host that runs apt-cacher-ng - to speed up installation. It will override httpmirrorhost, install_repo',
        default="")

    args = parser.parse_args()

    if args.aptcachernghost:
        httpmirrorhost = args.aptcachernghost + ":3142"
        install_repo = "http://" + httpmirrorhost + "/archive.ubuntu.com" + args.httpmirrordirectory
    else:
        httpmirrorhost = args.httpmirrorhost
        install_repo = args.install_repo

    try:
        command(
            args.xsuser, args.xspass, args.host, args.suite,
            install_repo, args.preseed_file, args.vmname, args.hddsize,
            args.mac, args.fstype, args.usrpwd, args.packages, args.timezone,
            args.ntpserver, args.username, httpmirrorhost, args.httpmirrordirectory
        )
    finally:
        disconnect_all()
