"""HTTP client for the Slack Web API using browser session credentials."""

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

from slack_session_mcp.config import TEAM_ID_PREFIX, WorkspaceConfig
from slack_session_mcp.errors import SlackApiError

ApiCaller = Callable[[str, str, dict[str, str]], dict[str, Any]]
SEARCH_API_HOST = "slack.com"


class SlackSessionClient:
    """Low-level Slack Web API client for one workspace."""

    def __init__(
        self,
        workspace: WorkspaceConfig,
        api_caller: ApiCaller | None = None,
    ) -> None:
        self.workspace = workspace
        self._api_caller = api_caller or self._default_api_call

    def call_api(self, method: str, params: dict[str, str | int | bool] | None = None) -> dict:
        """
        Call a Slack Web API method.

        Parameters
        ----------
        method
            API method name, for example ``conversations.history``.
        params
            Optional method parameters.

        Returns
        -------
        dict
            Parsed JSON response body.

        Raises
        ------
        SlackApiError
            If the HTTP request fails or Slack returns ``ok: false``.
        """
        payload = {"token": self.workspace.token}
        if params:
            payload.update({key: str(value) for key, value in params.items()})
        host = self._api_host(method)
        response = self._api_caller(host, method, payload)
        if not response.get("ok"):
            error = str(response.get("error", "unknown_error"))
            raise SlackApiError(f"Slack API {method} failed: {error}")
        return response

    def _api_host(self, method: str) -> str:
        if method.startswith("search."):
            return SEARCH_API_HOST
        if self.workspace.host_slug.startswith(TEAM_ID_PREFIX):
            return SEARCH_API_HOST
        return f"{self.workspace.host_slug}.slack.com"

    def _default_api_call(self, host: str, method: str, params: dict[str, str]) -> dict:
        url = f"https://{host}/api/{method}"
        body = urllib.parse.urlencode(params).encode()
        request = urllib.request.Request(url, data=body, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        request.add_header("Cookie", f"d={self.workspace.session_cookie}")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise SlackApiError(f"HTTP {exc.code} calling {method}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise SlackApiError(f"Network error calling {method}: {exc.reason}") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SlackApiError(f"Invalid JSON from {method}.") from exc
