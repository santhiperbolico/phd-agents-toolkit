"""Tests for remote path validation."""

import pytest

from taurus_mcp.errors import UnsafePathError
from taurus_mcp.paths import validate_remote_path


@pytest.mark.parametrize(
    "path",
    [
        "/home/user/project",
        "project/logs",
        "./logs",
    ],
)
def test_validate_remote_path_accepts_safe_paths(path: str) -> None:
    assert validate_remote_path(path) == path.strip()


@pytest.mark.parametrize(
    "path",
    [
        "",
        "   ",
        "../etc/passwd",
        "/home/user/../secret",
        "logs/../secret",
        "-la",
        "/home/user\n/etc/passwd",
    ],
)
def test_validate_remote_path_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(UnsafePathError):
        validate_remote_path(path)


def test_validate_remote_path_rejects_null_byte() -> None:
    with pytest.raises(UnsafePathError, match="null or newline"):
        validate_remote_path("logs\0/evil")


def test_validate_remote_path_strips_whitespace() -> None:
    assert validate_remote_path("  /home/user  ") == "/home/user"
