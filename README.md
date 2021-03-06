boxes
=====

Python Library to control your boxes - servers, pdus, etc

Install XCP-XAPI
================
A way of automatically install an xcp-xapi on top of a minimal Ubuntu 12.04
installation. 

WARNING: this script will wipe your sda7. The script is an automated execution
of steps covered by:

http://wiki.openstack.org/XenServer/Install/XcpXapiOnPrecise

Usage:

    install_xcp_xapi root rootpassword yourhost.yourdomain

This script will leave a box with 
  * components: xcp-xapi
    * bridge networking
    * dhcp on eth0
    * ext storage on sda7


Install and start a Debian-Like VM
==================================
To Install a precise machine:

    create_start_deblike yourxenserver.yourdomain \
    yourpreseed.cfg machinename password    

For further options, and default values, type:

    create_start_deblike --help


Install OpenStack Plugins to your XenServer
===========================================
This script will download the latest nova zipball, and copy the openstack
plugins to your xenserver. Existing files will not be overwritten.

    install_openstack_plugins root rootpassword yourxenserver.yourdomain

Get the IP of your DevstackDomU
===============================
If you installed devstack on your xenserver, you can use this script to get
the IP of that machine. For more information, see:

    get_devstack_domu_ip -h

Immediate Reboot your machine
=============================
you will need to install additional dependencies to remote your PDU:

    install_pdu_requirements

This small script emulates a browser, communicates with an APC PDU, to reboot
the selected server. For more information:

    hard_reset -h

Install a PXE file on your PXE server
=====================================
Put a file to a PXE server.

    install_pxeboot_config -h

Remove a PXE file from your PXE server
======================================

    remove_pxeboot_config -h

Run exercise.sh
===============

    run_exercise -h

Restart a devstack service
==========================
Send Ctrl+C, Ctrl+P, and Enter to the given devstack screen.

    restart_devstack_service -h

Set extra config
================
Read some bytes in the standard input, and append those lines to the file
specified, on the remote system.

    set_extra_config -h
    cat /dev/null | set_extra_config devstackip /etc/cinder/cinder.conf
    echo "someoption=True" | set_extra_config devstackip /etc/cinder/cinder.conf
