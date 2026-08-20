"""Domain errors for the Overleaf MCP server."""


class OverleafMcpError(Exception):
    """Base error for Overleaf MCP operations."""


class ConfigError(OverleafMcpError):
    """Raised when environment configuration is missing or invalid."""


class GitCommandError(OverleafMcpError):
    """Raised when a git command fails."""


class UnsafePathError(OverleafMcpError):
    """Raised when a file path would escape the project clone."""


class ProjectFileNotFoundError(OverleafMcpError):
    """Raised when a project file does not exist."""


class UnknownProjectError(OverleafMcpError):
    """Raised when the requested project alias is not configured."""
