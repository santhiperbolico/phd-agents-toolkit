"""Tests for read-only Slack service operations."""

import pytest
from conftest import DESI_WORKSPACE, EUCLID_WORKSPACE, FakeSlackClient, make_settings

from slack_session_mcp.errors import ChannelNotFoundError, WorkspaceNotFoundError
from slack_session_mcp.service import SlackSessionService


def build_service(fake: FakeSlackClient) -> SlackSessionService:
    clients = {
        EUCLID_WORKSPACE.alias: fake,
        DESI_WORKSPACE.alias: fake,
    }
    return SlackSessionService(make_settings(), clients=clients)


def test_list_workspaces_returns_team_metadata() -> None:
    fake = FakeSlackClient({"auth.test": {"ok": True, "team": "Euclid", "user": "ada"}})
    service = build_service(fake)
    rows = service.list_workspaces()
    assert rows[0]["team"] == "Euclid"
    assert rows[0]["alias"] == "euclid"


def test_list_channels_filters_non_member_channels() -> None:
    fake = FakeSlackClient(
        {
            "conversations.list": {
                "ok": True,
                "channels": [
                    {"id": "C1", "name": "general", "is_member": True, "is_private": False},
                    {"id": "C2", "name": "secret", "is_member": False, "is_private": True},
                ],
            }
        }
    )
    service = build_service(fake)
    rows = service.list_channels("euclid", limit=10)
    assert len(rows) == 1
    assert rows[0]["name"] == "general"


def test_read_channel_resolves_name_and_reverses_messages() -> None:
    fake = FakeSlackClient(
        {
            "conversations.list": {
                "ok": True,
                "channels": [{"id": "C1", "name": "general", "is_member": True}],
            },
            "conversations.history": {
                "ok": True,
                "messages": [
                    {"ts": "2.0", "user": "U1", "text": "new"},
                    {"ts": "1.0", "user": "U2", "text": "old"},
                ],
            },
        }
    )
    service = build_service(fake)
    rows = service.read_channel("euclid", "#general", limit=2)
    assert [row["text"] for row in rows] == ["new", "old"]


def test_read_channel_accepts_channel_id_without_lookup() -> None:
    fake = FakeSlackClient(
        {
            "conversations.history": {
                "ok": True,
                "messages": [{"ts": "1.0", "user": "U1", "text": "hi"}],
            }
        }
    )
    service = build_service(fake)
    rows = service.read_channel("euclid", "C123", limit=1)
    assert rows[0]["text"] == "hi"
    assert fake.calls[0][0] == "conversations.history"


def test_search_messages_requires_query() -> None:
    service = build_service(FakeSlackClient())
    with pytest.raises(ValueError, match="query"):
        service.search_messages("euclid", "  ")


def test_search_messages_returns_matches() -> None:
    fake = FakeSlackClient(
        {
            "search.messages": {
                "ok": True,
                "messages": {
                    "matches": [
                        {
                            "ts": "1.0",
                            "user": "U1",
                            "text": "deadline",
                            "channel": {"id": "C1", "name": "general"},
                        }
                    ]
                },
            }
        }
    )
    service = build_service(fake)
    rows = service.search_messages("desi", "deadline", limit=5)
    assert rows[0]["channel_name"] == "general"


def test_read_thread_returns_chronological_messages() -> None:
    fake = FakeSlackClient(
        {
            "conversations.list": {
                "ok": True,
                "channels": [{"id": "C1", "name": "general", "is_member": True}],
            },
            "conversations.replies": {
                "ok": True,
                "messages": [
                    {"ts": "1.0", "user": "U1", "text": "parent"},
                    {"ts": "1.1", "user": "U2", "text": "reply"},
                ],
            },
        }
    )
    service = build_service(fake)
    rows = service.read_thread("euclid", "general", "1.0", limit=10)
    assert [row["text"] for row in rows] == ["parent", "reply"]


def test_unknown_workspace_raises() -> None:
    service = build_service(FakeSlackClient())
    with pytest.raises(WorkspaceNotFoundError, match="Unknown workspace"):
        service.list_channels("missing")


def test_unknown_channel_raises() -> None:
    fake = FakeSlackClient(
        {
            "conversations.list": {
                "ok": True,
                "channels": [{"id": "C1", "name": "general", "is_member": True}],
            }
        }
    )
    service = build_service(fake)
    with pytest.raises(ChannelNotFoundError, match="not found"):
        service.read_channel("euclid", "missing", limit=1)
