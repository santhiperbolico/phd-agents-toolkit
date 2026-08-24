"""Tests for high-level mailbox operations."""

import pytest
from conftest import FakeMailbox

from upm_mail_mcp.errors import MailError
from upm_mail_mcp.service import UpMailService


def test_list_folders_delegates(student_settings) -> None:
    mailbox = FakeMailbox()
    service = UpMailService(student_settings, mailbox=mailbox)
    assert service.list_folders() == ["INBOX", "Sent"]


def test_list_messages_returns_newest_first(student_settings) -> None:
    mailbox = FakeMailbox()
    mailbox.uids = ["1", "2", "3", "4"]
    service = UpMailService(student_settings, mailbox=mailbox)
    rows = service.list_messages(limit=2, unread_only=True, from_address="ada@upm.es")
    assert [row["uid"] for row in rows] == ["4", "3"]
    folder, criteria = mailbox.search_calls[0]
    assert folder == "INBOX"
    assert criteria[0] == "UNSEEN"
    assert "FROM" in criteria


def test_list_messages_rejects_invalid_limit(student_settings) -> None:
    service = UpMailService(student_settings, mailbox=FakeMailbox())
    with pytest.raises(MailError, match="at least 1"):
        service.list_messages(limit=0)


def test_get_message_requires_uid(student_settings) -> None:
    service = UpMailService(student_settings, mailbox=FakeMailbox())
    with pytest.raises(MailError, match="uid"):
        service.get_message("  ")


def test_get_message_reads_folder(student_settings) -> None:
    mailbox = FakeMailbox()
    service = UpMailService(student_settings, mailbox=mailbox)
    row = service.get_message("12", folder="Sent")
    assert row["uid"] == "12"
    assert row["folder"] == "Sent"


@pytest.mark.parametrize(
    "to, subject, body, match",
    [
        ("", "Hi", "Body", "recipient"),
        ("ada@upm.es", "  ", "Body", "subject"),
        ("ada@upm.es", "Hi", "  ", "body"),
        ("not-an-address", "Hi", "Body", "Invalid"),
    ],
)
def test_send_message_validates(student_settings, to, subject, body, match) -> None:
    service = UpMailService(student_settings, mailbox=FakeMailbox())
    with pytest.raises(MailError, match=match):
        service.send_message(to, subject, body)


def test_send_message_success(student_settings) -> None:
    mailbox = FakeMailbox()
    service = UpMailService(student_settings, mailbox=mailbox)
    result = service.send_message(
        "a@upm.es, b@upm.es",
        "Hello",
        "Body",
        cc="c@upm.es",
    )
    assert result.startswith("Sent to")
    assert mailbox.sent[0] == ["a@upm.es", "b@upm.es"]
    assert mailbox.sent[1] == "Hello"
    assert mailbox.sent[3] == ["c@upm.es"]
