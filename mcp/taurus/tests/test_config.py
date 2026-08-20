"""Tests for environment configuration."""

from taurus_mcp.config import DEFAULT_SSH_HOST, ENV_SSH_HOST, load_settings


def test_load_settings_default_host() -> None:
    settings = load_settings({})
    assert settings.ssh_host == DEFAULT_SSH_HOST


def test_load_settings_custom_host() -> None:
    settings = load_settings({ENV_SSH_HOST: "taurus-dev"})
    assert settings.ssh_host == "taurus-dev"


def test_load_settings_whitespace_host_falls_back_to_default() -> None:
    settings = load_settings({ENV_SSH_HOST: "   "})
    assert settings.ssh_host == DEFAULT_SSH_HOST
