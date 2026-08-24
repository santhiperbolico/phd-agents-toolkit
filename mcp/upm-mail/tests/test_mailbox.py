"""Tests for the IMAP/SMTP mailbox client."""

import imaplib
import smtplib

import pytest
from conftest import SAMPLE_BODY, SAMPLE_RAW, FakeImap, FakeSmtp, fetch_entry

from upm_mail_mcp.errors import MailAuthError, MailError
from upm_mail_mcp.mailbox import ImapSmtpMailbox


def _mailbox(settings, imap_client=None, smtp_client=None):
    imap_client = imap_client or FakeImap()
    smtp_client = smtp_client or FakeSmtp()
    box = ImapSmtpMailbox(
        settings,
        imap_factory=lambda host, port: imap_client,
        smtp_factory=lambda host, port: smtp_client,
    )
    return box, imap_client, smtp_client


def test_list_folders_parses_names(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.list_lines = [
        b'(\\HasNoChildren) "/" INBOX',
        b'(\\Noselect) "/" "."',
        b'(\\HasNoChildren) "/" "Sent Items"',
        "ignored",
    ]
    assert box.list_folders() == ["INBOX", "Sent Items"]
    assert imap_client.logged_out is True


def test_list_folders_rejects_bad_status(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.list_status = "NO"
    with pytest.raises(MailError, match="LIST"):
        box.list_folders()


def test_imap_login_error_becomes_auth_error(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.raise_on_login = True
    with pytest.raises(MailAuthError, match="IMAP"):
        box.list_folders()
    assert imap_client.logged_out is True


def test_imap_login_no_status(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.login_status = "NO"
    with pytest.raises(MailAuthError, match="login"):
        box.list_folders()


def test_search_returns_uids_and_selects_inbox(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    assert box.search("  ", ["ALL"]) == ["10", "11", "12"]
    assert imap_client.selected == "INBOX"


def test_search_empty(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.search_data = [b""]
    assert box.search("INBOX", ["ALL"]) == []


def test_fetch_summaries_and_message(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.fetch_data = [
        fetch_entry("12", SAMPLE_RAW),
        b")",
        (b"no-uid FLAGS () RFC822 {1}", b"x"),
    ]
    summaries = box.fetch_summaries("INBOX", ["12"])
    assert summaries[0]["uid"] == "12"
    assert summaries[0]["subject"] == "Hello"
    assert summaries[0]["unseen"] is False
    imap_client.fetch_data = [fetch_entry("12", SAMPLE_RAW, flags="")]
    detail = box.fetch_message("INBOX", "12")
    assert SAMPLE_BODY in str(detail["body"])
    assert detail["unseen"] is True


def test_fetch_summaries_empty_uids(student_settings) -> None:
    box, _, _ = _mailbox(student_settings)
    assert box.fetch_summaries("INBOX", []) == []


def test_fetch_message_missing_uid(student_settings) -> None:
    box, imap_client, _ = _mailbox(student_settings)
    imap_client.fetch_data = []
    with pytest.raises(MailError, match="was not found"):
        box.fetch_message("INBOX", "99")


def test_send_message_uses_starttls(student_settings) -> None:
    box, _, smtp_client = _mailbox(student_settings)
    box.send(["a@upm.es"], "Hi", "Body", ["c@upm.es"])
    assert smtp_client.started_tls is True
    assert smtp_client.logged_in == (student_settings.address, "secret")
    message, recipients = smtp_client.sent
    assert message["From"] == student_settings.address
    assert recipients == ["a@upm.es", "c@upm.es"]
    assert smtp_client.quit_called is True


def test_send_auth_and_smtp_errors(student_settings) -> None:
    box, _, smtp_client = _mailbox(student_settings)
    smtp_client.raise_auth = True
    with pytest.raises(MailAuthError, match="SMTP"):
        box.send(["a@upm.es"], "Hi", "Body", [])
    smtp_client.raise_auth = False
    smtp_client.raise_send = True
    with pytest.raises(MailError, match="send"):
        box.send(["a@upm.es"], "Hi", "Body", [])


def test_default_factories_pass_timeout(student_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    created = {}

    class FakeSsl:
        def __init__(self, host, port, timeout=None):
            created["imap"] = (host, port, timeout)

        def login(self, *args):
            raise imaplib.IMAP4.error("no")

        def logout(self):
            return "BYE", []

    class FakeSmtpClass:
        def __init__(self, host, port, timeout=None):
            created["smtp"] = (host, port, timeout)

        def starttls(self):
            return (220, b"ok")

        def login(self, *args):
            raise smtplib.SMTPAuthenticationError(535, b"auth")

        def quit(self):
            return (221, b"bye")

    monkeypatch.setattr("upm_mail_mcp.mailbox.imaplib.IMAP4_SSL", FakeSsl)
    monkeypatch.setattr("upm_mail_mcp.mailbox.smtplib.SMTP", FakeSmtpClass)
    box = ImapSmtpMailbox(student_settings)
    with pytest.raises(MailAuthError):
        box.list_folders()
    with pytest.raises(MailAuthError):
        box.send(["a@upm.es"], "Hi", "Body", [])
    assert created["imap"][2] == 30
    assert created["smtp"][2] == 30
