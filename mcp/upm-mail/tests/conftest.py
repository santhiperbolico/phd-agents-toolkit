"""Shared fixtures for UPM mail MCP tests."""

import imaplib
import smtplib

import pytest

from upm_mail_mcp.config import KIND_STUDENT, Settings

STUDENT_ADDRESS = "nombre.apellido@alumnos.upm.es"
SAMPLE_BODY = "Body text"
SAMPLE_RAW = (
    b"From: Ada Lovelace <ada@upm.es>\r\n"
    b"To: alumno@alumnos.upm.es\r\n"
    b"Cc: tutor@upm.es\r\n"
    b"Subject: Hello\r\n"
    b"Date: Mon, 24 Aug 2026 10:00:00 +0200\r\n"
    b"\r\n" + SAMPLE_BODY.encode() + b"\r\n"
)


@pytest.fixture
def student_settings() -> Settings:
    return Settings(address=STUDENT_ADDRESS, password="secret", kind=KIND_STUDENT)


def fetch_entry(uid: str, raw: bytes, flags: str = r"\Seen") -> tuple[bytes, bytes]:
    """Build a fake IMAP FETCH tuple."""
    meta = f"1 (UID {uid} FLAGS ({flags}) RFC822 {{{len(raw)}}}".encode()
    return meta, raw


class FakeImap:
    """In-memory IMAP client used by mailbox tests."""

    def __init__(self) -> None:
        self.login_status = "OK"
        self.list_status = "OK"
        self.select_status = "OK"
        self.search_status = "OK"
        self.fetch_status = "OK"
        self.list_lines: list[bytes] = [b'(\\HasNoChildren) "/" INBOX']
        self.search_data: list[bytes] = [b"10 11 12"]
        self.fetch_data: list = []
        self.raise_on_login = False
        self.logged_out = False
        self.selected: str | None = None
        self.uid_calls: list[tuple] = []

    def login(self, user: str, password: str):
        if self.raise_on_login:
            raise imaplib.IMAP4.error("login failed")
        return self.login_status, [b"ok"]

    def logout(self):
        self.logged_out = True
        return "BYE", []

    def list(self):
        return self.list_status, self.list_lines

    def select(self, folder: str, readonly: bool = True):
        self.selected = folder
        return self.select_status, [b"1"]

    def uid(self, command: str, *args):
        self.uid_calls.append((command, args))
        if command == "SEARCH":
            return self.search_status, self.search_data
        return self.fetch_status, self.fetch_data


class FakeSmtp:
    """In-memory SMTP client used by mailbox tests."""

    def __init__(self) -> None:
        self.raise_auth = False
        self.raise_send = False
        self.started_tls = False
        self.logged_in: tuple[str, str] | None = None
        self.sent: tuple | None = None
        self.quit_called = False

    def starttls(self):
        self.started_tls = True
        return (220, b"ok")

    def login(self, user: str, password: str):
        if self.raise_auth:
            raise smtplib.SMTPAuthenticationError(535, b"auth")
        self.logged_in = (user, password)
        return (235, b"ok")

    def send_message(self, message, to_addrs=None):
        if self.raise_send:
            raise smtplib.SMTPException("send failed")
        self.sent = (message, list(to_addrs or []))

    def quit(self):
        self.quit_called = True


class FakeMailbox:
    """Mailbox double for service tests."""

    def __init__(self) -> None:
        self.folders = ["INBOX", "Sent"]
        self.uids = ["1", "2", "3"]
        self.summaries: list[dict] = []
        self.message: dict = {"uid": "3", "body": "hi"}
        self.sent: tuple | None = None
        self.search_calls: list[tuple] = []

    def list_folders(self) -> list[str]:
        return self.folders

    def search(self, folder: str, criteria) -> list[str]:
        self.search_calls.append((folder, list(criteria)))
        return self.uids

    def fetch_summaries(self, folder: str, uids) -> list[dict]:
        if self.summaries:
            return self.summaries
        return [{"uid": uid, "folder": folder} for uid in uids]

    def fetch_message(self, folder: str, uid: str) -> dict:
        return {**self.message, "folder": folder, "uid": uid}

    def send(self, to, subject, body, cc) -> None:
        self.sent = (list(to), subject, body, list(cc))
