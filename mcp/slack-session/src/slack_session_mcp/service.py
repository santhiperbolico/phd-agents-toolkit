"""Read-only Slack operations used by the session MCP tools."""

from slack_session_mcp.client import SlackSessionClient
from slack_session_mcp.config import Settings
from slack_session_mcp.errors import ChannelNotFoundError, WorkspaceNotFoundError
from slack_session_mcp.parsing import (
    clamp_limit,
    is_channel_id,
    normalize_channel_name,
    simplify_message,
)


class SlackSessionService:
    """High-level read-only operations across configured Slack workspaces."""

    def __init__(
        self,
        settings: Settings,
        clients: dict[str, SlackSessionClient] | None = None,
    ) -> None:
        self.settings = settings
        if clients is None:
            clients = {
                workspace.alias: SlackSessionClient(workspace) for workspace in settings.workspaces
            }
        self._clients = clients

    def list_workspaces(self) -> list[dict[str, str]]:
        """
        List configured workspaces and verify session tokens.

        Returns
        -------
        list of dict
            Workspace alias, host slug, team id and team name when available.

        Raises
        ------
        SlackApiError
            If a workspace token is invalid.
        """
        rows: list[dict[str, str]] = []
        for workspace in self.settings.workspaces:
            client = self._get_client(workspace.alias)
            auth = client.call_api("auth.test")
            rows.append(
                {
                    "alias": workspace.alias,
                    "host": workspace.host_slug,
                    "team_id": str(auth.get("team_id", "")) or workspace.team_id,
                    "team": str(auth.get("team", "")),
                    "user": str(auth.get("user", "")),
                }
            )
        return rows

    def list_channels(
        self,
        workspace: str,
        include_private: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, str | bool]]:
        """
        List channels visible to the session user.

        Parameters
        ----------
        workspace
            Configured workspace alias.
        include_private
            Include private channels when true.
        limit
            Maximum number of channels to return.

        Returns
        -------
        list of dict
            Channel id, name, privacy flag and member flag.

        Raises
        ------
        WorkspaceNotFoundError
            If the alias is unknown.
        SlackApiError
            If the Slack API call fails.
        ValueError
            If ``limit`` is invalid.
        """
        capped = clamp_limit(limit)
        client = self._get_client(workspace)
        types = ["public_channel"]
        if include_private:
            types.append("private_channel")
        channels = self._paginate(
            client,
            "conversations.list",
            {"types": ",".join(types), "exclude_archived": "true", "limit": "200"},
            "channels",
        )
        member_channels = [channel for channel in channels if channel.get("is_member")]
        rows: list[dict[str, str | bool]] = []
        for channel in member_channels[:capped]:
            rows.append(
                {
                    "id": str(channel.get("id", "")),
                    "name": str(channel.get("name", "")),
                    "is_private": bool(channel.get("is_private")),
                    "is_member": bool(channel.get("is_member")),
                }
            )
        return rows

    def read_channel(
        self,
        workspace: str,
        channel: str,
        limit: int | None = None,
        oldest: str = "",
        latest: str = "",
    ) -> list[dict[str, str | int | bool]]:
        """
        Read recent messages from a channel.

        Parameters
        ----------
        workspace
            Configured workspace alias.
        channel
            Channel name (``#foo`` or ``foo``) or channel ID.
        limit
            Maximum number of messages.
        oldest
            Optional oldest timestamp (Slack ``ts`` format).
        latest
            Optional latest timestamp (Slack ``ts`` format).

        Returns
        -------
        list of dict
            Simplified messages, newest first.

        Raises
        ------
        WorkspaceNotFoundError
            If the alias is unknown.
        ChannelNotFoundError
            If the channel cannot be resolved.
        SlackApiError
            If the Slack API call fails.
        ValueError
            If ``limit`` is invalid.
        """
        capped = clamp_limit(limit)
        client = self._get_client(workspace)
        channel_id = self._resolve_channel_id(client, channel)
        params: dict[str, str | int | bool] = {
            "channel": channel_id,
            "limit": capped,
        }
        if oldest.strip():
            params["oldest"] = oldest.strip()
        if latest.strip():
            params["latest"] = latest.strip()
        response = client.call_api("conversations.history", params)
        messages = response.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        simplified = [
            simplify_message(message) for message in messages if isinstance(message, dict)
        ]
        return simplified

    def search_messages(
        self,
        workspace: str,
        query: str,
        limit: int | None = None,
    ) -> list[dict[str, str | int | bool]]:
        """
        Search messages with Slack search syntax.

        Parameters
        ----------
        workspace
            Configured workspace alias.
        query
            Slack search query, for example ``in:general deadline``.
        limit
            Maximum number of matches.

        Returns
        -------
        list of dict
            Simplified messages with channel metadata when available.

        Raises
        ------
        WorkspaceNotFoundError
            If the alias is unknown.
        SlackApiError
            If the Slack API call fails.
        ValueError
            If ``limit`` or ``query`` is invalid.
        """
        capped = clamp_limit(limit)
        search_query = query.strip()
        if not search_query:
            raise ValueError("query is required.")
        client = self._get_client(workspace)
        response = client.call_api(
            "search.messages",
            {"query": search_query, "count": capped, "sort": "timestamp", "sort_dir": "desc"},
        )
        matches = response.get("messages", {}).get("matches", [])
        if not isinstance(matches, list):
            return []
        rows: list[dict[str, str | int | bool]] = []
        for match in matches[:capped]:
            if not isinstance(match, dict):
                continue
            row = simplify_message(match)
            channel = match.get("channel", {})
            if isinstance(channel, dict):
                row["channel_id"] = str(channel.get("id", ""))
                row["channel_name"] = str(channel.get("name", ""))
            rows.append(row)
        return rows

    def read_thread(
        self,
        workspace: str,
        channel: str,
        thread_ts: str,
        limit: int | None = None,
    ) -> list[dict[str, str | int | bool]]:
        """
        Read all messages in a thread.

        Parameters
        ----------
        workspace
            Configured workspace alias.
        channel
            Channel name or ID that contains the thread.
        thread_ts
            Parent message timestamp.
        limit
            Maximum number of thread messages.

        Returns
        -------
        list of dict
            Simplified thread messages in chronological order.

        Raises
        ------
        WorkspaceNotFoundError
            If the alias is unknown.
        ChannelNotFoundError
            If the channel cannot be resolved.
        SlackApiError
            If the Slack API call fails.
        ValueError
            If ``limit`` or ``thread_ts`` is invalid.
        """
        capped = clamp_limit(limit)
        parent_ts = thread_ts.strip()
        if not parent_ts:
            raise ValueError("thread_ts is required.")
        client = self._get_client(workspace)
        channel_id = self._resolve_channel_id(client, channel)
        response = client.call_api(
            "conversations.replies",
            {"channel": channel_id, "ts": parent_ts, "limit": capped},
        )
        messages = response.get("messages", [])
        if not isinstance(messages, list):
            return []
        return [simplify_message(message) for message in messages if isinstance(message, dict)][
            :capped
        ]

    def _get_client(self, workspace_alias: str) -> SlackSessionClient:
        alias = workspace_alias.strip()
        client = self._clients.get(alias)
        if client is None:
            raise WorkspaceNotFoundError(
                f"Unknown workspace {alias!r}. Configured: {', '.join(self._clients)}."
            )
        return client

    def _resolve_channel_id(self, client: SlackSessionClient, channel: str) -> str:
        normalized = normalize_channel_name(channel)
        if not normalized:
            raise ChannelNotFoundError("channel is required.")
        if is_channel_id(normalized):
            return normalized
        channels = self._paginate(
            client,
            "conversations.list",
            {
                "types": "public_channel,private_channel",
                "exclude_archived": "true",
                "limit": "200",
            },
            "channels",
        )
        for item in channels:
            if not isinstance(item, dict):
                continue
            if str(item.get("name", "")) == normalized and item.get("is_member"):
                return str(item.get("id", ""))
        raise ChannelNotFoundError(f"Channel {normalized!r} not found or not a member.")

    def _paginate(
        self,
        client: SlackSessionClient,
        method: str,
        params: dict[str, str],
        collection_key: str,
    ) -> list[dict]:
        rows: list[dict] = []
        cursor = ""
        while True:
            page_params = dict(params)
            if cursor:
                page_params["cursor"] = cursor
            response = client.call_api(method, page_params)
            chunk = response.get(collection_key, [])
            if isinstance(chunk, list):
                rows.extend(item for item in chunk if isinstance(item, dict))
            metadata = response.get("response_metadata", {})
            if not isinstance(metadata, dict):
                break
            cursor = str(metadata.get("next_cursor", ""))
            if not cursor:
                break
        return rows
