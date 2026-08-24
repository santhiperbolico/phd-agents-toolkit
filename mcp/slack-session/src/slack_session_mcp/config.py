"""Load Slack session MCP settings from the environment."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from slack_session_mcp.errors import ConfigError

ENV_SESSION_COOKIE = "SLACK_SESSION_COOKIE"
ENV_WORKSPACES = "SLACK_WORKSPACES"
TEAM_ID_PREFIX = "T"
TOKEN_PREFIX = "xoxc-"
COOKIE_PREFIX = "xoxd-"


@dataclass(frozen=True)
class WorkspaceConfig:
    """One Slack workspace reachable with a browser session token."""

    alias: str
    host_slug: str
    token: str
    session_cookie: str
    team_id: str = ""

    @property
    def subdomain(self) -> str:
        """Return the workspace subdomain when ``host_slug`` is not a team ID."""
        if self.host_slug.startswith(TEAM_ID_PREFIX):
            return ""
        return self.host_slug


def parse_workspace_entry(item: str, default_cookie: str) -> WorkspaceConfig:
    """
    Parse one workspace entry from ``SLACK_WORKSPACES``.

    Supported shapes (comma-separated in the env var):

    - ``alias:host:xoxc-token:xoxd-cookie`` — one Slack account per workspace.
    - ``alias:host:xoxc-token`` — uses ``SLACK_SESSION_COOKIE`` as fallback.
    - ``alias:subdomain:team_id:xoxc-token:xoxd-cookie`` — subdomain plus team ID.

    ``host`` may be a workspace subdomain (``euclid-consortium``) or a team ID
    from ``app.slack.com/client/TEAM_ID/...`` (``T01234567``).

    Parameters
    ----------
    item
        Single workspace entry.
    default_cookie
        Fallback session cookie from ``SLACK_SESSION_COOKIE``.

    Returns
    -------
    WorkspaceConfig
        Parsed workspace definition.

    Raises
    ------
    ConfigError
        If the entry is malformed.
    """
    parts = [part.strip() for part in item.split(":") if part.strip()]
    if len(parts) < 3:
        raise ConfigError(
            f"{ENV_WORKSPACES} entries need at least alias:host:xoxc-token, got {item!r}."
        )
    alias = parts[0]
    token_index = next(
        (index for index, part in enumerate(parts) if part.startswith(TOKEN_PREFIX)), -1
    )
    if token_index < 0:
        raise ConfigError(f"Workspace {alias!r} token must start with {TOKEN_PREFIX}.")
    host_parts = parts[1:token_index]
    if not host_parts:
        raise ConfigError(f"Workspace {alias!r} is missing host or team id.")
    token = parts[token_index]
    cookie = ""
    if token_index + 1 < len(parts):
        cookie = parts[token_index + 1]
    if not cookie:
        cookie = default_cookie
    if not cookie:
        raise ConfigError(
            f"Workspace {alias!r} needs an xoxd cookie in the entry or {ENV_SESSION_COOKIE}."
        )
    if not cookie.startswith(COOKIE_PREFIX):
        raise ConfigError(f"Workspace {alias!r} cookie must start with {COOKIE_PREFIX}.")
    host_slug, team_id = _parse_host_parts(host_parts)
    return WorkspaceConfig(
        alias=alias,
        host_slug=host_slug,
        token=token,
        session_cookie=cookie,
        team_id=team_id,
    )


def _parse_host_parts(host_parts: list[str]) -> tuple[str, str]:
    if len(host_parts) == 1:
        host = host_parts[0]
        if host.startswith(TEAM_ID_PREFIX):
            return host, host
        return host, ""
    if len(host_parts) == 2:
        subdomain, team_id = host_parts
        if not team_id.startswith(TEAM_ID_PREFIX):
            raise ConfigError("team id must start with T when subdomain and team id are both set.")
        return subdomain, team_id
    raise ConfigError("too many host fields before the xoxc token.")


def parse_workspaces(raw: str, default_cookie: str = "") -> tuple[WorkspaceConfig, ...]:
    """
    Parse the ``SLACK_WORKSPACES`` environment value.

    Parameters
    ----------
    raw
        Comma-separated workspace entries.
    default_cookie
        Optional fallback cookie for three-field entries.

    Returns
    -------
    tuple of WorkspaceConfig
        Parsed workspace definitions.

    Raises
    ------
    ConfigError
        If the string is empty or an entry is malformed.
    """
    text = raw.strip()
    if not text:
        raise ConfigError(f"{ENV_WORKSPACES} is required.")
    workspaces: list[WorkspaceConfig] = []
    seen_aliases: set[str] = set()
    for entry in text.split(","):
        item = entry.strip()
        if not item:
            continue
        workspace = parse_workspace_entry(item, default_cookie)
        if workspace.alias in seen_aliases:
            raise ConfigError(
                f"Duplicate workspace alias {workspace.alias!r} in {ENV_WORKSPACES}."
            )
        seen_aliases.add(workspace.alias)
        workspaces.append(workspace)
    if not workspaces:
        raise ConfigError(f"{ENV_WORKSPACES} must list at least one workspace.")
    return tuple(workspaces)


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Slack session MCP server."""

    default_session_cookie: str
    workspaces: tuple[WorkspaceConfig, ...]


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """
    Load settings from environment variables.

    Parameters
    ----------
    environ
        Mapping of environment variables. Defaults to ``os.environ``.

    Returns
    -------
    Settings
        Parsed workspaces and optional shared session cookie.

    Raises
    ------
    ConfigError
        If workspace configuration is missing or invalid.
    """
    env = os.environ if environ is None else environ
    default_cookie = env.get(ENV_SESSION_COOKIE, "").strip()
    workspaces = parse_workspaces(env.get(ENV_WORKSPACES, ""), default_cookie=default_cookie)
    return Settings(default_session_cookie=default_cookie, workspaces=workspaces)
