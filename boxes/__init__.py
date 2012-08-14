import re
import os
import lxml.html
from fabric.api import put, run
from fabric.context_managers import settings


class Server(object):
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    @property
    def _settings(self):
        return dict(
            host_string=self.host,
            user=self.user,
            password=self.password)

    def put(self, local_path, remote_path):
        with settings(**self._settings):
            put(local_path, remote_path)

    def run(self, command):
        with settings(**self._settings):
            return run(command)


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
