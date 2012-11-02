import argparse
from boxes import Server, disconnect_all
import logging


logger = logging.getLogger(__name__)


def command(host, user, password, pubkey, license_server):
    server = Server(host, user, password)
    server.disable_known_hosts = True

    logger.info('Clean out .ssh')
    server.run('rm -rf .ssh')
    server.run('mkdir .ssh')
    server.run('chmod 0755 .ssh')

    logger.info('Copy over public key')
    server.put(pubkey, '.ssh/authorized_keys')
    server.run('chmod 0600 .ssh/authorized_keys')

    logger.info('Generating new ssh key on host')
    server.run('ssh-keygen -t rsa -N "" -f .ssh/id_rsa')

    logger.info('Add generated key to known_hosts')
    server.run('cat .ssh/id_rsa.pub >> .ssh/authorized_keys')

    logger.info('Establishing a connection to cache host key')
    server.run('ssh -o "StrictHostKeyChecking no" localhost hostname')

    logger.info('Setting licences')
    host_uuid = server.run('xe host-list --minimal')

    server.run(
        'xe host-apply-edition '
        'host-uuid=%s edition="platinum" '
        'license-server-address="%s" '
        'license-server-port="27000"' % (host_uuid, license_server))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Prepare a XenServer for CI')
    parser.add_argument('host', help='Host')
    parser.add_argument('user', help='user')
    parser.add_argument('password', help='password')
    parser.add_argument('pubkey', help='Public key to copy')
    parser.add_argument('license_server', help='Address of license server')

    args = parser.parse_args()
    command(args.host, args.user, args.password, args.pubkey,
            args.license_server)
