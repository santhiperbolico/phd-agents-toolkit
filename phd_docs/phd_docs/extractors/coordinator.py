"""Coordinator for PhD documentation sources declared in ``phd_docs.json``."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from claudia_docs.config import Settings
from claudia_docs.domain.exceptions import ConfigError
from claudia_docs.domain.progress import SyncReporter
from claudia_docs.domain.results import RepoScanSummary
from claudia_docs.extractors.base import DocumentExtractor
from claudia_docs.extractors.external.providers.registry import ProviderRegistry
from claudia_docs.extractors.external.schema import load_docs_config_with_local
from claudia_docs.pipeline.sync_state import SyncState
from langchain_core.documents import Document

from phd_docs.config import docs_config_path, resolve_toolkit_root

logger = logging.getLogger(__name__)


@dataclass
class PhdDocsExtractor(DocumentExtractor):
    """Extract documents from ``docs/phd_docs.json`` in the toolkit root."""

    settings: Settings
    registry: type[ProviderRegistry] = ProviderRegistry
    _scan: RepoScanSummary | None = field(default=None, init=False, repr=False)

    def extract(
        self,
        *,
        reporter: SyncReporter | None = None,
        sync_state: SyncState | None = None,
    ) -> Iterable[Document]:
        """
        Yield documents from all configured providers.

        Parameters
        ----------
        reporter : SyncReporter, optional
            Progress reporter for CLI output.
        sync_state : SyncState, optional
            Incremental sync manifest.

        Yields
        ------
        Document
            Raw documents before chunking.
        """
        config_path = docs_config_path()
        repo_name = resolve_toolkit_root().name
        count = 0
        try:
            entries = load_docs_config_with_local(config_path)
        except ConfigError as exc:
            logger.error("%s", exc)
            self._scan = RepoScanSummary(
                repos_with_docs=[],
                repos_without_docs=[repo_name],
                repo_file_counts={},
            )
            return

        for entry in entries:
            yield from self._process_entry(
                entry,
                repo_name=repo_name,
                config_path=config_path,
                reporter=reporter,
                sync_state=sync_state,
            )
            count += 1

        self._scan = RepoScanSummary(
            repos_with_docs=[repo_name],
            repos_without_docs=[],
            repo_file_counts={repo_name: count},
        )

    def scan_summary(self) -> RepoScanSummary | None:
        """Return the summary produced by the last extract run."""
        return self._scan

    def _process_entry(
        self,
        entry: dict[str, object],
        *,
        repo_name: str,
        config_path: Path,
        reporter: SyncReporter | None,
        sync_state: SyncState | None,
    ) -> Iterable[Document]:
        provider_name = str(entry.get("provider", "")).strip()
        if not provider_name:
            logger.warning("Entry without provider in %s", config_path)
            return
        if not self.registry.is_registered(provider_name):
            logger.warning(
                "Unknown provider %r in %s (registered: %s)",
                provider_name,
                config_path,
                ", ".join(self.registry.known_providers()) or "<none>",
            )
            return

        provider = self.registry.create(provider_name)
        try:
            yield from provider.extract_entry(
                entry,
                repo_name=repo_name,
                config_path=config_path,
                reporter=reporter,
                sync_state=sync_state,
            )
        except Exception:
            logger.exception(
                "Failed loading provider %s (repo=%s, config=%s)",
                provider_name,
                repo_name,
                config_path,
            )
