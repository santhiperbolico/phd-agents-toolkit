"""Parsing helpers for Slack session MCP tools."""

DEFAULT_LIMIT = 20
MAX_LIMIT = 50
MAX_TEXT_LENGTH = 20_000

CHANNEL_ID_PREFIX = "C"
PRIVATE_CHANNEL_ID_PREFIX = "G"


def clamp_limit(limit: int | None) -> int:
    """
    Clamp a message or channel limit to the allowed range.

    Parameters
    ----------
    limit
        Requested limit. Defaults to ``DEFAULT_LIMIT`` when ``None``.

    Returns
    -------
    int
        Value between 1 and ``MAX_LIMIT``.

    Raises
    ------
    ValueError
        If ``limit`` is less than 1.
    """
    value = DEFAULT_LIMIT if limit is None else limit
    if value < 1:
        raise ValueError("limit must be at least 1.")
    return min(value, MAX_LIMIT)


def normalize_channel_name(channel: str) -> str:
    """
    Strip leading ``#`` and whitespace from a channel name.

    Parameters
    ----------
    channel
        Channel name or ID.

    Returns
    -------
    str
        Normalized channel identifier.
    """
    return channel.strip().lstrip("#")


def is_channel_id(channel: str) -> bool:
    """
    Return whether the value looks like a Slack channel ID.

    Parameters
    ----------
    channel
        Channel name or ID.

    Returns
    -------
    bool
        True when the value starts with ``C`` or ``G``.
    """
    normalized = normalize_channel_name(channel)
    return normalized.startswith(CHANNEL_ID_PREFIX) or normalized.startswith(
        PRIVATE_CHANNEL_ID_PREFIX
    )


def truncate_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> tuple[str, bool]:
    """
    Truncate long message text for MCP responses.

    Parameters
    ----------
    text
        Raw message text.
    max_length
        Maximum number of characters to keep.

    Returns
    -------
    tuple of (str, bool)
        Truncated text and whether truncation happened.
    """
    if len(text) <= max_length:
        return text, False
    return text[:max_length], True


def simplify_message(message: dict) -> dict[str, str | int | bool]:
    """
    Reduce a Slack message payload for agent consumption.

    Parameters
    ----------
    message
        Raw Slack message dictionary.

    Returns
    -------
    dict
        Compact message fields.
    """
    text, truncated = truncate_text(str(message.get("text", "")))
    thread_ts = message.get("thread_ts")
    payload: dict[str, str | int | bool] = {
        "ts": str(message.get("ts", "")),
        "user": str(message.get("user", "")),
        "text": text,
        "truncated": truncated,
    }
    if thread_ts:
        payload["thread_ts"] = str(thread_ts)
    reply_count = message.get("reply_count")
    if isinstance(reply_count, int):
        payload["reply_count"] = reply_count
    return payload
