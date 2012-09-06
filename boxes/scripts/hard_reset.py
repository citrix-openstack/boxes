import argparse
import mechanize
import logging
import boxes

logger = logging.getLogger(__name__)


def hard_reset(pdu_user, pdu_pass, pdu_address, machine_label, machine_port):
    pdu = boxes.Pdu(pdu_address, mechanize.Browser())
    pdu.login(pdu_user, pdu_pass)

    try:
        pdu.navigate_to_control()
        pdu.select_immediate_reboot()
        pdu.set_checkbox(machine_label)
        expected_message = (
            "Outlet/s {0} selected for Reboot Immediate.".format(machine_port))
        if expected_message not in pdu.body:
            raise Exception("expected message not found")

        logger.info("Rebooting NOW")
        pdu.browser.select_form(nr=0)
        pdu.browser.submit(label="Apply")

    except Exception as e:
        logging.warning(e)
    finally:
        pdu.logoff()


def main():
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description="Hard reset a machine by controlling the pdu")
    parser.add_argument("pdu_user", help="The user to access APC PDU")
    parser.add_argument("pdu_pass", help="Password for your user")
    parser.add_argument(
        "pdu_address",
        help="Address to your PDU (http://your.pdus.ip.address)")
    parser.add_argument(
        "machine_label",
        help="The label that identifies your machine within the PDU")
    parser.add_argument("machine_port", help="pdu port for the machine")
    args = parser.parse_args()

    hard_reset(
        args.pdu_user, args.pdu_pass, args.pdu_address,
        args.machine_label, args.machine_port)
