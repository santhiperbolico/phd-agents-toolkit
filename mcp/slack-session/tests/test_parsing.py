"""Tests for parsing helpers."""

import pytest

from slack_session_mcp.parsing import (
    MAX_TEXT_LENGTH,
    clamp_limit,
    is_channel_id,
    normalize_channel_name,
    simplify_message,
    truncate_text,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, 20),
        (5, 5),
        (100, 50),
    ],
)
def test_clamp_limit(value: int | None, expected: int) -> None:
    assert clamp_limit(value) == expected


def test_clamp_limit_rejects_zero() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        clamp_limit(0)


@pytest.mark.parametrize(
    "channel, expected",
    [
        ("#general", "general"),
        (" C123 ", "C123"),
    ],
)
def test_normalize_channel_name(channel: str, expected: str) -> None:
    assert normalize_channel_name(channel) == expected


@pytest.mark.parametrize(
    "channel, expected",
    [
        ("C0123", True),
        ("G0123", True),
        ("general", False),
    ],
)
def test_is_channel_id(channel: str, expected: bool) -> None:
    assert is_channel_id(channel) is expected


def test_truncate_text_flags_long_messages() -> None:
    text = "x" * (MAX_TEXT_LENGTH + 1)
    truncated, was_truncated = truncate_text(text)
    assert was_truncated is True
    assert len(truncated) == MAX_TEXT_LENGTH


def test_simplify_message_keeps_thread_metadata() -> None:
    row = simplify_message(
        {
            "ts": "1.0",
            "thread_ts": "0.5",
            "user": "U1",
            "text": "hello",
            "reply_count": 3,
        }
    )
    assert row["thread_ts"] == "0.5"
    assert row["reply_count"] == 3
