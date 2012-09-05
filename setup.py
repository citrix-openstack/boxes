from setuptools import setup


setup(
    name='boxes',
    version='0.0',
    description='Automate your boxes',
    packages=['boxes', 'boxes.scripts'],
    install_requires=['fabric', 'lxml'],
    entry_points = {
        'console_scripts': [
            'install_xcp_xapi = boxes.scripts.install_xcp_xapi:main',
            'create_start_deblike = boxes.scripts.create_start_deblike:main',
            'install_openstack_plugins = boxes.scripts.install_openstack_plugins:main',
            'get_devstack_domu_ip = boxes.scripts.get_devstack_domu_ip:main',
            'start_devstack = boxes.scripts.start_devstack:main',
            'run_tempest_tests = boxes.scripts.run_tempest_tests:main',
            'hard_reset = boxes.scripts.hard_reset:main',
        ]
    }
)
