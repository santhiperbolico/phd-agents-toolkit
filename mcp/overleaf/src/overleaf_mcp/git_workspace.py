"""Git clone, pull, read and write helpers for an Overleaf project."""

import os
import subprocess
from pathlib import Path

from overleaf_mcp.errors import GitCommandError, ProjectFileNotFoundError
from overleaf_mcp.paths import resolve_project_path

GIT_USERNAME = "git"
ASKPASS_FILENAME = "git-askpass.sh"
DEFAULT_AUTHOR_NAME = "Overleaf MCP"
DEFAULT_AUTHOR_EMAIL = "overleaf-mcp@localhost"
POST_BUFFER_BYTES = "10485760"
TEXT_ENCODING = "utf-8"

ASKPASS_SCRIPT = """#!/bin/sh
case "$1" in
  *[Uu]sername*) printf '%s\\n' git ;;
  *) printf '%s\\n' "$OVERLEAF_GIT_TOKEN" ;;
esac
"""


class GitWorkspace:
    """Local git clone used to sync one Overleaf project."""

    def __init__(
        self,
        repo_dir: Path,
        remote_url: str,
        git_token: str | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        """
        Parameters
        ----------
        repo_dir
            Directory that holds the local clone.
        remote_url
            Git remote URL (Overleaf or a local path in tests).
        git_token
            Overleaf Git token used as the HTTPS password. Optional for
            file remotes.
        cache_dir
            Directory where the askpass helper is written when a token is set.
        """
        self.repo_dir = repo_dir
        self.remote_url = remote_url
        self.git_token = git_token
        self.cache_dir = cache_dir if cache_dir is not None else repo_dir.parent

    def ensure_cloned(self) -> None:
        """Clone the remote if the local directory is not a git repository."""
        if (self.repo_dir / ".git").exists():
            return
        self.repo_dir.parent.mkdir(parents=True, exist_ok=True)
        self._run_git(["clone", self.remote_url, str(self.repo_dir)], cwd=None)
        self._configure_repo()

    def pull(self) -> None:
        """Fetch and rebase the latest commits from the remote."""
        self.ensure_cloned()
        self._run_git(["pull", "--rebase"], cwd=self.repo_dir)

    def list_files(self) -> list[str]:
        """
        Return tracked file paths relative to the project root.

        Returns
        -------
        list[str]
            POSIX paths of files tracked by git.
        """
        self.ensure_cloned()
        output = self._run_git(["ls-files"], cwd=self.repo_dir)
        return [line for line in output.splitlines() if line]

    def read_file(self, relative_path: str) -> str:
        """
        Read a UTF-8 text file from the local clone.

        Parameters
        ----------
        relative_path
            Path relative to the project root.

        Returns
        -------
        str
            File contents.

        Raises
        ------
        ProjectFileNotFoundError
            If the file does not exist.
        GitCommandError
            If the file is not valid UTF-8 text.
        """
        self.ensure_cloned()
        target = resolve_project_path(self.repo_dir, relative_path)
        if not target.is_file():
            raise ProjectFileNotFoundError(f"File not found: {relative_path}")
        try:
            return target.read_text(encoding=TEXT_ENCODING)
        except UnicodeDecodeError as exc:
            raise GitCommandError(f"File is not UTF-8 text: {relative_path}") from exc

    def write_file(self, relative_path: str, content: str, commit_message: str) -> str:
        """
        Write a text file, commit, and push to the remote.

        Parameters
        ----------
        relative_path
            Path relative to the project root.
        content
            Full file contents to write.
        commit_message
            Message used if the working tree changes.

        Returns
        -------
        str
            Short status message.
        """
        self.pull()
        target = resolve_project_path(self.repo_dir, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=TEXT_ENCODING)
        self._run_git(["add", "--", _posix_relative(self.repo_dir, target)], cwd=self.repo_dir)
        return self._commit_and_push(commit_message)

    def delete_file(self, relative_path: str, commit_message: str) -> str:
        """
        Remove a tracked file, commit, and push to the remote.

        Parameters
        ----------
        relative_path
            Path relative to the project root.
        commit_message
            Message used for the deletion commit.

        Returns
        -------
        str
            Short status message.
        """
        self.pull()
        target = resolve_project_path(self.repo_dir, relative_path)
        if not target.is_file():
            raise ProjectFileNotFoundError(f"File not found: {relative_path}")
        self._run_git(["rm", "--", _posix_relative(self.repo_dir, target)], cwd=self.repo_dir)
        return self._commit_and_push(commit_message)

    def _commit_and_push(self, commit_message: str) -> str:
        status = self._run_git(["status", "--porcelain"], cwd=self.repo_dir)
        if not status.strip():
            return "No changes to commit."
        self._run_git(["commit", "-m", commit_message], cwd=self.repo_dir)
        self._run_git(["push"], cwd=self.repo_dir)
        return "Changes pushed to Overleaf."

    def _configure_repo(self) -> None:
        self._run_git(["config", "http.postBuffer", POST_BUFFER_BYTES], cwd=self.repo_dir)
        self._run_git(["config", "core.fileMode", "false"], cwd=self.repo_dir)
        if not self._read_config("user.name"):
            self._run_git(["config", "user.name", DEFAULT_AUTHOR_NAME], cwd=self.repo_dir)
        if not self._read_config("user.email"):
            self._run_git(["config", "user.email", DEFAULT_AUTHOR_EMAIL], cwd=self.repo_dir)

    def _read_config(self, key: str) -> str:
        result = subprocess.run(
            ["git", "config", "--get", key],
            cwd=self.repo_dir,
            env=self._git_env(),
            check=False,
            capture_output=True,
            text=True,
            encoding=TEXT_ENCODING,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()

    def _askpass_path(self) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self.cache_dir / ASKPASS_FILENAME
        if not path.exists():
            path.write_text(ASKPASS_SCRIPT, encoding=TEXT_ENCODING)
            path.chmod(0o700)
        return path

    def _git_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        if self.git_token:
            env["OVERLEAF_GIT_TOKEN"] = self.git_token
            env["GIT_ASKPASS"] = str(self._askpass_path())
            env["SSH_ASKPASS"] = env["GIT_ASKPASS"]
            env["GIT_USERNAME"] = GIT_USERNAME
        return env

    def _redact(self, text: str) -> str:
        if self.git_token:
            return text.replace(self.git_token, "***")
        return text

    def _run_git(self, args: list[str], cwd: Path | None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=self._git_env(),
            check=False,
            capture_output=True,
            text=True,
            encoding=TEXT_ENCODING,
        )
        if result.returncode != 0:
            detail = self._redact((result.stderr or result.stdout or "").strip())
            raise GitCommandError(f"git {' '.join(args)} failed: {detail}")
        return result.stdout


def _posix_relative(repo_dir: Path, target: Path) -> str:
    """Return ``target`` as a POSIX path relative to the clone root."""
    return target.relative_to(repo_dir.resolve()).as_posix()
