"""FastMCP server exposing read-only Slack session tools."""

from fastmcp import FastMCP

from slack_session_mcp.config import load_settings
from slack_session_mcp.parsing import DEFAULT_LIMIT
from slack_session_mcp.service import SlackSessionService

mcp = FastMCP(name="slack-session")


def get_service() -> SlackSessionService:
    """Build a service from the current process environment."""
    return SlackSessionService(load_settings())


@mcp.tool()
def list_workspaces() -> list[dict[str, str]]:
    """List configured Slack workspaces (Euclid, DESI, etc.) and verify tokens."""
    return get_service().list_workspaces()


@mcp.tool()
def list_channels(
    workspace: str,
    include_private: bool = True,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, str | bool]]:
    """
    List channels the session user belongs to.

    Parameters
    ----------
    workspace
        Workspace alias from ``list_workspaces``.
    include_private
        Include private channels when true.
    limit
        Maximum number of channels (1-50).
    """
    return get_service().list_channels(
        workspace=workspace,
        include_private=include_private,
        limit=limit,
    )


@mcp.tool()
def read_channel(
    workspace: str,
    channel: str,
    limit: int = DEFAULT_LIMIT,
    oldest: str = "",
    latest: str = "",
) -> list[dict[str, str | int | bool]]:
    """
    Read recent messages from a channel (newest first).

    Parameters
    ----------
    workspace
        Workspace alias from ``list_workspaces``.
    channel
        Channel name (``#foo`` or ``foo``) or channel ID.
    limit
        Maximum number of messages (1-50).
    oldest
        Optional oldest Slack timestamp.
    latest
        Optional latest Slack timestamp.
    """
    return get_service().read_channel(
        workspace=workspace,
        channel=channel,
        limit=limit,
        oldest=oldest,
        latest=latest,
    )


@mcp.tool()
def search_messages(
    workspace: str,
    query: str,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, str | int | bool]]:
    """
    Search messages with Slack syntax (``in:channel``, ``from:@user``, dates).

    Parameters
    ----------
    workspace
        Workspace alias from ``list_workspaces``.
    query
        Slack search query.
    limit
        Maximum number of matches (1-50).
    """
    return get_service().search_messages(workspace=workspace, query=query, limit=limit)


@mcp.tool()
def read_thread(
    workspace: str,
    channel: str,
    thread_ts: str,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, str | int | bool]]:
    """
    Read messages in a thread.

    Parameters
    ----------
    workspace
        Workspace alias from ``list_workspaces``.
    channel
        Channel name or ID that contains the thread.
    thread_ts
        Parent message timestamp from ``read_channel`` or ``search_messages``.
    limit
        Maximum number of thread messages (1-50).
    """
    return get_service().read_thread(
        workspace=workspace,
        channel=channel,
        thread_ts=thread_ts,
        limit=limit,
    )


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()
