import sys
import argparse
import time

from boxes import Server, disconnect_all
from boxes.scripts.get_devstack_domu_ip import get_devstack_ip



def command(xenhost, xenpass, devstackpass):
    xen = Server(xenhost, 'root', xenpass)
    while True:
        devstack_ip = get_devstack_ip(xen)
        if devstack_ip:
            break
        time.sleep(1)

    devstack = Server(devstack_ip, 'stack', devstackpass)

    devstack.wait_for_ssh()

    if is_run_sh_succeeded(devstack):
        return
    else:
        if rabbit_is_failing(devstack):
            restart_rabbit(devstack)
        time.sleep(5)
        start_run_sh(devstack)
        assert is_run_sh_succeeded(devstack)
    disconnect_all()


def runtail(devstack):
    return devstack.run("tail -3 /opt/stack/run.sh.log")


def is_run_sh_succeeded(devstack):
    while True:
        tail = runtail(devstack)
        if "++ failed" in tail:
            return False
        elif "stack.sh completed" in tail:
            return True
        else:
            time.sleep(1)


def rabbit_is_failing(devstack):
    rabbit_status = devstack.run("sudo /etc/init.d/rabbitmq-server status || true")
    return "Error: unable to connect" in rabbit_status


def restart_rabbit(devstack):
    devstack.run("sudo /etc/init.d/rabbitmq-server restart || true")


def start_run_sh(devstack):
    devstack.run("/opt/stack/run.sh > /opt/stack/run.sh.log 2>&1")


def main():
    parser = argparse.ArgumentParser(description='wait for devstack')
    parser.add_argument('xenhost', help='XenServer host')
    parser.add_argument('xenpass', help='XenServer password')
    parser.add_argument('devstackpass', help='Devstack password')
    args = parser.parse_args()
    command(args.xenhost, args.xenpass, args.devstackpass)
