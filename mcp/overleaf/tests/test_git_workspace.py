"""Tests for git-backed Overleaf workspace operations."""

import subprocess
from pathlib import Path

import pytest
from git_helpers import make_bare_remote

from overleaf_mcp.errors import GitCommandError, ProjectFileNotFoundError
from overleaf_mcp.git_workspace import ASKPASS_FILENAME, GitWorkspace


def test_list_and_read_file(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    assert workspace.list_files() == ["main.tex"]
    assert workspace.read_file("main.tex") == "hello\n"


def test_write_file_pushes_to_remote(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    status = workspace.write_file("chapters/intro.tex", "new\n", "add intro")
    assert status == "Changes pushed to Overleaf."
    other = GitWorkspace(tmp_path / "clone2", str(bare))
    other.pull()
    assert other.read_file("chapters/intro.tex") == "new\n"


def test_write_file_without_changes(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    status = workspace.write_file("main.tex", "hello\n", "noop")
    assert status == "No changes to commit."


def test_delete_file_pushes_removal(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    workspace.delete_file("main.tex", "remove main")
    assert "main.tex" not in workspace.list_files()


@pytest.mark.parametrize(
    "method_name, kwargs",
    [
        ("read_file", {"relative_path": "missing.tex"}),
        ("delete_file", {"relative_path": "missing.tex", "commit_message": "rm"}),
    ],
)
def test_missing_file_raises(tmp_path: Path, method_name: str, kwargs: dict) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    method = getattr(workspace, method_name)
    with pytest.raises(ProjectFileNotFoundError):
        method(**kwargs)


def test_read_file_rejects_binary(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path, files={"pic.bin": b"\xff\xfe\x00\x01"})
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    with pytest.raises(GitCommandError, match="UTF-8"):
        workspace.read_file("pic.bin")


def test_ensure_cloned_is_idempotent(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(tmp_path / "clone", str(bare))
    workspace.ensure_cloned()
    workspace.ensure_cloned()
    assert (tmp_path / "clone" / ".git").exists()


def test_clone_failure_raises_git_error(tmp_path: Path) -> None:
    workspace = GitWorkspace(tmp_path / "clone", str(tmp_path / "missing.git"))
    with pytest.raises(GitCommandError, match="clone"):
        workspace.ensure_cloned()


def test_git_error_redacts_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    token = "olp_secret_token"
    workspace = GitWorkspace(
        tmp_path / "clone",
        "https://git.overleaf.com/abc",
        git_token=token,
        cache_dir=tmp_path,
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr=f"fatal: Authentication failed for {token}",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(GitCommandError) as exc_info:
        workspace.ensure_cloned()
    assert token not in str(exc_info.value)
    assert "***" in str(exc_info.value)


def test_git_env_writes_askpass_without_token(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    workspace = GitWorkspace(
        tmp_path / "clone",
        str(bare),
        git_token="olp_token",
        cache_dir=tmp_path / "cache",
    )
    workspace.ensure_cloned()
    askpass = tmp_path / "cache" / ASKPASS_FILENAME
    script = askpass.read_text()
    assert "olp_token" not in script
    assert "OVERLEAF_GIT_TOKEN" in script
