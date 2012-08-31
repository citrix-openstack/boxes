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


def command(user, password, host):
    xenhost = boxes.Server(host, user, password)
    xenhost.disable_known_hosts = True

    uuid = xenhost.run("xe vm-list name-label=DevStackOSDomU --minimal")
    network = xenhost.run(
        "xe vm-param-get uuid={uuid} param-name=networks --minimal".format(
        uuid=uuid))

    return extract_ip(network, 2)


def main():
    user, password, host = sys.argv[1:]
    print "IP of DevStackOSDomU is: {0}".format(command(user, password, host))
