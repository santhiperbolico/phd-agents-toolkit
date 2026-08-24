"""Parse RFC822 headers and extract a readable text body."""

import re
from email.header import decode_header, make_header
from email.message import EmailMessage, Message
from email.parser import BytesParser
from email.policy import default as email_policy

DEFAULT_FOLDER = "INBOX"
DEFAULT_LIMIT = 20
MAX_LIMIT = 50
MAX_BODY_CHARS = 20_000


def decode_header_value(raw: str | None) -> str:
    """
    Decode a possibly encoded RFC2047 header to a Unicode string.

    Parameters
    ----------
    raw
        Header value, or ``None``.

    Returns
    -------
    str
        Decoded text, or an empty string.
    """
    if not raw:
        return ""
    return str(make_header(decode_header(raw)))


def clamp_limit(limit: int | None) -> int:
    """
    Clamp a listing limit to the allowed range.

    Parameters
    ----------
    limit
        Requested number of messages. ``None`` uses the default.

    Returns
    -------
    int
        Value between 1 and ``MAX_LIMIT``.

    Raises
    ------
    ValueError
        If ``limit`` is less than 1.
    """
    if limit is None:
        return DEFAULT_LIMIT
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    return min(limit, MAX_LIMIT)


def parse_recipients(raw: str) -> list[str]:
    """
    Split a comma-separated recipient list.

    Parameters
    ----------
    raw
        One or more addresses separated by commas.

    Returns
    -------
    list of str
        Trimmed addresses.

    Raises
    ------
    ValueError
        If the list is empty or an address has no ``@``.
    """
    parts = [item.strip() for item in raw.split(",") if item.strip()]
    if not parts:
        raise ValueError("At least one recipient is required.")
    for item in parts:
        if "@" not in item:
            raise ValueError(f"Invalid recipient: {item}")
    return parts


def quote_imap_string(value: str) -> str:
    """
    Quote a value for an IMAP SEARCH criterion.

    Parameters
    ----------
    value
        Raw search token.

    Returns
    -------
    str
        Double-quoted IMAP string.
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_search_criteria(
    from_address: str = "",
    subject: str = "",
    text: str = "",
    unread_only: bool = False,
) -> list[str]:
    """
    Build IMAP SEARCH tokens from optional filters.

    Parameters
    ----------
    from_address
        Match the From header.
    subject
        Match the Subject header.
    text
        Match message text.
    unread_only
        Restrict to unseen messages.

    Returns
    -------
    list of str
        IMAP criteria, or ``ALL`` when no filter is set.
    """
    criteria: list[str] = []
    if unread_only:
        criteria.append("UNSEEN")
    if from_address.strip():
        criteria.extend(["FROM", quote_imap_string(from_address.strip())])
    if subject.strip():
        criteria.extend(["SUBJECT", quote_imap_string(subject.strip())])
    if text.strip():
        criteria.extend(["TEXT", quote_imap_string(text.strip())])
    if not criteria:
        return ["ALL"]
    return criteria


def parse_imap_list_name(line: bytes) -> str | None:
    """
    Extract a selectable mailbox name from an IMAP LIST line.

    Parameters
    ----------
    line
        Raw LIST response line.

    Returns
    -------
    str or None
        Folder name, or ``None`` for ``\\Noselect`` entries.
    """
    text = line.decode("utf-8", "replace").strip()
    if not text:
        return None
    if "\\noselect" in text.lower():
        return None
    match = re.search(r'\)\s+"[^"]*"\s+(.*)$', text)
    if match is None:
        tokens = text.split()
        return tokens[-1] if tokens else None
    rest = match.group(1).strip()
    if len(rest) >= 2 and rest.startswith('"'):
        closing = rest.rfind('"')
        if closing > 0:
            return rest[1:closing]
    return rest.split()[0] if rest else None


def message_from_bytes(raw: bytes) -> EmailMessage:
    """
    Parse RFC822 bytes into an ``EmailMessage``.

    Parameters
    ----------
    raw
        Raw message or header bytes.

    Returns
    -------
    EmailMessage
        Parsed message.
    """
    parsed = BytesParser(policy=email_policy).parsebytes(raw)
    if isinstance(parsed, EmailMessage):
        return parsed
    rebuilt = EmailMessage()
    rebuilt.set_payload(parsed.get_payload())
    for key, value in parsed.items():
        rebuilt[key] = value
    return rebuilt


def extract_text_body(message: Message, max_chars: int = MAX_BODY_CHARS) -> tuple[str, bool]:
    """
    Prefer ``text/plain``, then ``text/html``, and truncate if needed.

    Parameters
    ----------
    message
        Parsed email message.
    max_chars
        Maximum number of characters to return.

    Returns
    -------
    tuple of str and bool
        Body text and whether it was truncated.
    """
    if isinstance(message, EmailMessage):
        body_part = message.get_body(preferencelist=("plain", "html"))
        payload = body_part.get_content() if body_part is not None else ""
    else:
        payload = _legacy_payload_text(message)
    if not isinstance(payload, str):
        payload = str(payload)
    truncated = len(payload) > max_chars
    if truncated:
        payload = payload[:max_chars]
    return payload, truncated


def attachment_names(message: EmailMessage) -> list[str]:
    """
    Return attachment filenames without downloading payloads.

    Parameters
    ----------
    message
        Parsed email message.

    Returns
    -------
    list of str
        Filenames, using ``unnamed`` when the header is missing.
    """
    names = []
    for part in message.iter_attachments():
        names.append(part.get_filename() or "unnamed")
    return names


def summary_from_message(
    uid: str,
    folder: str,
    flags: str,
    message: Message,
) -> dict[str, str | bool]:
    """
    Build a header-only summary dictionary.

    Parameters
    ----------
    uid
        IMAP UID.
    folder
        Folder name.
    flags
        IMAP FLAGS string.
    message
        Parsed headers.

    Returns
    -------
    dict
        Summary fields for MCP tools.
    """
    return {
        "uid": uid,
        "folder": folder,
        "from": decode_header_value(message.get("From")),
        "to": decode_header_value(message.get("To")),
        "cc": decode_header_value(message.get("Cc")),
        "subject": decode_header_value(message.get("Subject")),
        "date": decode_header_value(message.get("Date")),
        "unseen": "\\Seen" not in flags,
    }


def detail_from_message(
    uid: str,
    folder: str,
    flags: str,
    message: EmailMessage,
) -> dict[str, str | bool | list[str]]:
    """
    Build a message dictionary including a truncated body.

    Parameters
    ----------
    uid
        IMAP UID.
    folder
        Folder name.
    flags
        IMAP FLAGS string.
    message
        Parsed full message.

    Returns
    -------
    dict
        Detail fields for MCP tools.
    """
    body, truncated = extract_text_body(message)
    summary = summary_from_message(uid, folder, flags, message)
    detail: dict[str, str | bool | list[str]] = dict(summary)
    detail["body"] = body
    detail["truncated"] = truncated
    detail["attachments"] = attachment_names(message)
    return detail


def _legacy_payload_text(message: Message) -> str:
    """Return a decoded payload for non-EmailMessage objects."""
    payload = message.get_payload(decode=True)
    if isinstance(payload, bytes):
        charset = message.get_content_charset() or "utf-8"
        return payload.decode(charset, "replace")
    if isinstance(payload, str):
        return payload
    return ""
