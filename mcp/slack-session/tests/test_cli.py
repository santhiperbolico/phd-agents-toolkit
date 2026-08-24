"""Tests for the Slack session CLI."""

from slack_session_mcp.cli import MCP_COMMAND, PROG_NAME, build_parser


def test_build_parser_registers_mcp_command() -> None:
    parser = build_parser()
    args = parser.parse_args([MCP_COMMAND])
    assert args.command == MCP_COMMAND
    assert parser.prog == PROG_NAME
