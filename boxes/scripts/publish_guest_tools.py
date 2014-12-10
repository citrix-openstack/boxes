import argparse
import logging

from boxes import Server


def publish_tools(args):
    xenhost = Server(args.host, args.xsuser, args.xspass)
    xenhost.disable_known_hosts = True

    pbd_uuid = xenhost.run(
        'xe sr-list params=PBDs name-label="XenServer Tools" --minimal')

    device_config = xenhost.run(
        'xe pbd-param-get uuid={pbd_uuid} param-name=device-config'.format(
            pbd_uuid=pbd_uuid))

    location = None
    for config_item in device_config.split(';'):
        if 'location: ' in config_item:
            location = config_item.replace('location: ', '')
            break

    assert location

    filenames = xenhost.run('ls {location}'.format(location=location))

    tools_iso_basename = None
    for filename in filenames.split(' '):
        if 'tools' in filename:
            tools_iso_basename = filename
            break

    assert tools_iso_basename

    tools_iso_path = location + '/' + tools_iso_basename

    temp_dir = xenhost.run('mktemp -d')

    xenhost.run('mount -o loop {tools_iso_path} {temp_dir}'.format(
        tools_iso_path=tools_iso_path, temp_dir=temp_dir))

    xenhost.run('rm -rf /opt/xensource/www/tools')
    xenhost.run('mkdir /opt/xensource/www/tools')

    utilities = xenhost.run(
        'find {temp_dir} -name "xe-guest-utilities*"'.format(
            temp_dir=temp_dir)
    )

    guest_tool = None
    for utility_raw in utilities.split('\n'):
        utility = utility_raw.strip()
        if 'amd64' in utility and '.deb' in utility:
            guest_tool = utility

    assert guest_tool

    xenhost.run('cp {guest_tool} /opt/xensource/www/tools/amd64.deb'.format(
        guest_tool=guest_tool))

    xenhost.run('umount {temp_dir}'.format(temp_dir=temp_dir))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Publish Xenserver tools on XenServer's "
        "builtin http server"
    )
    parser.add_argument('host', help='XenServer host')
    parser.add_argument(
        '--xsuser', help='Username for XenServer (root)', default="root")
    parser.add_argument(
        '--xspass', help='Password for XenServer')

    publish_tools(parser.parse_args())

