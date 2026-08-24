"""Tests for RFC822 parsing and IMAP helpers."""

from email.message import EmailMessage, Message

import pytest

from upm_mail_mcp.parsing import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    attachment_names,
    build_search_criteria,
    clamp_limit,
    decode_header_value,
    detail_from_message,
    extract_text_body,
    message_from_bytes,
    parse_imap_list_name,
    parse_recipients,
    quote_imap_string,
    summary_from_message,
)


def test_decode_header_value_handles_encoded_words() -> None:
    raw = "=?utf-8?q?Reuni=C3=B3n?="
    assert decode_header_value(raw) == "Reunión"
    assert decode_header_value(None) == ""
    assert decode_header_value("") == ""


@pytest.mark.parametrize(
    "limit, expected",
    [
        (None, DEFAULT_LIMIT),
        (1, 1),
        (100, MAX_LIMIT),
    ],
)
def test_clamp_limit(limit: int | None, expected: int) -> None:
    assert clamp_limit(limit) == expected


def test_clamp_limit_rejects_zero() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        clamp_limit(0)


def test_parse_recipients() -> None:
    assert parse_recipients(" a@upm.es , b@upm.es ") == ["a@upm.es", "b@upm.es"]


@pytest.mark.parametrize("raw", ["", "   ", "nonesuch"])
def test_parse_recipients_rejects_invalid(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_recipients(raw)


def test_quote_imap_string_escapes_quotes() -> None:
    assert quote_imap_string('say "hi"') == r'"say \"hi\""'


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, ["ALL"]),
        ({"unread_only": True}, ["UNSEEN"]),
        (
            {"from_address": "ada@upm.es", "subject": "Hi", "text": "agenda"},
            [
                "FROM",
                '"ada@upm.es"',
                "SUBJECT",
                '"Hi"',
                "TEXT",
                '"agenda"',
            ],
        ),
    ],
)
def test_build_search_criteria(kwargs: dict, expected: list[str]) -> None:
    assert build_search_criteria(**kwargs) == expected


@pytest.mark.parametrize(
    "line, expected",
    [
        (b'(\\HasNoChildren) "/" INBOX', "INBOX"),
        (b'(\\HasNoChildren) "/" "Sent Items"', "Sent Items"),
        (b'(\\Noselect) "/" "."', None),
        (b"", None),
    ],
)
def test_parse_imap_list_name(line: bytes, expected: str | None) -> None:
    assert parse_imap_list_name(line) == expected


def test_message_summary_and_detail() -> None:
    raw = (
        b"From: Ada <ada@upm.es>\r\n"
        b"To: alumno@alumnos.upm.es\r\n"
        b"Subject: Hello\r\n"
        b"Date: Mon, 24 Aug 2026 10:00:00 +0200\r\n"
        b"\r\n"
        b"Plain body\r\n"
    )
    message = message_from_bytes(raw)
    summary = summary_from_message("12", "INBOX", r"\Seen", message)
    assert summary["from"] == "Ada <ada@upm.es>"
    assert summary["unseen"] is False
    detail = detail_from_message("12", "INBOX", "", message)
    assert detail["unseen"] is True
    assert "Plain body" in str(detail["body"])
    assert detail["truncated"] is False
    assert detail["attachments"] == []


def test_extract_html_body_and_truncation() -> None:
    message = EmailMessage()
    message["Subject"] = "x"
    message.set_content("<p>Hi</p>", subtype="html")
    body, truncated = extract_text_body(message)
    assert "Hi" in body
    assert truncated is False
    short, was_cut = extract_text_body(message, max_chars=2)
    assert len(short) == 2
    assert was_cut is True


def test_legacy_payload_and_attachments() -> None:
    legacy = Message()
    legacy.set_payload("hello".encode(), charset="utf-8")
    assert extract_text_body(legacy)[0] == "hello"

    message = EmailMessage()
    message["Subject"] = "files"
    message.set_content("cover")
    message.add_attachment(
        b"data",
        maintype="application",
        subtype="pdf",
        filename="a.pdf",
    )
    message.add_attachment(b"x", maintype="application", subtype="octet-stream")
    names = attachment_names(message)
    assert "a.pdf" in names
    assert "unnamed" in names
