"""Tests for project path validation."""

from pathlib import Path

import pytest

from overleaf_mcp.errors import UnsafePathError
from overleaf_mcp.paths import resolve_project_path


@pytest.mark.parametrize(
    "relative_path",
    [
        "",
        "   ",
        "/etc/passwd",
        "../secret.tex",
        "foo/../../secret.tex",
        ".git/config",
        "nested/.git/hooks",
    ],
)
def test_resolve_project_path_rejects_unsafe_paths(tmp_path: Path, relative_path: str) -> None:
    repo_dir = tmp_path / "project"
    repo_dir.mkdir()
    with pytest.raises(UnsafePathError):
        resolve_project_path(repo_dir, relative_path)


def test_resolve_project_path_accepts_nested_file(tmp_path: Path) -> None:
    repo_dir = tmp_path / "project"
    nested = repo_dir / "chapters"
    nested.mkdir(parents=True)
    resolved = resolve_project_path(repo_dir, "chapters/intro.tex")
    assert resolved == (nested / "intro.tex").resolve()
