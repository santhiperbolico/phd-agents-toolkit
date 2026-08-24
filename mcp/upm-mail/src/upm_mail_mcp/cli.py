"""Command-line entry point for UPM mail tools."""

import argparse

from upm_mail_mcp.server import mcp

MCP_COMMAND = "mcp"
PROG_NAME = "upm-mail-tools"


def build_parser() -> argparse.ArgumentParser:
    """
    Build the ``upm-mail-tools`` argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser with the ``mcp`` subcommand.
    """
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="UPM IMAP/SMTP tools for Cursor.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(MCP_COMMAND, help="Run the MCP server on stdio.")
    return parser


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
