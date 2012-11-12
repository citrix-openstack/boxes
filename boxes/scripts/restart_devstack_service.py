import argparse
from boxes import Server, disconnect_all
import logging


logger = logging.getLogger(__name__)


def command(host, service, user, password):
    server = Server(host, user, password)
    server.disable_known_hosts = True

    try:
        tempfile = server.run('tempfile')
        server.run('echo -ne "\\003\\x10\\015" > %s' % tempfile)
        server.run('screen -S stack -X bufferfile %s' % tempfile)
        server.run('screen -S stack -X readbuf')
        server.run('screen -S stack -p %s -X paste .' % service)
    finally:
        disconnect_all()


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='restart a devstack service '
    'by sending ctrl-c, ctrl-p, enter to the screen window')
    parser.add_argument('host', help='Devstack host')
    parser.add_argument('service', help='Service to restart (Like c-vol)')
    parser.add_argument('--user', type=str,
                        help='User to use for connection', default='stack')
    parser.add_argument('--password', type=str,
                        help='Password for connection', default=None)

    args = parser.parse_args()
    command(args.host, args.service, args.user, args.password)
