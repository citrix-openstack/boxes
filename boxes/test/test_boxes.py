from unittest import TestCase
import textwrap
import mock

from boxes import WebServer, Server, Pdu


class WebServerTestCase(TestCase):
    def test_url_for(self):
        server = Server("host", "user", "pass")
        ws = WebServer(server, "/var/www", "somedir/otherdir")

        self.assertEquals(
            "http://host/somedir/otherdir/fname",
            ws.url_for("fname"))

    def test_path_for(self):
        server = Server("host", "user", "pass")
        ws = WebServer(server, "/var/www", "somedir/otherdir")

        self.assertEquals(
            "http://host/somedir/otherdir/fname",
            ws.url_for("fname"))


class PduTestCase(TestCase):
    def test_login(self):
        c = mock.call
        browser = mock.Mock()

        pdu = Pdu("http://a", browser=browser)
        pdu.login("user", "pass")

        self.assertEquals([
            c.open("http://a/logon.htm"),
            c.select_form(nr=0),
            c.set_value('user', 'login_username'),
            c.set_value('pass', 'login_password'),
            c.submit(),
        ], browser.mock_calls)

    def test_navigate_to_control(self):
        c = mock.call
        browser = mock.Mock()

        pdu = Pdu(None, browser=browser)
        pdu.navigate_to_control()

        self.assertEquals([
            c.click_link(text='Device Manager'),
            c.open(mock.ANY),
            c.click_link(text='Control'),
            c.open(mock.ANY),
        ], browser.mock_calls)

    def test_select_immediate_reboot(self):
        c = mock.call
        browser = mock.Mock()
        outlet_ctrl = mock.Mock()
        item1 = mock.Mock()
        item1.name = "item1_name"
        item1.__repr__ = lambda x: "blah Reboot Immediate blah"
        item2 = mock.Mock()
        outlet_ctrl.items = [item1, item2]
        browser.find_control.return_value = outlet_ctrl

        pdu = Pdu(None, browser=browser)
        pdu.select_immediate_reboot()

        self.assertEquals([
            c.select_form(nr=0),
            c.find_control(name='rPDUOutletCtrl'),
        ], browser.mock_calls)
        self.assertEquals(
            ["item1_name"], outlet_ctrl.value)

    def test_logoff(self):
        c = mock.call
        browser = mock.Mock()

        pdu = Pdu(None, browser=browser)
        pdu.logoff()

        self.assertEquals([
            c.click_link(text_regex='Log Off.*'),
            c.open(mock.ANY),
        ], browser.mock_calls)

    def test_set_checkboxes(self):
        c = mock.call
        control = mock.Mock()
        browser = mock.Mock()
        response = mock.Mock()
        response.read.return_value = textwrap.dedent("""
        <html>
          <td>
            <input type="checkbox" name="OL_Cntrl_Col3_Btn" value="?9,2,2" />
          </td>
          <td class="on">&nbsp;On</td>
          <td noWrap>&nbsp;Somename     </td>
        </html>
        """)
        browser.response.return_value = response
        browser.form.find_control.return_value = control

        pdu = Pdu(None, browser=browser)
        pdu.set_checkbox("Somename")

        self.assertIn(
            c.form.find_control("OL_Cntrl_Col3_Btn"), browser.mock_calls)

        self.assertIn(
            c.submit(), browser.mock_calls)

        self.assertEquals(
            ['?9,2,2'], control.value)

    def test_body(self):
        c = mock.call
        browser = mock.Mock()
        response = mock.Mock()
        response.read.return_value = "somecontent"
        browser.response.return_value = response

        pdu = Pdu(None, browser=browser)
        body = pdu.body

        self.assertEquals("somecontent", body)
