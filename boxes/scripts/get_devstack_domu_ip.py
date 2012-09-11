import sys
import boxes


def extract_ip(networks_line, iface):
    """
    Extract the ip from a xe vm-param-get --param-name=networks line
    Returns empty string on failure

    >>> extract_ip("1/ip: 10.0.0.3; 3/ip: 172.24.4.10; 2/ip: 10.219.2.199; 1/ip: 10.255.255.255", 2)
    '10.219.2.199'
    >>> extract_ip(None, 2)
    >>> extract_ip(' ', 2)
    """
    try:
        parts = networks_line.split("{iface}/ip: ".format(iface=iface))
        return parts[1].split(";")[0]
    except (IndexError, AttributeError):
        pass


def get_devstack_ip(xenhost):
    uuid = xenhost.run("xe vm-list name-label=DevStackOSDomU --minimal")
    if not uuid:
        uuid = xenhost.run("xe vm-list name-label=DevStackComputeSlave --minimal")

    network = xenhost.run(
        "xe vm-param-get uuid={uuid} param-name=networks --minimal".format(
        uuid=uuid))

    return extract_ip(network, 2)


def command(user, password, host):
    xenhost = boxes.Server(host, user, password)
    xenhost.disable_known_hosts = True
    return get_devstack_ip(xenhost)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Get the devstack domU IP')
    parser.add_argument('host', help='XenServer host name')
    parser.add_argument(
        '--password', help='Password for XenServer', default=None)
    parser.add_argument(
        '--user', help='User for XenServer', default='root')

    args = parser.parse_args()
    user, password, host = args.user, args.password, args.host
    print "IP of DevStackOSDomU is: {0}".format(command(user, password, host))
