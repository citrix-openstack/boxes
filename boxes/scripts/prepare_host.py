import argparse
from boxes import Server, disconnect_all
import logging


logger = logging.getLogger(__name__)


def _setup_ssh(host, user, password, pubkey, license_server):
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

def setup_license(host, user, password, pubkey, license_server):
    server = Server(host, user, password)
    server.disable_known_hosts = True

    if license_server is None:
        return

    logger.info('Setting licences')
    host_uuid = server.run('xe host-list --minimal')

    server.run(
        'xe host-apply-edition '
        'host-uuid=%s edition="platinum" '
        'license-server-address="%s" '
        'license-server-port="27000"' % (host_uuid, license_server))


def setup_ssh():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Prepare a machine ')
    parser.add_argument('host', help='Host')
    parser.add_argument('user', help='user')
    parser.add_argument('password', help='password')
    parser.add_argument('pubkey', help='Public key to copy')

    args = parser.parse_args()
    _setup_ssh(args.host, args.user, args.password, args.pubkey)

def prepare_xs():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Prepare a XenServer for CI')
    parser.add_argument('host', help='Host')
    parser.add_argument('user', help='user')
    parser.add_argument('password', help='password')
    parser.add_argument('pubkey', help='Public key to copy')
    parser.add_argument('--license_server', help='Address of license server',
                        default=None)

    args = parser.parse_args()
    _setup_ssh(args.host, args.user, args.password, args.pubkey)
    setup_license(args.host, args.user, args.password, args.pubkey,
            args.license_server)

