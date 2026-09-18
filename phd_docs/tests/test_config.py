"""Tests for phd_docs.config."""

import os

from phd_docs.config import (
    build_settings,
    configure_embedding_runtime,
    docs_config_path,
    resolve_toolkit_root,
)


def test_resolve_toolkit_root_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PHD_TOOLKIT_ROOT", str(tmp_path))
    assert resolve_toolkit_root() == tmp_path.resolve()


def test_docs_config_path_points_to_docs_json(tmp_path, monkeypatch):
    monkeypatch.setenv("PHD_TOOLKIT_ROOT", str(tmp_path))
    assert docs_config_path() == tmp_path / "docs" / "phd_docs.json"


def test_build_settings_maps_phd_docs_home(monkeypatch):
    monkeypatch.setenv("PHD_TOOLKIT_ROOT", "/tmp/toolkit")
    monkeypatch.setenv("PHD_DOCS_HOME", "/tmp/phd-index")
    settings = build_settings()
    assert str(settings.docs_home) == "/tmp/phd-index"
    assert settings.collection_name == "phd_docs"


def test_configure_embedding_runtime_forces_cpu(monkeypatch):
    monkeypatch.delenv("CUDA_VISIBLE_DEVICES", raising=False)
    device = configure_embedding_runtime({"PHD_DOCS_EMBEDDING_DEVICE": "cpu"})
    assert device == "cpu"
    assert os.environ["CUDA_VISIBLE_DEVICES"] == ""
