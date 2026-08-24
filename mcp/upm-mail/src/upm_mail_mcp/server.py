"""FastMCP server exposing UPM IMAP/SMTP tools."""

from fastmcp import FastMCP

from upm_mail_mcp.config import load_settings
from upm_mail_mcp.parsing import DEFAULT_FOLDER, DEFAULT_LIMIT
from upm_mail_mcp.service import UpMailService

mcp = FastMCP(name="upm-mail")


def get_service() -> UpMailService:
    """Build a service from the current process environment."""
    return UpMailService(load_settings())


@mcp.tool()
def list_folders() -> list[str]:
    """List IMAP folders in the configured UPM mailbox."""
    return get_service().list_folders()


@mcp.tool()
def list_messages(
    folder: str = DEFAULT_FOLDER,
    limit: int = DEFAULT_LIMIT,
    unread_only: bool = False,
    from_address: str = "",
    subject: str = "",
    text: str = "",
) -> list[dict[str, str | bool]]:
    """
    List recent messages in a folder (newest first).

    Parameters
    ----------
    folder
        IMAP folder, for example ``INBOX``.
    limit
        Maximum number of messages (1-50).
    unread_only
        If true, only unseen messages.
    from_address
        Optional From filter.
    subject
        Optional Subject filter.
    text
        Optional body/text filter.
    """
    return get_service().list_messages(
        folder=folder,
        limit=limit,
        unread_only=unread_only,
        from_address=from_address,
        subject=subject,
        text=text,
    )


@mcp.tool()
def get_message(uid: str, folder: str = DEFAULT_FOLDER) -> dict[str, str | bool | list[str]]:
    """
    Read one message by IMAP UID.

    Parameters
    ----------
    uid
        IMAP UID from ``list_messages``.
    folder
        IMAP folder that contains the message.
    """
    return get_service().get_message(uid, folder)


@mcp.tool()
def send_message(to: str, subject: str, body: str, cc: str = "") -> str:
    """
    Send a plain-text email from the configured UPM address.

    Parameters
    ----------
    to
        Comma-separated recipients.
    subject
        Message subject.
    body
        Plain-text body.
    cc
        Optional comma-separated carbon copies.
    """
    return get_service().send_message(to, subject, body, cc)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()
