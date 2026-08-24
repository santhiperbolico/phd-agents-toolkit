"""Tests for MCP tool wrappers."""

import pytest

from upm_mail_mcp import server
from upm_mail_mcp.config import KIND_STUDENT, Settings


def _invoke(tool, *args, **kwargs):
    """Call a FastMCP tool through its underlying function when present."""
    target = getattr(tool, "fn", tool)
    return target(*args, **kwargs)


class FakeService:
    """Minimal service double for MCP tool tests."""

    def list_folders(self):
        return ["INBOX"]

    def list_messages(self, folder, limit, unread_only, from_address, subject, text):
        return [
            {
                "folder": folder,
                "limit": limit,
                "unread_only": unread_only,
                "from_address": from_address,
                "subject": subject,
                "text": text,
            }
        ]

    def get_message(self, uid, folder):
        return {"uid": uid, "folder": folder}

    def send_message(self, to, subject, body, cc):
        return f"sent:{to}:{subject}:{body}:{cc}"


@pytest.fixture
def fake_service(monkeypatch: pytest.MonkeyPatch) -> FakeService:
    service = FakeService()
    monkeypatch.setattr(server, "get_service", lambda: service)
    return service


def test_folder_and_message_tools(fake_service: FakeService) -> None:
    assert _invoke(server.list_folders) == ["INBOX"]
    rows = _invoke(
        server.list_messages,
        folder="Sent",
        limit=5,
        unread_only=True,
        from_address="ada@upm.es",
        subject="Hi",
        text="agenda",
    )
    assert rows[0]["folder"] == "Sent"
    assert rows[0]["unread_only"] is True
    assert _invoke(server.get_message, "12", "INBOX") == {"uid": "12", "folder": "INBOX"}


def test_send_message_tool(fake_service: FakeService) -> None:
    result = _invoke(server.send_message, "a@upm.es", "Hi", "Body", "c@upm.es")
    assert result == "sent:a@upm.es:Hi:Body:c@upm.es"


def test_get_service_uses_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        server,
        "load_settings",
        lambda: Settings(
            address="ada@alumnos.upm.es",
            password="secret",
            kind=KIND_STUDENT,
        ),
    )
    service = server.get_service()
    assert service.settings.imap_host == "correo.alumnos.upm.es"
