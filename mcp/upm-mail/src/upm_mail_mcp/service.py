"""Mailbox operations used by the UPM mail MCP tools."""

from upm_mail_mcp.config import Settings
from upm_mail_mcp.errors import MailError
from upm_mail_mcp.mailbox import ImapSmtpMailbox
from upm_mail_mcp.parsing import (
    DEFAULT_FOLDER,
    build_search_criteria,
    clamp_limit,
    parse_recipients,
)


class UpMailService:
    """High-level list, read and send operations on a UPM mailbox."""

    def __init__(
        self,
        settings: Settings,
        mailbox: ImapSmtpMailbox | None = None,
    ) -> None:
        self.settings = settings
        self._mailbox = mailbox or ImapSmtpMailbox(settings)

    def list_folders(self) -> list[str]:
        """
        List selectable IMAP folders.

        Returns
        -------
        list of str
            Folder names reported by the server.
        """
        return self._mailbox.list_folders()

    def list_messages(
        self,
        folder: str = DEFAULT_FOLDER,
        limit: int | None = None,
        unread_only: bool = False,
        from_address: str = "",
        subject: str = "",
        text: str = "",
    ) -> list[dict[str, str | bool]]:
        """
        List recent messages in a folder, optionally filtered.

        Parameters
        ----------
        folder
            IMAP folder. Defaults to ``INBOX``.
        limit
            Maximum number of messages (newest first). Capped at 50.
        unread_only
            If true, only unseen messages.
        from_address
            Optional From filter.
        subject
            Optional Subject filter.
        text
            Optional full-text filter.

        Returns
        -------
        list of dict
            Header summaries.

        Raises
        ------
        MailError
            If ``limit`` is invalid.
        """
        folder_name = folder.strip() or DEFAULT_FOLDER
        try:
            capped = clamp_limit(limit)
        except ValueError as exc:
            raise MailError(str(exc)) from exc
        criteria = build_search_criteria(
            from_address=from_address,
            subject=subject,
            text=text,
            unread_only=unread_only,
        )
        uids = self._mailbox.search(folder_name, criteria)
        newest = list(reversed(uids[-capped:]))
        return self._mailbox.fetch_summaries(folder_name, newest)

    def get_message(
        self,
        uid: str,
        folder: str = DEFAULT_FOLDER,
    ) -> dict[str, str | bool | list[str]]:
        """
        Read one message by IMAP UID.

        Parameters
        ----------
        uid
            IMAP UID.
        folder
            IMAP folder. Defaults to ``INBOX``.

        Returns
        -------
        dict
            Headers, truncated body and attachment names.

        Raises
        ------
        MailError
            If ``uid`` is empty.
        """
        identifier = uid.strip()
        if not identifier:
            raise MailError("uid is required.")
        folder_name = folder.strip() or DEFAULT_FOLDER
        return self._mailbox.fetch_message(folder_name, identifier)

    def send_message(self, to: str, subject: str, body: str, cc: str = "") -> str:
        """
        Send a plain-text message from the configured UPM address.

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

        Returns
        -------
        str
            Confirmation mentioning the primary recipients.

        Raises
        ------
        MailError
            If recipients, subject or body are invalid.
        """
        try:
            recipients = parse_recipients(to)
            copies = parse_recipients(cc) if cc.strip() else []
        except ValueError as exc:
            raise MailError(str(exc)) from exc
        if not subject.strip():
            raise MailError("subject is required.")
        if not body.strip():
            raise MailError("body is required.")
        self._mailbox.send(recipients, subject.strip(), body, copies)
        return f"Sent to {', '.join(recipients)}."
