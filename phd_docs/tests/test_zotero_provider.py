"""Tests for Zotero provider configuration helpers."""

from phd_docs.extractors.zotero.provider import ZoteroProviderExtractor


def test_resolve_exclude_tags_normalizes_case():
    entry = {"exclude_tags": ["To-Read", "draft"]}
    resolved = ZoteroProviderExtractor._resolve_exclude_tags(entry)
    assert resolved == frozenset({"to-read", "draft"})


def test_resolve_include_defaults_to_all_sections():
    resolved = ZoteroProviderExtractor._resolve_include({})
    assert "pdf" in resolved
    assert "annotations" in resolved
