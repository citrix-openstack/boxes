import argparse
import boxes


def get_remote_pxe_filename(mac):
    mac = mac.lower().replace(':', '-')
    return '/tftpboot/pxelinux.cfg/01-{0}'.format(mac)


def install_pxeboot_config(user, host, mac, pxe_file):
    pxe_server = boxes.Server(host, user, None)
    remote_file = get_remote_pxe_filename(mac)
    pxe_server.put(pxe_file, remote_file)
    pxe_server.run('chmod +r {0}'.format(remote_file))


def remove_pxeboot_config(user, host, mac):
    pxe_server = boxes.Server(host, user, None)
    remote_file = get_remote_pxe_filename(mac)
    pxe_server.run('rm -f {0}'.format(remote_file))


def install_main():
    parser = argparse.ArgumentParser(description='Install a pxeboot config')
    parser.add_argument('user', help='User for PXE Server')
    parser.add_argument('host', help='PXE Server')
    parser.add_argument('mac', help='Mac address (xx:xx:xx:xx:xx:xx)')
    parser.add_argument('pxe_file',
        help='the pxe file you want to put on the server')
    args = parser.parse_args()
    install_pxeboot_config(args.user, args.host, args.mac, args.pxe_file)
    boxes.disconnect_all()


def remove_main():
    parser = argparse.ArgumentParser(description='Remove a pxeboot config')
    parser.add_argument('user', help='User for PXE Server')
    parser.add_argument('host', help='PXE Server')
    parser.add_argument('mac', help='Mac address (xx:xx:xx:xx:xx:xx)')
    args = parser.parse_args()
    remove_pxeboot_config(args.user, args.host, args.mac)
    boxes.disconnect_all()
