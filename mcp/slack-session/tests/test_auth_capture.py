"""Tests for Slack credential parsing helpers."""

import pytest

from slack_session_mcp.auth_capture import (
    credentials_complete,
    merge_workspace_entry,
    parse_team_id_from_url,
    parse_token_from_post_data,
    pick_session_cookie,
    workspace_to_entry,
)
from slack_session_mcp.config import WorkspaceConfig
from slack_session_mcp.errors import ConfigError


@pytest.mark.parametrize(
    "url, team_id",
    [
        ("https://app.slack.com/client/T0123ABCD/C9876", "T0123ABCD"),
        ("https://app.slack.com/client/T0AAA/", "T0AAA"),
        ("https://slack.com/signin", ""),
    ],
)
def test_parse_team_id_from_url(url: str, team_id: str) -> None:
    assert parse_team_id_from_url(url) == team_id


def test_parse_token_from_post_data_reads_form_body() -> None:
    body = "token=xoxc-123-456&channel=C1"
    assert parse_token_from_post_data(body) == "xoxc-123-456"


def test_parse_token_from_bytes_reads_binary_body() -> None:
    from slack_session_mcp.auth_capture import parse_token_from_bytes

    body = b"prefix\xfftoken=xoxc-123-456&channel=C1"
    assert parse_token_from_bytes(body) == "xoxc-123-456"


def test_parse_token_from_url_query_reads_query_param() -> None:
    from slack_session_mcp.auth_capture import parse_token_from_url_query

    url = "https://euclid.slack.com/api/auth.test?token=xoxc-123-456"
    assert parse_token_from_url_query(url) == "xoxc-123-456"


def test_parse_token_from_playwright_request_ignores_non_api_urls() -> None:
    from slack_session_mcp.auth_capture import parse_token_from_playwright_request

    class FakeRequest:
        url = "https://app.slack.com/static/loader.js"

    assert parse_token_from_playwright_request(FakeRequest()) == ""


def test_scrape_token_from_page_html_reads_api_token() -> None:
    from slack_session_mcp.auth_capture import scrape_token_from_page_html

    html = '<script>"api_token":"xoxc-from-html"</script>'
    assert scrape_token_from_page_html(html) == "xoxc-from-html"


def test_pick_session_cookie_returns_d_value() -> None:
    cookies = [{"name": "d", "value": "xoxd-cookie"}, {"name": "other", "value": "x"}]
    assert pick_session_cookie(cookies) == "xoxd-cookie"


@pytest.mark.parametrize(
    "team_id, token, cookie, expected",
    [
        ("T123", "xoxc-aaa", "xoxd-bbb", True),
        ("A123", "xoxc-aaa", "xoxd-bbb", False),
        ("T123", "bad", "xoxd-bbb", False),
    ],
)
def test_credentials_complete(team_id: str, token: str, cookie: str, expected: bool) -> None:
    assert credentials_complete(team_id, token, cookie) is expected


def test_merge_workspace_entry_replaces_same_alias() -> None:
    existing = "euclid:T111:xoxc-old:xoxd-old,desi:T222:xoxc-desi:xoxd-desi"
    merged = merge_workspace_entry(existing, "euclid:T999:xoxc-new:xoxd-new")
    assert "T999" in merged
    assert "xoxc-new" in merged
    assert "desi:T222" in merged
    assert "xoxc-old" not in merged


def test_merge_workspace_entry_rejects_invalid_entry() -> None:
    with pytest.raises(ConfigError):
        merge_workspace_entry("", "bad-entry")


def test_workspace_to_entry_uses_team_id() -> None:
    workspace = WorkspaceConfig(
        alias="euclid",
        host_slug="T111",
        token="xoxc-aaa",
        session_cookie="xoxd-bbb",
        team_id="T111",
    )
    assert workspace_to_entry(workspace) == "euclid:T111:xoxc-aaa:xoxd-bbb"
