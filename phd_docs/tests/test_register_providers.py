"""Tests for provider registration."""

from claudia_docs.extractors.external.providers.registry import ProviderRegistry

from phd_docs.extractors import register_phd_providers


def test_register_phd_providers_registers_local_and_zotero():
    register_phd_providers()
    providers = ProviderRegistry.known_providers()
    assert "localfolder" in providers
    assert "zotero" in providers
