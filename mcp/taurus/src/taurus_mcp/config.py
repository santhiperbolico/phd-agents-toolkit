"""Load Taurus MCP settings from the environment."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

ENV_SSH_HOST = "TAURUS_SSH_HOST"
DEFAULT_SSH_HOST = "taurus"


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Taurus MCP server."""

    ssh_host: str


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """
    Load settings from environment variables.

    Parameters
    ----------
    environ
        Mapping of environment variables. Defaults to ``os.environ``.

    Returns
    -------
    Settings
        Parsed SSH host alias.
    """
    env = os.environ if environ is None else environ
    ssh_host = env.get(ENV_SSH_HOST, "").strip() or DEFAULT_SSH_HOST
    return Settings(ssh_host=ssh_host)
