"""Command-line entry point for Slack session tools."""

import argparse
import json
import sys

from slack_session_mcp.auth_browser import extract_credentials_with_playwright
from slack_session_mcp.auth_capture import (
    AuthExtractError,
    CapturedCredentials,
    merge_workspace_entry,
)
from slack_session_mcp.server import mcp

MCP_COMMAND = "mcp"
AUTH_COMMAND = "auth"
EXTRACT_COMMAND = "extract"
PROG_NAME = "slack-session-tools"


def build_parser() -> argparse.ArgumentParser:
    """
    Build the ``slack-session-tools`` argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser with MCP and auth subcommands.
    """
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="Read-only Slack session tools for Cursor.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(MCP_COMMAND, help="Run the MCP server on stdio.")

    auth_parser = subparsers.add_parser(
        AUTH_COMMAND,
        help="Capture browser session credentials for mcp.json.",
    )
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)
    extract_parser = auth_subparsers.add_parser(
        EXTRACT_COMMAND,
        help="Open Slack in Chromium and capture xoxc/xoxd credentials.",
    )
    extract_parser.add_argument(
        "--alias",
        required=True,
        help="Workspace alias for SLACK_WORKSPACES, for example euclid or desi.",
    )
    extract_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Seconds to wait for login before failing.",
    )
    extract_parser.add_argument(
        "--merge",
        default="",
        help="Existing SLACK_WORKSPACES value to upsert by alias.",
    )
    extract_parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of human-readable output.",
    )
    extract_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chromium headless. Only use if the profile is already logged in.",
    )
    return parser


def print_extract_result(
    credentials: CapturedCredentials,
    merge_value: str,
    as_json: bool,
) -> None:
    """
    Print captured credentials for pasting into ``mcp.json``.

    Parameters
    ----------
    credentials
        Captured Slack session values.
    merge_value
        Optional existing ``SLACK_WORKSPACES`` string to merge into.
    as_json
        When true, print JSON instead of text instructions.
    """
    entry = credentials.to_entry()
    merged = merge_workspace_entry(merge_value, entry) if merge_value else entry
    if as_json:
        payload = {
            "entry": entry,
            "slack_workspaces": merged,
            "alias": credentials.alias,
            "team_id": credentials.team_id,
        }
        print(json.dumps(payload, indent=2))
        return
    print(f"Captured workspace entry for {credentials.alias!r}:")
    print(entry)
    print()
    print("Paste into ~/.cursor/mcp.json → slack-session → env → SLACK_WORKSPACES:")
    print(merged)


def main(argv: list[str] | None = None) -> None:
    """
    Parse CLI arguments and run the selected command.

    Parameters
    ----------
    argv
        Argument list without the program name. Defaults to ``sys.argv[1:]``.
    """
    args = build_parser().parse_args(argv)
    if args.command == MCP_COMMAND:
        mcp.run()
        return
    if args.command == AUTH_COMMAND and args.auth_command == EXTRACT_COMMAND:
        try:
            credentials = extract_credentials_with_playwright(
                alias=args.alias,
                timeout_seconds=args.timeout,
                headed=not args.headless,
            )
        except AuthExtractError as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print_extract_result(credentials, args.merge, args.json)
        return
    raise SystemExit(f"Unknown command: {args.command}")
