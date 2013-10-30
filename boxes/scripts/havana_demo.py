import sys
import argparse

from boxes import Server


class XenserverCore(object):
    def __init__(self, params):
        self.params = params
        self.server = Server(params.xenserver_host, 'root')
        self.server.disable_known_hosts = True

    @property
    def network_labels(self):
        return self.server.run('xe network-list params=name-label --minimal').split(',')

    @property
    def pif_devices(self):
        return self.server.run('xe pif-list params=device --minimal').split(',')

    def _get_network_uuid(self, network_name):
        network, = self.server.run(
            'xe network-list name-label={0} --minimal'.format(
                network_name)).split(',')

        return network

    def _get_pif_uuid(self, device):
        pif, = self.server.run(
            'xe pif-list device={0} --minimal'.format(
                device)).split(',')

        return pif

    def get_bridge_for_network(self, network_name):
        network = self._get_network_uuid(network_name)
        return self.server.run(
            'xe network-param-get param-name=bridge uuid={network}'.format(
                **locals()))

    def get_interfaces_of_bridge(self, bridge):
        brctl_out = self.server.run(
            'brctl show {0}'.format(bridge))
        lines = brctl_out.split('\n')[1:]
        return [line.split()[-1].strip() for line in lines]

    def add_interface_to_bridge(self, interface, bridge):
        self.server.run(
            'brctl addif {bridge} {interface}'.format(**locals()))

    def remove_interface_from_bridge(self, interface, bridge):
        self.server.run(
            'brctl delif {bridge} {interface}'.format(**locals()))


class CommandFailure(Exception):
    pass


class ConnectNetwork(object):
    def __init__(self, params):
        self.params = params
        self.xenserver = XenserverCore(params)
        self.error_messages = []

    def __call__(self):
        params = self.params

        if params.network not in self.xenserver.network_labels:
            raise CommandFailure(
                "network {0} was not found. Available networks: {1}".format(
                    params.network, self.xenserver.network_labels))

        if params.interface not in self.xenserver.pif_devices:
            raise CommandFailure(
                "interface {0} was not found. Available interfaces: {1}".format(
                    params.interface, self.xenserver.pif_devices))

        bridge = self.xenserver.get_bridge_for_network(params.network)
        if params.interface in self.xenserver.get_interfaces_of_bridge(bridge):
            return

        default_bridge_for_interface = 'br{0}'.format(params.interface)
        if params.interface in self.xenserver.get_interfaces_of_bridge(default_bridge_for_interface):
            self.xenserver.remove_interface_from_bridge(
                params.interface, default_bridge_for_interface)

        self.xenserver.add_interface_to_bridge(
            params.interface, bridge)


def get_params(argv):
    """
    >>> get_params('xenserver network interface'.split()).xenserver_host
    'xenserver'
    >>> get_params('xenserver network interface'.split()).network
    'network'
    >>> get_params('xenserver network interface'.split()).interface
    'interface'
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('xenserver_host')
    parser.add_argument('network')
    parser.add_argument('interface')
    return parser.parse_args(argv)


def connect_network():
    params = get_params(sys.argv[1:])
    command = ConnectNetwork(params)
    try:
        command()
    except CommandFailure as e:
        sys.stderr.write(e.message + '\n')
        sys.exit(1)
