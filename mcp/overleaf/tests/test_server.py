"""Tests for MCP tool wrappers."""

from pathlib import Path

import pytest

from overleaf_mcp import server


def _invoke(tool, *args, **kwargs):
    """Call a FastMCP tool through its underlying function when present."""
    target = getattr(tool, "fn", tool)
    return target(*args, **kwargs)


class FakeService:
    """Minimal service double for MCP tool tests."""

    def list_projects(self):
        return [{"alias": "thesis", "project_id": "abc", "default": True}]

    def sync_project(self, project=None):
        return f"synced:{project}"

    def list_files(self, project=None):
        return [f"{project}/main.tex"]

    def read_file(self, path, project=None):
        return f"{project}:{path}"

    def write_file(self, path, content, project=None, commit_message=None):
        return f"write:{project}:{path}:{content}:{commit_message}"

    def delete_file(self, path, project=None, commit_message=None):
        return f"delete:{project}:{path}:{commit_message}"


@pytest.fixture
def fake_service(monkeypatch: pytest.MonkeyPatch) -> FakeService:
    service = FakeService()
    monkeypatch.setattr(server, "get_service", lambda: service)
    return service


def test_list_projects_tool(fake_service: FakeService) -> None:
    assert _invoke(server.list_projects)[0]["alias"] == "thesis"


def test_sync_and_list_files_tools(fake_service: FakeService) -> None:
    assert _invoke(server.sync_project, "thesis") == "synced:thesis"
    assert _invoke(server.list_files, "thesis") == ["thesis/main.tex"]


def test_read_write_delete_tools(fake_service: FakeService) -> None:
    assert _invoke(server.read_file, "main.tex", "thesis") == "thesis:main.tex"
    written = _invoke(server.write_file, "main.tex", "body", "thesis", "msg")
    assert written == "write:thesis:main.tex:body:msg"
    deleted = _invoke(server.delete_file, "main.tex", "thesis", "rm")
    assert deleted == "delete:thesis:main.tex:rm"


def test_get_service_uses_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        server,
        "load_settings",
        lambda: type(
            "Settings",
            (),
            {
                "git_token": "tok",
                "projects": {},
                "default_alias": "default",
                "cache_dir": tmp_path,
                "git_host": "git.overleaf.com",
            },
        )(),
    )
    service = server.get_service()
    assert service.settings.git_token == "tok"
