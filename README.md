boxes
=====

Python Library to control your boxes - servers, pdus, etc

Install XCP-XAPI
================
WARNING: this script will wipe your sda7. For more info, see:

http://wiki.openstack.org/XenServer/Install/XcpXapiOnPrecise

If you want to get started with XCP-XAPI, and you have an minimal Ubuntu
installation, and an sda7 free to be destroyed:

    install_xcp_xapi root rootpassword yourhost.yourdomain

This script will leave a box with 
  * xcp-xapi
  * bridge networking
  * dhcp on eth0
  * ext storage


Install and start a Debian-Like VM
==================================
To Install a precise machine:

    create_start_deblike root rootpassword yourxenserver.yourdomain precise \
    http://youraptcacher-ng.server:3142/archive.ubuntu.net/ubuntu \
    http://yourwebserver/yourpreseed.cfg machinename    


Install OpenStack Plugins to your XenServer
===========================================
This script will download the latest nova zipball, and copy the openstack
plugins to your xenserver. Existing files will not be overwritten.

    install_openstack_plugins root rootpassword yourxenserver.yourdomain

Get the IP of your DevstackDomU
===============================
If you installed devstack on your xenserver, you can use this script to get
the IP of that machine:

    get_devstack_domu_ip root rootpassword yourxenserver.yourdomain

