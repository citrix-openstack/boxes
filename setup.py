from setuptools import setup


setup(
    name='boxes',
    version='0.8',
    description='Automate your boxes',
    packages=['boxes', 'boxes.scripts'],
    install_requires=['fabric'],
    package_data = {
        'boxes': ['pdu-requirements.txt', 'virt-kickstart']
    },
    entry_points = {
        'console_scripts': [
            'install_xcp_xapi = boxes.scripts.install_xcp_xapi:main',
            'create_start_deblike = boxes.scripts.create_start_deblike:main',
            'create_start_centos = boxes.scripts.create_start_centos:main',
            'install_openstack_plugins = boxes.scripts.install_openstack_plugins:main',
            'get_guest_ip = boxes.scripts.get_guest_ip:main',
            'hard_reset = boxes.scripts.hard_reset:main',
            'install_pxeboot_config = boxes.scripts.pxeboot_config:install_main',
            'remove_pxeboot_config = boxes.scripts.pxeboot_config:remove_main',
            'install_pdu_requirements = boxes.scripts.install_pdu_requirements:main',
            'wait_for_ssh = boxes.scripts.wait_for_ssh:main',
            'prepare_xs_for_devstack_ci = boxes.scripts.prepare_host:prepare_xs',
            'prepare_generic_host = boxes.scripts.prepare_host:setup_ssh',
            'run_exercise = boxes.scripts.run_exercise:main',
            'restart_devstack_service = boxes.scripts.restart_devstack_service:main',
            'set_extra_config = boxes.scripts.set_extra_config:main',
            'havana-demo-connect-network-to-phy = boxes.scripts.havana_demo:connect_network',
            'no_vm_with_name = boxes.scripts.no_vm_with_name:main',
            'publish_guest_tools = boxes.scripts.publish_guest_tools:main',
            'bxs-delete-vms = boxes.scripts.delete_vms:main',
            'bxs-list-vms = boxes.scripts.list_vms:main',
            'bxs-export-xva = boxes.scripts.export_xva:main',
            'bxs-import-xva = boxes.scripts.import_xva:main',
            'bxs-list-xvas = boxes.scripts.list_xvas:main',
            'bxs-wait-for-halt = boxes.scripts.wait_for_halt:main',
            'bxs-start-vm = boxes.scripts.start_vm:main',
            'bxs-vm-ip = boxes.scripts.get_guest_ip:main',
            'bxs-delete-xva = boxes.scripts.delete_xva:main',
            'bxs-vm-set = boxes.scripts.set_vm:main',
        ]
    }
)
