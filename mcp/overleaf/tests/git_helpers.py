"""Git helpers for Overleaf MCP tests."""

import subprocess
from pathlib import Path

TEST_USER_NAME = "Test User"
TEST_USER_EMAIL = "test@example.com"


def run_git(args: list[str], cwd: Path) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def set_git_identity(repo_dir: Path) -> None:
    """Set a local git author so tests can commit."""
    run_git(["config", "user.name", TEST_USER_NAME], repo_dir)
    run_git(["config", "user.email", TEST_USER_EMAIL], repo_dir)


def make_bare_remote(tmp_path: Path, files: dict[str, str | bytes] | None = None) -> Path:
    """
    Create a bare git remote with an initial commit.

    Parameters
    ----------
    tmp_path
        Pytest temporary directory.
    files
        Paths mapped to text or binary content. Defaults to ``main.tex``.

    Returns
    -------
    Path
        Path of the bare repository.
    """
    contents = files if files is not None else {"main.tex": "hello\n"}
    work = tmp_path / "origin-work"
    work.mkdir()
    run_git(["init", "-b", "main"], work)
    set_git_identity(work)
    for name, content in contents.items():
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content)
        run_git(["add", "--", name], work)
    run_git(["commit", "-m", "init"], work)
    bare = tmp_path / "remote.git"
    run_git(["clone", "--bare", str(work), str(bare)], tmp_path)
    return bare
