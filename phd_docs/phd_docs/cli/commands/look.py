"""Look command for ``phd-docs look``."""

from __future__ import annotations

import argparse
import json

from claudia_docs.extractors.external.schema import load_docs_config_with_local
from rich.console import Console

from phd_docs.cli.commands.base import Command
from phd_docs.config import docs_config_path


class LookCommand(Command):
    """Show configured documentation sources."""

    def run(self, args: argparse.Namespace) -> int:
        """
        Print configured extractors without indexing.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed CLI arguments.

        Returns
        -------
        int
            Process exit code.
        """
        config_path = docs_config_path()
        entries = load_docs_config_with_local(config_path)
        if args.json:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
            return 0

        console = Console()
        console.print(f"[bold]Config:[/bold] {config_path}")
        for index, entry in enumerate(entries, start=1):
            provider = entry.get("provider", "?")
            console.print(f"{index}. {provider} -> {entry}")
        return 0
