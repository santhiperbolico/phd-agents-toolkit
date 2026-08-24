"""Domain errors for the UPM mail MCP server."""


class UpMailMcpError(Exception):
    """Base error for UPM mail MCP operations."""


class ConfigError(UpMailMcpError):
    """Raised when environment configuration is missing or invalid."""


class MailError(UpMailMcpError):
    """Raised when an IMAP or SMTP operation fails."""


class MailAuthError(MailError):
    """Raised when IMAP or SMTP authentication fails."""
