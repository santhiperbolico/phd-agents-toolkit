"""Sync command for ``phd-docs sync``."""

from __future__ import annotations

import argparse

from rich.console import Console

from phd_docs.cli.commands.base import Command
from phd_docs.container import build_sync_pipeline


class SyncCommand(Command):
    """Re-index PhD notes, specs, and Zotero PDFs."""

    def run(self, args: argparse.Namespace) -> int:
        """
        Run the sync pipeline.

        Parameters
        ----------
        args : argparse.Namespace
            Parsed CLI arguments.

        Returns
        -------
        int
            Process exit code.
        """
        console = Console()
        console.print("[bold]Syncing PhD documentation index[/bold]")
        pipeline = build_sync_pipeline(self.settings)
        result = pipeline.run(full=bool(args.full))
        console.print(
            f"Done: {result.updated_files} updated, "
            f"{result.skipped_files} skipped, "
            f"{result.total_chunks} chunks indexed."
        )
        return 0
