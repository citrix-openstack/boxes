import sys
import argparse
import time

from boxes import Server, disconnect_all
from boxes.scripts.get_devstack_domu_ip import get_devstack_ip


def command(xenhost, xenpass, devstackpass, tempest_params):
    xen = Server(xenhost, 'root', xenpass)

    while True:
        devstack_ip = get_devstack_ip(xen)
        if devstack_ip:
            break
        time.sleep(1)

    devstack = Server(devstack_ip, 'stack', devstackpass)
    devstack.run(
        "rm -rf /opt/stack/tempest")
    devstack.run(
        "cd /opt/stack && git clone https://github.com/openstack/tempest.git")
    devstack.run(
        "cd /opt/stack/tempest && git checkout master")
    devstack.run(
        "/opt/stack/devstack/tools/configure_tempest.sh")
    devstack.run(
        "sudo pip install -U nose || true")
    devstack.run(
        "rm -f /opt/stack/tempest/tempest/tests/compute/test_console_output.py")
    devstack.run(
        """nosetests %s -v tempest -e "test_change_server_password" """
        % tempest_params)

    disconnect_all()

def main():
    parser = argparse.ArgumentParser(description='run tempest tests')
    parser.add_argument('xenhost', help='XenServer host')
    parser.add_argument('xenpass', help='XenServer password')
    parser.add_argument('devstackpass', help='Devstack password')
    parser.add_argument('--TempestParams', help='Additional tempest params',
        default='')

    args = parser.parse_args()
    command(args.xenhost, args.xenpass, args.devstackpass, args.TempestParams)
