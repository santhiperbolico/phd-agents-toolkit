"""Domain errors for the Taurus MCP server."""


class TaurusMcpError(Exception):
    """Base error for Taurus MCP operations."""


class ConfigError(TaurusMcpError):
    """Raised when environment configuration is missing or invalid."""


class UnsafePathError(TaurusMcpError):
    """Raised when a remote path contains unsafe segments."""


class SshCommandError(TaurusMcpError):
    """Raised when a fixed SSH command fails."""


class ReadLimitError(TaurusMcpError):
    """Raised when a file exceeds the read size cap."""


class BinaryFileError(TaurusMcpError):
    """Raised when a file looks binary or non-text."""


class OutputLimitError(TaurusMcpError):
    """Raised when command output exceeds configured line limits."""
