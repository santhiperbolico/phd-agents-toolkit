"""Tests for read-only Taurus service operations."""

import subprocess

import pytest

from taurus_mcp.config import Settings
from taurus_mcp.errors import (
    BinaryFileError,
    OutputLimitError,
    ReadLimitError,
    UnsafePathError,
)
from taurus_mcp.service import MAX_READ_BYTES, TaurusService


def _completed(argv, code=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, code, stdout, stderr)


def test_find_files_returns_matches() -> None:
    def runner(argv):
        return _completed(argv, stdout="/home/user/a.out\n/home/user/b.out\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.find_files("/home/user", "*.out") == "/home/user/a.out\n/home/user/b.out"


def test_grep_files_returns_matches() -> None:
    def runner(argv):
        return _completed(argv, stdout="/home/user/log:1:ERROR boom\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.grep_files("/home/user", "ERROR") == "/home/user/log:1:ERROR boom"


def test_list_dir_raises_when_output_too_large() -> None:
    lines = "\n".join(f"line{i}" for i in range(501))

    def runner(argv):
        return _completed(argv, stdout=lines + "\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    with pytest.raises(OutputLimitError, match="500 lines"):
        service.list_dir("/home/user")


def test_read_file_rejects_directory_path() -> None:
    def runner(argv):
        return _completed(argv, stdout="directory\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    with pytest.raises(BinaryFileError, match="directory"):
        service.read_file("/home/user")


def test_find_files_rejects_empty_pattern() -> None:
    service = TaurusService(Settings(ssh_host="taurus"), runner=lambda argv: _completed(argv))
    with pytest.raises(UnsafePathError, match="Name pattern"):
        service.find_files("/home/user", "  ")


def test_list_dir_runs_ls() -> None:
    calls = []

    def runner(argv):
        calls.append(argv)
        return _completed(argv, stdout="total 0\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.list_dir("/home/user") == "total 0"
    assert calls[0][-1] == "/home/user"
    assert "ls" in calls[0]


def test_read_file_rejects_binary_type() -> None:
    def runner(argv):
        if "file" in argv:
            return _completed(argv, stdout="ELF 64-bit LSB executable\n")
        return _completed(argv, stdout="ignored")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    with pytest.raises(BinaryFileError, match="non-text"):
        service.read_file("/home/user/bin/app")


def test_read_file_returns_text_within_limit() -> None:
    def runner(argv):
        if "file" in argv:
            return _completed(argv, stdout="ASCII text\n")
        if "head" in argv:
            return _completed(argv, stdout="hello\n")
        return _completed(argv)

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.read_file("/home/user/log.txt") == "hello\n"


def test_read_file_rejects_oversized_content() -> None:
    payload = "x" * (MAX_READ_BYTES + 1)

    def runner(argv):
        if "file" in argv:
            return _completed(argv, stdout="UTF-8 Unicode text\n")
        if "head" in argv:
            return _completed(argv, stdout=payload)
        return _completed(argv)

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    with pytest.raises(ReadLimitError, match="read limit"):
        service.read_file("/home/user/huge.log")


def test_find_files_caps_results() -> None:
    lines = "\n".join(f"/home/user/file{i}.txt" for i in range(201))

    def runner(argv):
        return _completed(argv, stdout=lines + "\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    with pytest.raises(OutputLimitError, match="200 entries"):
        service.find_files("/home/user", "*.txt")


def test_grep_files_returns_empty_on_no_matches() -> None:
    def runner(argv):
        return _completed(argv, code=1, stdout="", stderr="")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.grep_files("/home/user", "missing") == ""


def test_grep_files_rejects_empty_pattern() -> None:
    service = TaurusService(Settings(ssh_host="taurus"), runner=lambda argv: _completed(argv))
    with pytest.raises(UnsafePathError, match="pattern"):
        service.grep_files("/home/user", "   ")


def test_squeue_me_runs_exact_command() -> None:
    calls = []

    def runner(argv):
        calls.append(argv)
        return _completed(argv, stdout="12345 job1 RUNNING\n")

    service = TaurusService(Settings(ssh_host="taurus"), runner=runner)
    assert service.squeue_me() == "12345 job1 RUNNING"
    assert calls[0][-2:] == ["squeue", "--me"]
