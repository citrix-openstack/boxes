from setuptools import setup


setup(
    name='boxes',
    version='0.0',
    description='Automate your boxes',
    packages=['boxes'],
    install_requires=['fabric', 'lxml'],
    entry_points = {
        'console_scripts': [
            'install_xcp_xapi = boxes.scripts.install_xcp_xapi:main'
        ]
    }
)
