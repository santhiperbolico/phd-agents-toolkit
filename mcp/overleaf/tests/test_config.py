"""Tests for Overleaf MCP environment settings."""

from pathlib import Path

import pytest

from overleaf_mcp.config import (
    DEFAULT_GIT_HOST,
    DEFAULT_PROJECT_ALIAS,
    ENV_CACHE_DIR,
    ENV_DEFAULT_PROJECT,
    ENV_GIT_HOST,
    ENV_GIT_TOKEN,
    ENV_PROJECT_ID,
    ENV_PROJECTS,
    load_settings,
    parse_project_id,
    parse_projects,
)
from overleaf_mcp.errors import ConfigError


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("abc123", "abc123"),
        ("abc123/", "abc123"),
        ("https://www.overleaf.com/project/abc123", "abc123"),
        ("https://www.overleaf.com/project/abc123/", "abc123"),
        ("https://www.overleaf.com/project/abc123/extra", "abc123"),
    ],
)
def test_parse_project_id(raw: str, expected: str) -> None:
    assert parse_project_id(raw) == expected


def test_parse_project_id_rejects_empty() -> None:
    with pytest.raises(ConfigError, match="empty"):
        parse_project_id("  ")


@pytest.mark.parametrize(
    "raw, expected_ids",
    [
        ("thesis:abc", {"thesis": "abc"}),
        (
            "thesis:abc, paper:https://www.overleaf.com/project/def",
            {"thesis": "abc", "paper": "def"},
        ),
        ("thesis:abc,,paper:def", {"thesis": "abc", "paper": "def"}),
    ],
)
def test_parse_projects(raw: str, expected_ids: dict[str, str]) -> None:
    parsed = parse_projects(raw)
    assert {alias: project.project_id for alias, project in parsed.items()} == expected_ids


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "abc", ":abc", " , , "],
)
def test_parse_projects_rejects_invalid(raw: str) -> None:
    with pytest.raises(ConfigError):
        parse_projects(raw)


def test_load_settings_from_projects(tmp_path: Path) -> None:
    settings = load_settings(
        {
            ENV_GIT_TOKEN: "tok",
            ENV_PROJECTS: "thesis:abc,paper:def",
            ENV_CACHE_DIR: str(tmp_path),
        }
    )
    assert settings.git_token == "tok"
    assert settings.default_alias == "thesis"
    assert settings.projects["paper"].project_id == "def"
    assert settings.cache_dir == tmp_path
    assert settings.git_host == DEFAULT_GIT_HOST


def test_load_settings_from_project_id(tmp_path: Path) -> None:
    settings = load_settings(
        {
            ENV_GIT_TOKEN: "tok",
            ENV_PROJECT_ID: "https://www.overleaf.com/project/abc123",
            ENV_CACHE_DIR: str(tmp_path),
            ENV_GIT_HOST: "git.example.edu",
        }
    )
    assert settings.default_alias == DEFAULT_PROJECT_ALIAS
    assert settings.projects[DEFAULT_PROJECT_ALIAS].project_id == "abc123"
    assert settings.git_host == "git.example.edu"


def test_load_settings_honours_default_project(tmp_path: Path) -> None:
    settings = load_settings(
        {
            ENV_GIT_TOKEN: "tok",
            ENV_PROJECTS: "thesis:abc,paper:def",
            ENV_DEFAULT_PROJECT: "paper",
            ENV_CACHE_DIR: str(tmp_path),
        }
    )
    assert settings.default_alias == "paper"


def test_load_settings_uses_xdg_cache_home(tmp_path: Path) -> None:
    settings = load_settings(
        {
            ENV_GIT_TOKEN: "tok",
            ENV_PROJECT_ID: "abc",
            "XDG_CACHE_HOME": str(tmp_path),
        }
    )
    assert settings.cache_dir == tmp_path / "overleaf-mcp"


@pytest.mark.parametrize(
    "env",
    [
        {},
        {ENV_GIT_TOKEN: "tok"},
        {ENV_GIT_TOKEN: "tok", ENV_PROJECTS: "thesis:abc", ENV_DEFAULT_PROJECT: "missing"},
        {ENV_PROJECT_ID: "abc"},
    ],
)
def test_load_settings_rejects_invalid_env(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_settings(env)
