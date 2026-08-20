"""Tests for MCP tool wrappers."""

import pytest

from taurus_mcp import server


def _invoke(tool, *args, **kwargs):
    """Call a FastMCP tool through its underlying function when present."""
    target = getattr(tool, "fn", tool)
    return target(*args, **kwargs)


class FakeService:
    """Minimal service double for MCP tool tests."""

    def list_dir(self, path):
        return f"dir:{path}"

    def read_file(self, path):
        return f"file:{path}"

    def find_files(self, path, name_pattern):
        return f"find:{path}:{name_pattern}"

    def grep_files(self, path, pattern):
        return f"grep:{path}:{pattern}"

    def squeue_me(self):
        return "JOB 1 RUNNING"


@pytest.fixture
def fake_service(monkeypatch: pytest.MonkeyPatch) -> FakeService:
    service = FakeService()
    monkeypatch.setattr(server, "get_service", lambda: service)
    return service


def test_list_dir_tool(fake_service: FakeService) -> None:
    assert _invoke(server.list_dir, "/home/user/logs") == "dir:/home/user/logs"


def test_read_file_tool(fake_service: FakeService) -> None:
    assert _invoke(server.read_file, "/home/user/out.log") == "file:/home/user/out.log"


def test_find_and_grep_tools(fake_service: FakeService) -> None:
    assert _invoke(server.find_files, "/home/user", "*.out") == "find:/home/user:*.out"
    assert _invoke(server.grep_files, "/home/user", "ERROR") == "grep:/home/user:ERROR"


def test_squeue_me_tool(fake_service: FakeService) -> None:
    assert _invoke(server.squeue_me) == "JOB 1 RUNNING"


def test_get_service_uses_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        server,
        "load_settings",
        lambda: type("Settings", (), {"ssh_host": "taurus"})(),
    )
    service = server.get_service()
    assert service.settings.ssh_host == "taurus"
