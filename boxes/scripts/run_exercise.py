import argparse
from boxes import Server, disconnect_all
import logging


logger = logging.getLogger(__name__)


def command(host, user, password):
    server = Server(host, user, password)
    server.disable_known_hosts = True
    try:
        server.run("cd devstack && ./exercise.sh")
    finally:
        disconnect_all()


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='run exercise.sh on a devstack box')
    parser.add_argument('host', help='Devstack host')
    parser.add_argument('--user', type=str,
                        help='User to use for connection', default='stack')
    parser.add_argument('--password', type=str,
                        help='Password for connection', default=None)

    args = parser.parse_args()
    command(args.host, args.user, args.password)
