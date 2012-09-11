import boxes
import time


install_commands = """
apt-get update
apt-get -y dist-upgrade
echo "xcp-networkd    xcp-xapi/networking_type        select  bridge" | \
debconf-set-selections
dpkg-divert --add --rename --divert \
/etc/grub.d/09_linux_xen /etc/grub.d/20_linux_xen
apt-get install -y xcp-xapi
"""

post_install_fixes_1 = r"""
echo 'TOOLSTACK=xapi' > /etc/default/xen
echo 'bridge' > /etc/xcp/network.conf
apt-get install -y qemu-common
echo 'auto lo' > /etc/network/interfaces
echo 'iface lo inet loopback' >> /etc/network/interfaces
echo 'auto xenbr0' >> /etc/network/interfaces
echo 'iface xenbr0 inet dhcp' >> /etc/network/interfaces
echo '    bridge_ports eth0' >> /etc/network/interfaces
sed -i "s/\\\$XEND status && return 1/return 0/" /etc/init.d/xend
update-rc.d xendomains disable
update-rc.d openvswitch-switch disable
reboot
"""

post_install_fixes_2 = r"""
xe pif-reconfigure-ip uuid=$(xe pif-list device=eth0 --minimal) mode=dhcp
echo 'auto lo' > /etc/network/interfaces
echo 'iface lo inet loopback' >> /etc/network/interfaces
"""

add_sr = r"""
SRDEVICE=/dev/sda7
. /etc/xcp/inventory
SR=$(xe sr-create \
host-uuid=$INSTALLATION_UUID \
type=ext \
name-label='Local storage' \
device-config:device=$SRDEVICE)
POOL=$(xe pool-list --minimal)
xe pool-param-set uuid=$POOL default-SR=$SR
"""


def install_xcp_xapi(user, password, host):
    target = boxes.Server(host, user, password)
    target.disable_known_hosts = True

    def line_by_line(cmds):
        for command in cmds.strip().split('\n'):
            target.run(command)

    target.wait_for_ssh()
    line_by_line(install_commands)
    line_by_line(post_install_fixes_1)
    boxes.disconnect_all()
    # Make sure, that the server rebooted
    time.sleep(120)
    target.wait_for_ssh()
    line_by_line(post_install_fixes_2)
    target.run(add_sr)

    # And a final reboot
    target.run("reboot")
    boxes.disconnect_all()


def main():
    import sys
    user, password, host = sys.argv[1:]
    install_xcp_xapi(user, password, host)
