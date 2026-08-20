"""Tests for the overleaf-tools CLI."""

import pytest

from overleaf_mcp.cli import MCP_COMMAND, main


def test_cli_runs_mcp_subcommand(monkeypatch: pytest.MonkeyPatch) -> None:
    called = []
    monkeypatch.setattr("overleaf_mcp.cli.mcp.run", lambda: called.append(True))
    main([MCP_COMMAND])
    assert called == [True]


@pytest.mark.parametrize("argv", [[], ["not-a-command"]])
def test_cli_rejects_invalid_args(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        main(argv)
