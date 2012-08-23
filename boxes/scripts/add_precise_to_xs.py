import sys
import logging

from boxes import Server


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    username, password, host = sys.argv[1:]

    xenhost = Server(host, username, password)
    xenhost.disable_known_hosts = True

    lucid_label = 'Ubuntu Lucid Lynx 10.04 (64-bit)'
    precise_label = 'Ubuntu Precise Pangolin 12.04 (64-bit)'

    logger.info('Query for existing precise template')

    precise_uuid = xenhost.run(
        'xe template-list name-label="{0}" --minimal'.format(precise_label))

    if not precise_uuid:
        logger.info('No precise template found, cloning Lucid')
        lucid_uuid = xenhost.run(
            'xe template-list name-label="{0}" --minimal'.format(lucid_label))
        precise_uuid = xenhost.run(
            'xe vm-clone uuid={0} new-name-label="{1}"'
            .format(lucid_uuid, precise_label))

    logger.info('Setting parameters for Precise')
    xenhost.run(
        'xe template-param-set other-config:default_template=true other-config:debian-release=precise uuid={0}'
        .format(precise_uuid))
