"""Register PhD-specific extraction providers."""

from claudia_docs.extractors.external.providers import local_folder as _local_folder

from phd_docs.extractors.zotero import provider as _zotero_provider

_REGISTERED = False


def register_phd_providers() -> None:
    """Import provider modules so they register with ``ProviderRegistry``."""
    global _REGISTERED
    if _REGISTERED:
        return
    _ = (_local_folder, _zotero_provider)
    _REGISTERED = True
