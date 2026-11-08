"""Query command for ``phd-docs query``."""

from __future__ import annotations

import argparse
import json

from rich.console import Console

from phd_docs.cli.commands.base import Command
from phd_docs.container import build_query_service


class QueryCommand(Command):
    """Search the PhD documentation index."""

    def run(self, args: argparse.Namespace) -> int:
        """
        Execute a semantic query against the index.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed CLI arguments.

        Returns
        -------
        int
            Process exit code.
        """
        service = build_query_service(self.settings)
        matches = service.query(args.text, n_results=args.n)
        if args.json:
            payload = [match.to_dict() for match in matches]
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        console = Console()
        if not matches:
            console.print("[yellow]No matches found.[/yellow]")
            return 0

        for index, match in enumerate(matches, start=1):
            title = match.metadata.get("title") or match.path
            score = match.final_score if match.final_score is not None else match.similarity
            console.print(f"[bold cyan]{index}.[/bold cyan] {title} ({score:.3f})")
            console.print(match.document[:400])
            console.print("")
        return 0
