import platform  # For getting the operating system name
import subprocess  # For executing a shell command
from app import mail
from app.config import MAIL_SERVER, ADMINS


def test_ping_google(google_host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", google_host]

    assert subprocess.call(command) == 0


def test_ping_mailserver():
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", MAIL_SERVER]

    assert subprocess.call(command) == 0


def test_client(client):
    response = client.get("/index")
    assert response.status_code == 200


def test_email(test_app):
    test_context, test_mail = test_app
    with test_context:
        with test_mail.record_messages() as outbox:
            test_mail.send_message(
                subject="test",
                sender=ADMINS[0],
                recipients=["mimmo@gmail.com"],
                body="testing",
            )

            assert len(outbox) == 1
            assert outbox[0].subject == "test"
