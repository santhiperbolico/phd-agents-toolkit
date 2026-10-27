"""CLI command base class."""

import argparse
from abc import ABC, abstractmethod

from claudia_docs.config import Settings


class Command(ABC):
    """Base class for ``phd-docs`` subcommands."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    def run(self, args: argparse.Namespace) -> int:
        """Execute the command and return a process exit code."""
