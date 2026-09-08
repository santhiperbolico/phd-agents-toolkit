"""Runtime settings for ``phd_docs`` mapped onto ``claudia_docs``."""

import os
from pathlib import Path

from claudia_docs.config import Settings

DOCS_CONFIG = "phd_docs.json"
DEFAULT_PHD_DOCS_HOME = Path.home() / ".phd-docs"
DEFAULT_COLLECTION_NAME = "phd_docs"
DEFAULT_EMBEDDING_DEVICE = "cpu"
DEFAULT_TOOLKIT_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_embedding_device(env: dict[str, str] | None = None) -> str:
    """
    Resolve the torch device used for sentence-transformers.

    Parameters
    ----------
    env : dict[str, str], optional
        Environment mapping. Defaults to ``os.environ``.

    Returns
    -------
    str
        Device string such as ``cpu`` or ``cuda``.
    """
    source = env if env is not None else os.environ
    device = source.get("PHD_DOCS_EMBEDDING_DEVICE", DEFAULT_EMBEDDING_DEVICE).strip().lower()
    return device or DEFAULT_EMBEDDING_DEVICE


def configure_embedding_runtime(env: dict[str, str] | None = None) -> str:
    """
    Apply process-level settings before torch initializes CUDA.

    Parameters
    ----------
    env : dict[str, str], optional
        Environment mapping. Defaults to ``os.environ``.

    Returns
    -------
    str
        Selected embedding device.
    """
    device = resolve_embedding_device(env)
    if device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    return device


def resolve_toolkit_root() -> Path:
    """
    Resolve the ``phd-agents-toolkit`` repository root.

    Returns
    -------
    Path
        Absolute path to the toolkit root directory.
    """
    configured = os.environ.get("PHD_TOOLKIT_ROOT", "").strip()
    if configured:
        return Path(configured).resolve()
    return DEFAULT_TOOLKIT_ROOT.resolve()


def docs_config_path() -> Path:
    """
    Return the path to the main ``phd_docs.json`` configuration file.

    Returns
    -------
    Path
        Absolute path to ``docs/phd_docs.json`` under the toolkit root.
    """
    return resolve_toolkit_root() / "docs" / DOCS_CONFIG


def build_settings(env: dict[str, str] | None = None) -> Settings:
    """
    Build ``claudia_docs`` settings from PhD-specific environment variables.

    Parameters
    ----------
    env : dict[str, str], optional
        Environment mapping. Defaults to ``os.environ``.

    Returns
    -------
    Settings
        Runtime settings for sync and query pipelines.
    """
    source = dict(env if env is not None else os.environ)
    toolkit_root = resolve_toolkit_root()
    source.setdefault("CODE_HOME", str(toolkit_root))
    if "PHD_DOCS_HOME" in source and "CLAUDIA_DOCS_HOME" not in source:
        source["CLAUDIA_DOCS_HOME"] = source["PHD_DOCS_HOME"]
    source.setdefault("CLAUDIA_DOCS_HOME", str(DEFAULT_PHD_DOCS_HOME))
    source.setdefault("CLAUDIA_DOCS_COLLECTION", DEFAULT_COLLECTION_NAME)
    source["PHD_TOOLKIT_ROOT"] = str(toolkit_root)
    return Settings.from_env(source)
