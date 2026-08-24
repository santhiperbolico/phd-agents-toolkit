"""Domain errors for the Slack session MCP server."""


class SlackSessionMcpError(Exception):
    """Base error for Slack session MCP operations."""


class ConfigError(SlackSessionMcpError):
    """Raised when environment configuration is missing or invalid."""


class SlackApiError(SlackSessionMcpError):
    """Raised when the Slack Web API returns an error."""


class WorkspaceNotFoundError(SlackSessionMcpError):
    """Raised when a workspace alias is not configured."""


class ChannelNotFoundError(SlackSessionMcpError):
    """Raised when a channel name or ID cannot be resolved."""
