import sys
import argparse
import time
import logging

from boxes import Server, disconnect_all
from boxes.scripts.get_devstack_domu_ip import get_devstack_ip


logger = logging.getLogger(__name__)


def command(xenhost, xenpass, devstackpass):
    xen = Server(xenhost, 'root', xenpass)
    while True:
        devstack_ip = get_devstack_ip(xen)
        if devstack_ip:
            break
        time.sleep(1)

    devstack = Server(devstack_ip, 'stack', devstackpass)

    logger.info("Waiting for devstack machine")
    devstack.wait_for_ssh()

    logger.info("Checking run.sh results")
    if is_run_sh_succeeded(devstack):
        logger.info("run.sh succeeded")
    else:
        logger.info("run.sh failed, trying to fix it")
        if rabbit_is_failing(devstack):
            logger.info("rabbitmq is not running, restarting it")
            restart_rabbit(devstack)
        time.sleep(5)
        logger.info("Starting run.sh")
        start_run_sh(devstack)
        assert is_run_sh_succeeded(devstack)

    logger.info("Devstack is up and running, disconnecting")
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
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description='wait for devstack')
    parser.add_argument('xenhost', help='XenServer host')
    parser.add_argument('xenpass', help='XenServer password')
    parser.add_argument('devstackpass', help='Devstack password')
    args = parser.parse_args()
    command(args.xenhost, args.xenpass, args.devstackpass)
