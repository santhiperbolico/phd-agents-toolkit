"""Tests for the Slack HTTP client."""

import pytest
from conftest import EUCLID_WORKSPACE

from slack_session_mcp.client import SlackSessionClient
from slack_session_mcp.errors import SlackApiError


def test_call_api_raises_on_slack_error() -> None:
    def caller(host: str, method: str, params: dict[str, str]) -> dict:
        return {"ok": False, "error": "invalid_auth"}

    client = SlackSessionClient(EUCLID_WORKSPACE, api_caller=caller)
    with pytest.raises(SlackApiError, match="invalid_auth"):
        client.call_api("auth.test")


def test_call_api_uses_team_id_host_for_regular_methods() -> None:
    seen: dict[str, str] = {}

    def caller(host: str, method: str, params: dict[str, str]) -> dict:
        seen["host"] = host
        seen["method"] = method
        seen["token"] = params["token"]
        return {"ok": True}

    client = SlackSessionClient(EUCLID_WORKSPACE, api_caller=caller)
    client.call_api("conversations.list", {"limit": "1"})
    assert seen["host"] == "slack.com"
    assert seen["method"] == "conversations.list"
    assert seen["token"] == EUCLID_WORKSPACE.token


def test_call_api_uses_subdomain_host_when_configured() -> None:
    seen: dict[str, str] = {}

    def caller(host: str, method: str, params: dict[str, str]) -> dict:
        seen["host"] = host
        return {"ok": True}

    workspace = EUCLID_WORKSPACE
    workspace = workspace.__class__(
        alias=workspace.alias,
        host_slug="euclid-team",
        token=workspace.token,
        session_cookie=workspace.session_cookie,
        team_id="T111",
    )
    client = SlackSessionClient(workspace, api_caller=caller)
    client.call_api("conversations.list")
    assert seen["host"] == "euclid-team.slack.com"


def test_call_api_uses_slack_host_for_search() -> None:
    seen: dict[str, str] = {}

    def caller(host: str, method: str, params: dict[str, str]) -> dict:
        seen["host"] = host
        seen["method"] = method
        return {"ok": True, "messages": {"matches": []}}

    client = SlackSessionClient(EUCLID_WORKSPACE, api_caller=caller)
    client.call_api("search.messages", {"query": "hello"})
    assert seen["host"] == "slack.com"
    assert seen["method"] == "search.messages"
