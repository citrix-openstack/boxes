import argparse
from boxes import Server, disconnect_all
import logging


logger = logging.getLogger(__name__)


def command(host, timeout):
    server = Server(host, None, None)
    server.wait_for_ssh(timeout=timeout)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='wait for ssh to come up')
    parser.add_argument('host', help='Host')
    parser.add_argument('--timeout', type=int,
                        help='Timeout for connection', default=5)

    args = parser.parse_args()
    command(args.host, args.timeout)
