"""IMAP SSL and SMTP STARTTLS client for UPM mail."""

import imaplib
import re
import smtplib
from collections.abc import Callable, Sequence
from contextlib import suppress
from email.message import EmailMessage

from upm_mail_mcp.config import Settings
from upm_mail_mcp.errors import MailAuthError, MailError
from upm_mail_mcp.parsing import (
    DEFAULT_FOLDER,
    detail_from_message,
    message_from_bytes,
    parse_imap_list_name,
    summary_from_message,
)

ImapFactory = Callable[[str, int], imaplib.IMAP4_SSL]
SmtpFactory = Callable[[str, int], smtplib.SMTP]

UID_RE = re.compile(rb"UID\s+(\d+)")
FLAGS_RE = re.compile(rb"FLAGS\s+\(([^)]*)\)")
HEADER_FETCH = "(UID FLAGS RFC822.HEADER)"
FULL_FETCH = "(UID FLAGS RFC822)"


class ImapSmtpMailbox:
    """IMAP/SMTP mailbox bound to UPM settings."""

    def __init__(
        self,
        settings: Settings,
        imap_factory: ImapFactory | None = None,
        smtp_factory: SmtpFactory | None = None,
    ) -> None:
        self._settings = settings
        self._imap_factory = imap_factory or _default_imap
        self._smtp_factory = smtp_factory or _default_smtp

    def list_folders(self) -> list[str]:
        """
        List selectable IMAP folders.

        Returns
        -------
        list of str
            Folder names.

        Raises
        ------
        MailError
            If LIST fails.
        MailAuthError
            If login fails.
        """
        with self._imap_session() as client:
            status, lines = client.list()
            _require_ok(status, "IMAP LIST failed.")
            names = []
            for line in lines or []:
                if not isinstance(line, bytes):
                    continue
                name = parse_imap_list_name(line)
                if name:
                    names.append(name)
            return names

    def search(self, folder: str, criteria: Sequence[str]) -> list[str]:
        """
        Return matching UIDs in a folder (oldest first).

        Parameters
        ----------
        folder
            IMAP folder name.
        criteria
            IMAP SEARCH tokens.

        Returns
        -------
        list of str
            UIDs.

        Raises
        ------
        MailError
            If SELECT or SEARCH fails.
        """
        with self._imap_session() as client:
            _select_folder(client, folder)
            status, data = client.uid("SEARCH", None, *criteria)
            _require_ok(status, "IMAP SEARCH failed.")
            if not data or not data[0]:
                return []
            return data[0].decode("ascii", "replace").split()

    def fetch_summaries(self, folder: str, uids: Sequence[str]) -> list[dict[str, str | bool]]:
        """
        Fetch header summaries for the given UIDs.

        Parameters
        ----------
        folder
            IMAP folder name.
        uids
            Message UIDs.

        Returns
        -------
        list of dict
            Header summaries.
        """
        return self._fetch_parsed(folder, uids, HEADER_FETCH, as_detail=False)

    def fetch_message(self, folder: str, uid: str) -> dict[str, str | bool | list[str]]:
        """
        Fetch one full message by UID.

        Parameters
        ----------
        folder
            IMAP folder name.
        uid
            Message UID.

        Returns
        -------
        dict
            Headers, body and attachment names.

        Raises
        ------
        MailError
            If the UID is missing or FETCH fails.
        """
        items = self._fetch_parsed(folder, [uid], FULL_FETCH, as_detail=True)
        if not items:
            raise MailError(f"Message UID {uid} was not found in {folder}.")
        return items[0]

    def send(self, to: Sequence[str], subject: str, body: str, cc: Sequence[str]) -> None:
        """
        Send a plain-text message through UPM SMTP.

        Parameters
        ----------
        to
            Primary recipients.
        subject
            Message subject.
        body
            Plain-text body.
        cc
            Carbon-copy recipients.

        Raises
        ------
        MailAuthError
            If SMTP authentication fails.
        MailError
            If the message cannot be sent.
        """
        message = EmailMessage()
        message["From"] = self._settings.address
        message["To"] = ", ".join(to)
        if cc:
            message["Cc"] = ", ".join(cc)
        message["Subject"] = subject
        message.set_content(body)
        recipients = list(to) + list(cc)
        client = self._smtp_factory(self._settings.smtp_host, self._settings.smtp_port)
        try:
            client.starttls()
            client.login(self._settings.address, self._settings.password)
            client.send_message(message, to_addrs=recipients)
        except smtplib.SMTPAuthenticationError as exc:
            raise MailAuthError("SMTP authentication failed.") from exc
        except smtplib.SMTPException as exc:
            raise MailError("SMTP send failed.") from exc
        finally:
            with suppress(OSError, smtplib.SMTPException):
                client.quit()

    def _imap_session(self) -> "_ImapLogout":
        """Log in to IMAP SSL and log out when the block ends."""
        client = self._imap_factory(self._settings.imap_host, self._settings.imap_port)
        try:
            status, _ = client.login(
                self._settings.imap_username,
                self._settings.password,
            )
            _require_ok(status, "IMAP login failed.", auth=True)
        except (imaplib.IMAP4.error, MailAuthError) as exc:
            with suppress(OSError, imaplib.IMAP4.error):
                client.logout()
            if isinstance(exc, MailAuthError):
                raise
            raise MailAuthError("IMAP authentication failed.") from exc
        return _ImapLogout(client)

    def _fetch_parsed(
        self,
        folder: str,
        uids: Sequence[str],
        spec: str,
        as_detail: bool,
    ) -> list[dict]:
        """Fetch and parse RFC822 bytes for the given UIDs."""
        if not uids:
            return []
        uid_set = ",".join(uids)
        with self._imap_session() as client:
            _select_folder(client, folder)
            status, data = client.uid("FETCH", uid_set, spec)
            _require_ok(status, "IMAP FETCH failed.")
            parsed = []
            for uid, flags, raw in _iter_fetch_payloads(data or []):
                message = message_from_bytes(raw)
                if as_detail:
                    parsed.append(detail_from_message(uid, folder, flags, message))
                else:
                    parsed.append(summary_from_message(uid, folder, flags, message))
            return parsed


class _ImapLogout:
    """Context manager that logs out of an IMAP client."""

    def __init__(self, client: imaplib.IMAP4_SSL) -> None:
        self._client = client

    def __enter__(self) -> imaplib.IMAP4_SSL:
        return self._client

    def __exit__(self, exc_type, exc, traceback) -> None:
        with suppress(OSError, imaplib.IMAP4.error):
            self._client.logout()


def _default_imap(host: str, port: int) -> imaplib.IMAP4_SSL:
    """Open an IMAP SSL connection."""
    return imaplib.IMAP4_SSL(host, port, timeout=30)


def _default_smtp(host: str, port: int) -> smtplib.SMTP:
    """Open an SMTP connection."""
    return smtplib.SMTP(host, port, timeout=30)


def _select_folder(client: imaplib.IMAP4_SSL, folder: str) -> None:
    """Select an IMAP folder in read-only mode."""
    name = folder.strip() or DEFAULT_FOLDER
    status, _ = client.select(name, readonly=True)
    _require_ok(status, f"Cannot open folder {name}.")


def _require_ok(status: str | None, message: str, auth: bool = False) -> None:
    """Raise a mail error when the IMAP status is not OK."""
    if status == "OK":
        return
    if auth:
        raise MailAuthError(message)
    raise MailError(message)


def _iter_fetch_payloads(data: list) -> list[tuple[str, str, bytes]]:
    """
    Extract UID, flags and RFC822 bytes from an IMAP FETCH response.

    Parameters
    ----------
    data
        Raw ``uid('FETCH', ...)`` payload list.

    Returns
    -------
    list of tuple
        ``(uid, flags, raw_bytes)`` items.
    """
    items = []
    for entry in data:
        if not isinstance(entry, tuple) or len(entry) < 2:
            continue
        meta, payload = entry[0], entry[1]
        if not isinstance(meta, bytes) or not isinstance(payload, bytes):
            continue
        uid_match = UID_RE.search(meta)
        if uid_match is None:
            continue
        flags_match = FLAGS_RE.search(meta)
        flags = flags_match.group(1).decode("ascii", "replace") if flags_match else ""
        items.append((uid_match.group(1).decode("ascii"), flags, payload))
    return items
