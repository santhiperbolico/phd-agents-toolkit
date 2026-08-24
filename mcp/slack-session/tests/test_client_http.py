"""Tests for default HTTP transport in the Slack client."""

import json
from unittest.mock import MagicMock, patch

import pytest
from conftest import EUCLID_COOKIE, EUCLID_WORKSPACE

from slack_session_mcp.client import SlackSessionClient
from slack_session_mcp.errors import SlackApiError


def test_default_api_call_posts_token_and_cookie() -> None:
    client = SlackSessionClient(EUCLID_WORKSPACE)
    response_body = json.dumps({"ok": True, "team": "Euclid"}).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = response_body
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False
    with patch("urllib.request.urlopen", return_value=mock_response) as urlopen:
        result = client.call_api("auth.test")
    assert result["team"] == "Euclid"
    request = urlopen.call_args.args[0]
    assert request.get_header("Cookie") == f"d={EUCLID_COOKIE}"
    assert b"token=xoxc-euclid-token" in request.data


def test_default_api_call_raises_on_http_error() -> None:
    client = SlackSessionClient(EUCLID_WORKSPACE)
    import urllib.error

    error = urllib.error.HTTPError(
        url="https://example.com",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=MagicMock(read=MagicMock(return_value=b"denied")),
    )
    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(SlackApiError, match="HTTP 401"):
            client.call_api("auth.test")
