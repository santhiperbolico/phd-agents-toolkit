"""Tests for the taurus-tools CLI."""

import pytest

from taurus_mcp.cli import MCP_COMMAND, main


def test_cli_runs_mcp_subcommand(monkeypatch: pytest.MonkeyPatch) -> None:
    called = []
    monkeypatch.setattr("taurus_mcp.cli.mcp.run", lambda: called.append(True))
    main([MCP_COMMAND])
    assert called == [True]


@pytest.mark.parametrize("argv", [[], ["not-a-command"]])
def test_cli_rejects_invalid_args(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        main(argv)
