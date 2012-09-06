import sys
import shutil
import tempfile
import urllib
import zipfile
from os import path

from boxes import Server

import logging

logger = logging.getLogger(__name__)


def extract_xapi_plugins(zipfilename, tempdir):
    filenames = []
    z = zipfile.ZipFile(zipfilename)
    for f in z.namelist():
        if 'plugins/xenserver/xenapi/etc/xapi.d/plugins/' in f:
            basename = path.basename(f)
            if basename:
                z.extract(f, tempdir)
                filenames.append(path.join(tempdir, f))
    z.close()
    return filenames


def get_xapi_plugin_target_dir(xenhost):
    dirs_to_search = [
        '/usr/lib/xcp/plugins',
        '/etc/xapi.d/plugins'
    for tgt_dir in dirs_to_search:
        if xenhost.exists(tgt_dir):
            return tgt_dir

    raise Exception


def main():
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    user, password, host = sys.argv[1:]

    tempdir = tempfile.mkdtemp()

    url = "https://github.com/openstack/nova/zipball/master/"

    zipfilename = path.join(tempdir, 'nova.zip')

    logger.info("Downloading %s to %s", url, zipfilename)
    urllib.urlretrieve(url, zipfilename)

    filenames = extract_xapi_plugins(zipfilename, tempdir)

    xenhost = Server(host, user, password)
    xenhost.disable_known_hosts = True

    tgt_dir = get_xapi_plugin_target_dir(xenhost)
    logger.info("Remote directory: %s", tgt_dir)

    for src_filename in filenames:
        basename = path.basename(src_filename)
        tgt_filename = path.join(tgt_dir, basename)

        if xenhost.exists(tgt_filename):
            logger.info("%s exists, skipping", tgt_filename)
            continue

        logger.info("copy %s to %s", src_filename, tgt_filename)
        xenhost.put(src_filename, tgt_filename)

        if not tgt_filename.endswith(".py"):
            logger.info("mark %s as executable", tgt_filename)
            xenhost.run("chmod +x {0}".format(tgt_filename))

    logger.info("remove temporary directory %s", tempdir)
    shutil.rmtree(tempdir)
