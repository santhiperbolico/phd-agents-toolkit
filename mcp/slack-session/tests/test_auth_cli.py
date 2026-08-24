"""Tests for auth extraction CLI."""

from slack_session_mcp.auth_capture import CapturedCredentials
from slack_session_mcp.cli import build_parser, print_extract_result


def test_build_parser_registers_auth_extract() -> None:
    args = build_parser().parse_args(["auth", "extract", "--alias", "euclid"])
    assert args.command == "auth"
    assert args.auth_command == "extract"
    assert args.alias == "euclid"


def test_print_extract_result_json(capsys) -> None:
    credentials = CapturedCredentials(
        alias="euclid",
        team_id="T111",
        token="xoxc-aaa",
        session_cookie="xoxd-bbb",
    )
    print_extract_result(credentials, merge_value="", as_json=True)
    output = capsys.readouterr().out
    assert '"team_id": "T111"' in output
    assert "xoxc-aaa" in output
