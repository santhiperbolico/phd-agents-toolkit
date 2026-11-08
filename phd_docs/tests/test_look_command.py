"""Tests for look command."""

import json
from argparse import Namespace

from phd_docs.cli.commands.look import LookCommand
from phd_docs.config import build_settings


def test_look_command_prints_json(monkeypatch, capsys):
    settings = build_settings()
    command = LookCommand(settings=settings)
    exit_code = command.run(Namespace(json=True))
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    providers = {entry["provider"] for entry in payload}
    assert "LocalFolder" in providers
    assert "Zotero" in providers
