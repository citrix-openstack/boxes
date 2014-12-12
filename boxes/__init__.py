import re
import os
from fabric.api import put, run, get
from fabric.contrib.files import exists
from fabric.context_managers import settings, hide
from fabric.network import disconnect_all as fab_disconnect_all
import time
import socket
import logging


logger = logging.getLogger(__name__)


def disconnect_all():
    fab_disconnect_all()


class Server(object):
    def __init__(self, host, user, password=None):
        self.host = host
        self.user = user
        self.password = password
        self.disable_known_hosts = False

    @property
    def _settings(self):
        return dict(
            host_string=self.host,
            user=self.user,
            password=self.password,
            disable_known_hosts=self.disable_known_hosts)

    def put(self, local_path, remote_path):
        with self.fabric_settings():
            put(local_path, remote_path)

    def get(self, remote_path, local_path):
        with self.fabric_settings():
            get(remote_path, local_path)

    def run(self, command):
        with self.fabric_settings():
            return run(command, shell=False)

    def wait_for_ssh(self, timeout=10):
        return self.wait_for_ssh_with_retries(
            timeout, retry_condition=lambda x: True)

    def wait_for_ssh_with_retries(self, timeout, retry_condition):
        timeout = timeout
        iteration = 0
        while retry_condition(iteration):
            iteration += 1
            try:
                logger.info("Trying to tcp connect to ssh server...")
                socket.create_connection((self.host, 22), timeout=timeout)
                # A final sleep
                logger.info("tcp connection succeeded, additional delay")
                time.sleep(timeout)
                return True
            except Exception as e:
                logger.info("tcp connection failed, waiting")
                time.sleep(timeout)
        return False


    def fabric_settings(self):
        return settings(hide('everything'), **self._settings)

    def exists(self, path):
        with self.fabric_settings():
            return exists(path)


class WebServer(object):
    def __init__(self, server, www_root, subdir):
        self.server = server
        self.www_root = www_root
        self.subdir = subdir

    def path_for(self, fname):
        return os.path.join(
            self.www_root,
            self.subdir,
            fname)

    @property
    def settings(self):
        return dict(
            host=self.server.host,
            subdir=self.subdir)

    def url_for(self, name):
        return 'http://{host}/{subdir}/{name}'.format(
            **dict(self.settings, name=name))

    def publish(self, local, remote):
        self.server.put(
            local,
            self.path_for(remote))
        return url_for(remote)


class Pdu(object):
    def __init__(self, url, browser=None):
        self.url = url
        self.browser = browser

    def set_checkbox(self, label):
        import lxml.html
        body = self.browser.response().read()
        html = lxml.html.fromstring(body)
        regex = r".*%s\s+" % label
        result, = [
            i for i in
            html.cssselect("td")
            if re.match(regex, i.text_content())
        ]
        input_element = result.getprevious().getprevious().getchildren()[0]
        attrs = dict((name, value) for name, value in input_element.items())

        assert 'checkbox' == attrs['type']
        br = self.browser
        br.select_form(nr=0)
        form = br.form
        form.find_control(attrs['name']).value = [attrs['value']]
        br.submit()

    def login(self, username, password):
        br = self.browser
        br.open(self.url + "/logon.htm")
        br.select_form(nr=0)
        br.set_value(username, 'login_username')
        br.set_value(password, 'login_password')
        br.submit()

    def navigate_to_control(self):
        br = self.browser
        r = br.click_link(text='Device Manager')
        br.open(r)
        r = br.click_link(text='Control')
        br.open(r)

    def select_immediate_reboot(self):
        br = self.browser
        br.select_form(nr=0)
        c = br.find_control(name='rPDUOutletCtrl')
        names = [i.name for i in c.items if 'Reboot Immediate' in repr(i)]
        assert 1 == len(names)
        c.value = names

    @property
    def body(self):
        return self.browser.response().read()

    def logoff(self):
        br = self.browser
        r = br.click_link(text_regex='Log Off.*')
        br.open(r)
