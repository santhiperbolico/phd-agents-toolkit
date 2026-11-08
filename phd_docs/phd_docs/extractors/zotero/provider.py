"""Zotero library extraction provider."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from claudia_docs.domain.metadata import prepare_document_metadata
from claudia_docs.domain.progress import SyncReporter
from claudia_docs.extractors.external.providers.base import ProviderExtractor
from claudia_docs.extractors.external.providers.registry import register_provider
from claudia_docs.pipeline.sync_state import SyncState
from langchain_core.documents import Document

from phd_docs.extractors.zotero import pdf_text, sqlite_reader

logger = logging.getLogger(__name__)

DEFAULT_INCLUDE = frozenset({"metadata", "abstract", "pdf", "notes", "annotations"})
DEFAULT_DATA_DIR = Path.home() / "Zotero"


@register_provider
@dataclass
class ZoteroProviderExtractor(ProviderExtractor):
    """Extract bibliographic items and PDF text from the local Zotero library."""

    name: ClassVar[str] = "Zotero"
    default_include: frozenset[str] = field(default_factory=lambda: DEFAULT_INCLUDE)

    def extract_entry(
        self,
        entry: Mapping[str, Any],
        *,
        repo_name: str,
        config_path: Path,
        reporter: SyncReporter | None = None,
        sync_state: SyncState | None = None,
    ) -> Iterable[Document]:
        """
        Yield one document per PDF attachment in the Zotero library.

        Parameters
        ----------
        entry : Mapping[str, Any]
            Provider configuration from ``phd_docs.json``.
        repo_name : str
            Repository name used in metadata.
        config_path : Path
            Path to the JSON configuration file.
        reporter : SyncReporter, optional
            Progress reporter for CLI output.
        sync_state : SyncState, optional
            Incremental sync manifest.

        Yields
        ------
        Document
            Combined metadata, notes, annotations, and PDF text.
        """
        data_dir = self._resolve_data_dir(entry)
        db_path = data_dir / "zotero.sqlite"
        if not db_path.is_file():
            logger.warning("Zotero database not found at %s", db_path)
            return

        include_parts = self._resolve_include(entry)
        exclude_tags = self._resolve_exclude_tags(entry)
        linked_base = self._resolve_linked_base(entry)
        records = sqlite_reader.iter_pdf_records(db_path, exclude_tags=exclude_tags)
        total = len(records)

        for index, record in enumerate(records, start=1):
            doc_path = sqlite_reader.build_document_path(record.parent_key)

            pdf_file = sqlite_reader.resolve_pdf_path(
                data_dir,
                record.attachment_key,
                record.attachment_path,
                linked_attachment_base=linked_base,
            )
            extracted_pdf = ""
            if "pdf" in include_parts and pdf_file is not None:
                extracted_pdf = pdf_text.extract_pdf_text(pdf_file)

            notes = sqlite_reader.fetch_notes(db_path, record.parent_item_id)
            annotations = sqlite_reader.fetch_annotations(db_path, record.attachment_item_id)
            page_content = sqlite_reader.build_document_content(
                record,
                pdf_text=extracted_pdf,
                notes=notes,
                annotations=annotations,
                include_parts=include_parts,
            )
            if not page_content.strip():
                continue

            metadata = prepare_document_metadata(
                {
                    "repo": repo_name,
                    "provider": self.name,
                    "config_path": config_path.as_posix(),
                    "path": doc_path,
                    "title": record.title or record.parent_key,
                    "source_type": "paper",
                    "zotero_key": record.parent_key,
                    "attachment_key": record.attachment_key,
                    "creators": record.creators,
                    "year": record.year,
                    "doi": record.doi,
                    "tags": ", ".join(record.tags),
                },
                path=doc_path,
            )

            if sync_state is not None and sync_state.content_unchanged(doc_path, page_content):
                sync_state.note_skipped(doc_path)
                sync_state.record_metadata_refresh(doc_path, metadata)
                if reporter is not None:
                    reporter.on_skipped_file(doc_path)
                continue

            if sync_state is not None:
                sync_state.note_updated(doc_path)
            if reporter is not None:
                reporter.on_local_file(Path(doc_path), index, total)

            yield Document(page_content=page_content, metadata=metadata)

    @staticmethod
    def _resolve_data_dir(entry: Mapping[str, Any]) -> Path:
        configured = str(entry.get("data_dir") or entry.get("path") or DEFAULT_DATA_DIR)
        return Path(configured).expanduser().resolve()

    @staticmethod
    def _resolve_linked_base(entry: Mapping[str, Any]) -> Path | None:
        configured = str(entry.get("linked_attachment_base") or "").strip()
        if not configured:
            return None
        return Path(configured).expanduser().resolve()

    @staticmethod
    def _resolve_include(entry: Mapping[str, Any]) -> frozenset[str]:
        raw_include = entry.get("include")
        if raw_include is None:
            return DEFAULT_INCLUDE
        if isinstance(raw_include, str):
            values = [raw_include]
        elif isinstance(raw_include, Sequence):
            values = [str(value) for value in raw_include]
        else:
            return DEFAULT_INCLUDE
        resolved = {value.strip().lower() for value in values if value.strip()}
        return frozenset(resolved or DEFAULT_INCLUDE)

    @staticmethod
    def _resolve_exclude_tags(entry: Mapping[str, Any]) -> frozenset[str] | None:
        raw_tags = entry.get("exclude_tags")
        if raw_tags is None:
            return None
        if isinstance(raw_tags, str):
            values = [raw_tags]
        elif isinstance(raw_tags, Sequence):
            values = [str(value) for value in raw_tags]
        else:
            return None
        resolved = {value.strip().lower() for value in values if value.strip()}
        return frozenset(resolved) if resolved else None
