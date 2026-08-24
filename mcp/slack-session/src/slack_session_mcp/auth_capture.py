"""Parse and format Slack session credentials for MCP configuration."""

import re
import urllib.parse
from dataclasses import dataclass

from slack_session_mcp.config import WorkspaceConfig, parse_workspaces
from slack_session_mcp.errors import SlackSessionMcpError

TEAM_ID_PATTERN = re.compile(r"/client/(T[A-Z0-9]+)/")
TOKEN_PREFIX = "xoxc-"
COOKIE_PREFIX = "xoxd-"
TOKEN_TEXT_PATTERN = re.compile(r"xoxc-[A-Za-z0-9-]+")
TOKEN_BYTES_PATTERN = re.compile(rb"xoxc-[A-Za-z0-9-]+")
TOKEN_QUERY_PATTERN = re.compile(r"[?&]token=(xoxc-[^&]+)")
SLACK_CLIENT_URL = "https://app.slack.com/client"


@dataclass(frozen=True)
class CapturedCredentials:
    """Slack browser session values needed for one workspace entry."""

    alias: str
    team_id: str
    token: str
    session_cookie: str

    def to_entry(self) -> str:
        """
        Format credentials as one ``SLACK_WORKSPACES`` entry.

        Returns
        -------
        str
            ``alias:team_id:xoxc-token:xoxd-cookie``.
        """
        return f"{self.alias}:{self.team_id}:{self.token}:{self.session_cookie}"


class AuthExtractError(SlackSessionMcpError):
    """Raised when browser credential extraction fails."""


def parse_team_id_from_url(url: str) -> str:
    """
    Extract a Slack team ID from an ``app.slack.com`` client URL.

    Parameters
    ----------
    url
        Browser location, for example ``https://app.slack.com/client/T123/C456``.

    Returns
    -------
    str
        Team ID starting with ``T``, or an empty string when not found.
    """
    match = TEAM_ID_PATTERN.search(url)
    if not match:
        return ""
    return match.group(1)


def parse_token_from_post_data(post_data: str | None) -> str:
    """
    Extract an ``xoxc`` token from a Slack API request body.

    Parameters
    ----------
    post_data
        URL-encoded form body from a browser network request.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    if not post_data:
        return ""
    parsed = urllib.parse.parse_qs(post_data, keep_blank_values=True)
    token_values = parsed.get("token", [])
    if not token_values:
        match = TOKEN_TEXT_PATTERN.search(post_data)
        return match.group(0) if match else ""
    token = token_values[0].strip()
    if token.startswith(TOKEN_PREFIX):
        return token
    return ""


def parse_token_from_bytes(post_data: bytes | None) -> str:
    """
    Extract an ``xoxc`` token from raw request bytes.

    Parameters
    ----------
    post_data
        Raw HTTP request body.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    if not post_data:
        return ""
    match = TOKEN_BYTES_PATTERN.search(post_data)
    if not match:
        return ""
    return match.group(0).decode("ascii")


def parse_token_from_url_query(url: str) -> str:
    """
    Extract an ``xoxc`` token from a request URL query string.

    Parameters
    ----------
    url
        Full request URL.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    match = TOKEN_QUERY_PATTERN.search(url)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1))


def parse_token_from_playwright_request(request: object) -> str:
    """
    Safely extract an ``xoxc`` token from a Playwright request object.

    Parameters
    ----------
    request
        Playwright ``Request`` instance.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    url = str(getattr(request, "url", ""))
    if "/api/" not in url:
        return ""
    token = parse_token_from_url_query(url)
    if token:
        return token
    try:
        token = parse_token_from_post_data(getattr(request, "post_data", None))
        if token:
            return token
    except (UnicodeDecodeError, ValueError):
        pass
    try:
        return parse_token_from_bytes(getattr(request, "post_data_buffer", None))
    except (UnicodeDecodeError, ValueError):
        return ""
    return ""


def scrape_token_from_page_html(page_html: str) -> str:
    """
    Extract an ``xoxc`` token embedded in Slack boot HTML.

    Parameters
    ----------
    page_html
        Serialized page HTML or local storage dump.

    Returns
    -------
    str
        Token value, or an empty string when absent.
    """
    match = re.search(r'"api_token":"(xoxc-[^"]+)"', page_html)
    if match:
        return match.group(1)
    match = TOKEN_TEXT_PATTERN.search(page_html)
    return match.group(0) if match else ""


def pick_session_cookie(cookies: list[dict[str, str]]) -> str:
    """
    Return the Slack ``d`` session cookie from browser cookies.

    Parameters
    ----------
    cookies
        Playwright cookie dictionaries.

    Returns
    -------
    str
        Cookie value starting with ``xoxd-``, or an empty string.
    """
    for cookie in cookies:
        if cookie.get("name") != "d":
            continue
        value = str(cookie.get("value", "")).strip()
        if value.startswith(COOKIE_PREFIX):
            return value
    return ""


def credentials_complete(
    team_id: str,
    token: str,
    session_cookie: str,
) -> bool:
    """
    Return whether all required credential parts are present.

    Parameters
    ----------
    team_id
        Slack team ID.
    token
        Slack ``xoxc`` token.
    session_cookie
        Slack ``d`` cookie value.

    Returns
    -------
    bool
        True when every value is non-empty and correctly prefixed.
    """
    return (
        bool(team_id.startswith("T"))
        and token.startswith(TOKEN_PREFIX)
        and session_cookie.startswith(COOKIE_PREFIX)
    )


def merge_workspace_entry(existing: str, entry: str) -> str:
    """
    Insert or replace one workspace entry in ``SLACK_WORKSPACES``.

    Parameters
    ----------
    existing
        Current comma-separated workspace string, possibly empty.
    entry
        One ``alias:team:xoxc:xoxd`` entry to upsert by alias.

    Returns
    -------
    str
        Updated comma-separated workspace string.

    Raises
    ------
    ConfigError
        If ``entry`` is not a valid workspace definition.
    """
    new_workspace = parse_workspaces(entry, default_cookie="")[0]
    current = parse_workspaces(existing, default_cookie="") if existing.strip() else ()
    kept = [workspace for workspace in current if workspace.alias != new_workspace.alias]
    entries = [workspace_to_entry(workspace) for workspace in kept]
    entries.append(workspace_to_entry(new_workspace))
    return ",".join(entries)


def workspace_to_entry(workspace: WorkspaceConfig) -> str:
    """
    Serialize a workspace config as an environment entry.

    Parameters
    ----------
    workspace
        Parsed workspace configuration.

    Returns
    -------
    str
        ``alias:host:xoxc:xoxd`` string.
    """
    host = workspace.team_id or workspace.host_slug
    return f"{workspace.alias}:{host}:{workspace.token}:{workspace.session_cookie}"
