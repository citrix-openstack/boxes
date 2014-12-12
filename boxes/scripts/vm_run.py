import argparse
import logging

from boxes.scripts import lib
from boxes import Server


logger = logging.getLogger(__name__)

def vm_run(args):
    vm = Server(args.vm_ip, args.username, args.password)
    vm.verbose = args.verbose
    vm.disable_known_hosts = True
    if args.keyfile:
        vm.key_filenames.append(args.keyfile)

    vm.put(args.bash_script, 'vm_run.sh')
    logging.info("Running {bash_script} on remote system".format(
        bash_script=args.bash_script))
    vm.run('bash vm_run.sh')


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Run a script on a vm"
    )
    parser.add_argument('vm_ip', help='IP address for the VM')
    parser.add_argument('bash_script', help='bash script to run')
    parser.add_argument(
        '--keyfile', help='Keyfile to use', default="")
    parser.add_argument(
        '--username', help='Username for the VM', default="ubuntu")
    parser.add_argument(
        '--password', help='Password for the vm')
    parser.add_argument(
        '--verbose', action="store_true",
        default=False, help='Verbosely print out what is happening')

    vm_run(parser.parse_args())

