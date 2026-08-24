"""Tests for Slack session environment settings."""

import pytest

from slack_session_mcp.config import (
    ENV_SESSION_COOKIE,
    ENV_WORKSPACES,
    load_settings,
    parse_workspace_entry,
    parse_workspaces,
)
from slack_session_mcp.errors import ConfigError


def test_parse_workspaces_accepts_team_id_and_per_workspace_cookies() -> None:
    workspaces = parse_workspaces("euclid:T111:xoxc-aaa:xoxd-aaa, desi:T222:xoxc-bbb:xoxd-bbb")
    assert len(workspaces) == 2
    assert workspaces[0].alias == "euclid"
    assert workspaces[0].host_slug == "T111"
    assert workspaces[0].session_cookie == "xoxd-aaa"
    assert workspaces[1].team_id == "T222"


def test_parse_workspace_entry_uses_shared_cookie_for_three_part_entry() -> None:
    workspace = parse_workspace_entry("euclid:euclid-team:xoxc-aaa", "xoxd-shared")
    assert workspace.session_cookie == "xoxd-shared"
    assert workspace.host_slug == "euclid-team"


def test_parse_workspace_entry_accepts_subdomain_and_team_id() -> None:
    workspace = parse_workspace_entry(
        "euclid:euclid-team:T111:xoxc-aaa:xoxd-aaa",
        "",
    )
    assert workspace.host_slug == "euclid-team"
    assert workspace.team_id == "T111"


@pytest.mark.parametrize(
    "raw, match",
    [
        ("", "required"),
        ("bad-format", "at least"),
        ("euclid::xoxc-aaa", "host"),
        ("euclid:team:not-xoxc", "xoxc-"),
        ("euclid:team:xoxc-aaa", "xoxd"),
        ("euclid:team:xoxc-aaa:not-xoxd", "xoxd-"),
        ("euclid:team:xoxc-aaa:xoxd-aaa,euclid:other:xoxc-bbb:xoxd-bbb", "Duplicate"),
    ],
)
def test_parse_workspaces_rejects_invalid(raw: str, match: str) -> None:
    with pytest.raises(ConfigError, match=match):
        parse_workspaces(raw, default_cookie="")


def test_load_settings_parses_per_workspace_credentials() -> None:
    settings = load_settings(
        {
            ENV_WORKSPACES: "euclid:T111:xoxc-aaa:xoxd-aaa,desi:T222:xoxc-bbb:xoxd-bbb",
        }
    )
    assert settings.default_session_cookie == ""
    assert settings.workspaces[0].token == "xoxc-aaa"
    assert settings.workspaces[1].session_cookie == "xoxd-bbb"


def test_load_settings_keeps_shared_cookie_fallback() -> None:
    settings = load_settings(
        {
            ENV_SESSION_COOKIE: " xoxd-shared ",
            ENV_WORKSPACES: "euclid:euclid-team:xoxc-aaa",
        }
    )
    assert settings.default_session_cookie == "xoxd-shared"
    assert settings.workspaces[0].session_cookie == "xoxd-shared"


@pytest.mark.parametrize(
    "env",
    [
        {},
        {ENV_WORKSPACES: "euclid:team:xoxc-aaa"},
    ],
)
def test_load_settings_rejects_missing_values(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_settings(env)
