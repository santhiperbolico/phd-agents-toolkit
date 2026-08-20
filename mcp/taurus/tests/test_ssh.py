"""Tests for SSH argv building and client execution."""

import subprocess

import pytest

from taurus_mcp.config import Settings
from taurus_mcp.errors import SshCommandError
from taurus_mcp.ssh import SshClient, build_ssh_argv


def test_build_ssh_argv_uses_allowlisted_binary() -> None:
    argv = build_ssh_argv("taurus", "ls", "-la", "--", "/tmp")
    assert argv[:6] == ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "taurus"]
    assert argv[6:] == ["--", "ls", "-la", "--", "/tmp"]


def test_build_ssh_argv_rejects_unknown_binary() -> None:
    with pytest.raises(ValueError, match="not allowlisted"):
        build_ssh_argv("taurus", "rm", "-rf", "/")


def test_ssh_client_returns_stdout() -> None:
    settings = Settings(ssh_host="taurus")

    def runner(argv):
        assert argv[-2:] == ["squeue", "--me"]
        return subprocess.CompletedProcess(argv, 0, "JOBID NAME\n", "")

    client = SshClient(settings, runner=runner)
    assert client.run("squeue", "--me") == "JOBID NAME\n"


def test_ssh_client_raises_on_failure() -> None:
    settings = Settings(ssh_host="taurus")

    def runner(argv):
        return subprocess.CompletedProcess(argv, 2, "", "permission denied")

    client = SshClient(settings, runner=runner)
    with pytest.raises(SshCommandError, match="permission denied"):
        client.run("ls", "--", "/secret")


def test_ssh_client_allows_configured_returncodes() -> None:
    settings = Settings(ssh_host="taurus")

    def runner(argv):
        return subprocess.CompletedProcess(argv, 1, "", "")

    client = SshClient(settings, runner=runner)
    assert client.run("grep", "pattern", allowed_returncodes=frozenset({0, 1})) == ""
