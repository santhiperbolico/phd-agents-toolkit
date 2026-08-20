"""Run allowlisted commands on Taurus through the local ssh binary."""

import subprocess
from collections.abc import Callable, Sequence

from taurus_mcp.config import Settings
from taurus_mcp.errors import SshCommandError

ALLOWED_BINARIES = frozenset({"ls", "find", "grep", "head", "file", "squeue"})
SSH_COMMAND = "ssh"
SSH_OPTIONS = ("-o", "BatchMode=yes", "-o", "ConnectTimeout=15")

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def build_ssh_argv(ssh_host: str, binary: str, *remote_args: str) -> list[str]:
    """
    Build a fixed argv list for ``ssh host -- binary ...``.

    Parameters
    ----------
    ssh_host
        SSH config host alias, for example ``taurus``.
    binary
        Allowlisted remote binary name.
    remote_args
        Arguments passed to the remote binary after ``--``.

    Returns
    -------
    list[str]
        Local argv for ``subprocess.run``.

    Raises
    ------
    ValueError
        If the binary is not allowlisted.
    """
    if binary not in ALLOWED_BINARIES:
        raise ValueError(f"Binary '{binary}' is not allowlisted.")
    return [
        SSH_COMMAND,
        *SSH_OPTIONS,
        ssh_host,
        "--",
        binary,
        *remote_args,
    ]


def default_command_runner(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """
    Execute a local argv list without shell interpolation.

    Parameters
    ----------
    argv
        Command and arguments for ``subprocess.run``.

    Returns
    -------
    subprocess.CompletedProcess[str]
        Completed process with decoded stdout and stderr.
    """
    return subprocess.run(
        list(argv),
        check=False,
        capture_output=True,
        text=True,
    )


class SshClient:
    """Execute fixed remote commands through ``ssh``."""

    def __init__(
        self,
        settings: Settings,
        runner: CommandRunner | None = None,
    ) -> None:
        self.settings = settings
        self._runner = runner or default_command_runner

    def run(
        self,
        binary: str,
        *remote_args: str,
        allowed_returncodes: frozenset[int] | None = None,
    ) -> str:
        """
        Run an allowlisted binary on Taurus and return stdout.

        Parameters
        ----------
        binary
            Remote command name from the allowlist.
        remote_args
            Arguments forwarded to the remote binary.
        allowed_returncodes
            Exit codes treated as success. Defaults to ``{0}`` only.

        Returns
        -------
        str
            Standard output with trailing whitespace stripped.

        Raises
        ------
        SshCommandError
            If the SSH process exits with a non-zero status.
        """
        argv = build_ssh_argv(self.settings.ssh_host, binary, *remote_args)
        completed = self._runner(argv)
        allowed = allowed_returncodes or frozenset({0})
        if completed.returncode not in allowed:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise SshCommandError(f"Remote command failed ({binary}): {detail or 'unknown error'}")
        return completed.stdout
