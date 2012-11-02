import sys
import argparse
import time
import tempfile

from boxes import Server, disconnect_all
from boxes.scripts.get_devstack_domu_ip import get_devstack_ip


def command(xenhost, xenpass, devstackpass, tempest_params, tempest_repo,
            tempest_branch, no_clone, devstack_ip, suite):

    if not devstack_ip:
        xen = Server(xenhost, 'root', xenpass)
        xen.disable_known_hosts = True

        while True:
            devstack_ip = get_devstack_ip(xen)
            if devstack_ip:
                break
            time.sleep(1)

    devstack = Server(devstack_ip, 'stack', devstackpass)
    devstack.disable_known_hosts = True

    do_clone = not no_clone

    if do_clone:
        devstack.run(
            "rm -rf /opt/stack/tempest")
        devstack.run(
            "cd /opt/stack && git clone %s" % tempest_repo)
    else:
        devstack.run(
            "cd /opt/stack/tempest && git pull")

    devstack.run(
        "cd /opt/stack/tempest && git checkout %s" % tempest_branch)
    devstack.run(
        "/opt/stack/devstack/tools/configure_tempest.sh")
    devstack.run(
        "sudo pip install -U nose || true")

    temp_ini_file = tempfile.NamedTemporaryFile(delete=False)
    temp_ini_file.close()

    tempest_conf = "/opt/stack/tempest/etc/tempest.conf"
    devstack.get(tempest_conf, temp_ini_file.name)
    edit_ini_file(temp_ini_file.name)
    devstack.put(temp_ini_file.name, tempest_conf)

    devstack.run(
        "rm -f "
        "/opt/stack/tempest/tempest/tests/compute/test_console_output.py")
    devstack.run(
        """cd /opt/stack/tempest && nosetests %s %s -v -e "test_change_server_password" """
        % (suite, tempest_params))

    disconnect_all()


def edit_ini_file(ini_file):
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read(ini_file)

    config.set('compute', 'use_block_migration_for_live_migration', 'true')
    config.set('compute', 'live_migration_available', 'true')
    #config.set('compute', 'network_for_ssh', 'private')
    #config.set('compute', 'flavor_ref', '2')
    #config.set('compute', 'ssh_user', 'cirros')

    with open(ini_file, 'wb') as modified_config:
        config.write(modified_config)
        modified_config.close()


def main():
    parser = argparse.ArgumentParser(description='run tempest tests')
    parser.add_argument('xenhost', help='XenServer host')
    parser.add_argument('xenpass', help='XenServer password')
    parser.add_argument('devstackpass', help='Devstack password')
    parser.add_argument(
        '--suite', help='Suite to run', default='tempest')
    parser.add_argument(
        '--TempestParams', help='Additional tempest params', default='')
    parser.add_argument(
        '--tempestRepo', help='Tempest repository to use',
        default='https://github.com/openstack/tempest.git')
    parser.add_argument(
        '--tempestBranch', help='Tempest branch to use', default='master')
    parser.add_argument(
        '--noClone', help='Do not perform a clone, just a pull',
        action='store_true')
    parser.add_argument(
        '--devStackIp', help='IP for devstack machine '
        'If specified, the hypervisor will not be asked for the '
        'devstack IP', default='')

    args = parser.parse_args()
    command(
        args.xenhost, args.xenpass, args.devstackpass,
        args.TempestParams, args.tempestRepo, args.tempestBranch, args.noClone,
        args.devStackIp, args.suite)
