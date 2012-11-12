import argparse
from boxes import Server, disconnect_all
import logging
import tempfile
import sys


logger = logging.getLogger(__name__)

EXTRA_START = '# EXTRA_CONFIG START'

def set_extra_config(fname, extra_config):
    with open(fname, 'rb') as f:
        original_content = f.readlines()

    # Split extra config
    new_lines = []
    for line in original_content:
        if line.startswith(EXTRA_START):
            break
        new_lines.append(line)

    # Add extra config
    if extra_config:
        new_lines.append(EXTRA_START + '\n')
        for line in extra_config:
            new_lines.append(line)

    with open(fname, 'wb') as f:
        for line in new_lines:
            f.write(line)


def command(host, filename, user, password):
    server = Server(host, user, password)
    server.disable_known_hosts = True

    extra_config = sys.stdin.readlines()

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.file.close()

    try:
        server.get(filename, tmp.name)
        set_extra_config(tmp.name, extra_config)
        server.put(tmp.name, filename)
    finally:
        disconnect_all()


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='set the tail of a file')
    parser.add_argument('host', help='Devstack host')
    parser.add_argument('filename', help='name of the file')
    parser.add_argument('--user', type=str,
                        help='User to use for connection', default='stack')
    parser.add_argument('--password', type=str,
                        help='Password for connection', default=None)

    args = parser.parse_args()
    command(args.host, args.filename, args.user, args.password)
