"""``phd-docs`` command-line interface."""

from __future__ import annotations

import argparse
import logging
import sys

from claudia_docs.config import DEFAULT_QUERY_RESULTS

from phd_docs.cli.commands.look import LookCommand
from phd_docs.cli.commands.query import QueryCommand
from phd_docs.cli.commands.sync import SyncCommand
from phd_docs.config import build_settings, configure_embedding_runtime


def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser with ``sync``, ``query``, and ``look`` subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="phd-docs",
        description="Index and search PhD notes, specs, and Zotero PDFs.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Sync the documentation index")
    sync_parser.add_argument(
        "--full",
        action="store_true",
        help="Rebuild the index from scratch",
    )

    look_parser = subparsers.add_parser("look", help="Show configured sources")
    look_parser.add_argument("--json", action="store_true", help="Print JSON output")

    query_parser = subparsers.add_parser("query", help="Search the documentation index")
    query_parser.add_argument("text", help="Natural-language query")
    query_parser.add_argument(
        "-n",
        type=int,
        default=DEFAULT_QUERY_RESULTS,
        help=f"Number of results (default: {DEFAULT_QUERY_RESULTS})",
    )
    query_parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def main(argv: list[str] | None = None) -> None:
    """
    CLI entry point.

    Parameters
    ----------
    argv : list[str], optional
        Argument list. Defaults to ``sys.argv``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    device = configure_embedding_runtime()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    if args.verbose:
        logging.getLogger(__name__).info("Embedding device: %s", device)

    settings = build_settings()
    commands = {
        "sync": SyncCommand,
        "query": QueryCommand,
        "look": LookCommand,
    }
    command_class = commands[args.command]
    exit_code = command_class(settings=settings).run(args)
    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
