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

Add Ubuntu 12.04 to your Xenserver's templates
==============================================
This utility will create a template, called:
"Ubuntu Precise Pangolin 12.04 (64-bit)", so that you can install that version
on your XenServer/XCP:

    add_precise_to_xs root rootpassword yourxenserver.yourdomain
