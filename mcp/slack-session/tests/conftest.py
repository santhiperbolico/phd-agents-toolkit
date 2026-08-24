"""Shared fixtures for Slack session MCP tests."""

import pytest

from slack_session_mcp.config import Settings, WorkspaceConfig

EUCLID_COOKIE = "xoxd-euclid-cookie"
DESI_COOKIE = "xoxd-desi-cookie"
EUCLID_WORKSPACE = WorkspaceConfig(
    alias="euclid",
    host_slug="T-YYYY",
    token="xoxc-euclid-token",
    session_cookie=EUCLID_COOKIE,
    team_id="T-YYYY",
)
DESI_WORKSPACE = WorkspaceConfig(
    alias="desi",
    host_slug="T-XXXX",
    token="xoxc-desi-token",
    session_cookie=DESI_COOKIE,
    team_id="T-XXXX",
)


def make_settings() -> Settings:
    return Settings(default_session_cookie="", workspaces=(EUCLID_WORKSPACE, DESI_WORKSPACE))


@pytest.fixture
def slack_settings() -> Settings:
    return make_settings()


class FakeSlackClient:
    """In-memory Slack API double for service tests."""

    def __init__(self, responses: dict[str, dict] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, dict]] = []

    def call_api(self, method: str, params: dict | None = None) -> dict:
        self.calls.append((method, dict(params or {})))
        if method not in self.responses:
            return {"ok": True}
        response = self.responses[method]
        if response.get("ok") is False:
            from slack_session_mcp.errors import SlackApiError

            raise SlackApiError(f"Slack API {method} failed: {response.get('error')}")
        return response
