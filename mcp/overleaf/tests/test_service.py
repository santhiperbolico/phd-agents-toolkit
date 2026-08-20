"""Tests for the Overleaf service layer."""

from pathlib import Path

import pytest
from git_helpers import make_bare_remote

from overleaf_mcp.config import ProjectConfig, Settings
from overleaf_mcp.errors import UnknownProjectError
from overleaf_mcp.service import OverleafService


def _service(tmp_path: Path, bare: Path, alias: str = "thesis") -> OverleafService:
    settings = Settings(
        git_token="local-test",
        projects={alias: ProjectConfig(alias=alias, project_id="proj1")},
        default_alias=alias,
        cache_dir=tmp_path / "cache",
        git_host="git.overleaf.com",
    )
    return OverleafService(settings, remote_url_for=lambda _project_id: str(bare))


def test_list_projects_marks_default(tmp_path: Path) -> None:
    settings = Settings(
        git_token="tok",
        projects={
            "thesis": ProjectConfig("thesis", "aaa"),
            "paper": ProjectConfig("paper", "bbb"),
        },
        default_alias="paper",
        cache_dir=tmp_path,
        git_host="git.overleaf.com",
    )
    service = OverleafService(settings)
    rows = service.list_projects()
    by_alias = {row["alias"]: row for row in rows}
    assert by_alias["paper"]["default"] is True
    assert by_alias["thesis"]["default"] is False
    assert service.remote_url("aaa") == "https://git.overleaf.com/aaa"


def test_service_file_roundtrip(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    service = _service(tmp_path, bare)
    assert service.sync_project().startswith("Synced")
    assert "main.tex" in service.list_files()
    assert service.read_file("main.tex") == "hello\n"
    service.write_file("main.tex", "body\n", commit_message="edit")
    assert service.read_file("main.tex") == "body\n"
    service.delete_file("main.tex")
    assert "main.tex" not in service.list_files()


def test_unknown_project_raises(tmp_path: Path) -> None:
    bare = make_bare_remote(tmp_path)
    service = _service(tmp_path, bare)
    with pytest.raises(UnknownProjectError, match="Unknown project"):
        service.list_files("missing")
