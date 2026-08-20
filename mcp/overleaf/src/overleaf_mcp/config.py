"""Load Overleaf MCP settings from the environment."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from overleaf_mcp.errors import ConfigError

ENV_GIT_TOKEN = "OVERLEAF_GIT_TOKEN"
ENV_PROJECTS = "OVERLEAF_PROJECTS"
ENV_PROJECT_ID = "OVERLEAF_PROJECT_ID"
ENV_DEFAULT_PROJECT = "OVERLEAF_DEFAULT_PROJECT"
ENV_CACHE_DIR = "OVERLEAF_CACHE_DIR"
ENV_GIT_HOST = "OVERLEAF_GIT_HOST"

DEFAULT_GIT_HOST = "git.overleaf.com"
DEFAULT_PROJECT_ALIAS = "default"
DEFAULT_CACHE_DIRNAME = "overleaf-mcp"
PROJECT_URL_MARKER = "/project/"


@dataclass(frozen=True)
class ProjectConfig:
    """A configured Overleaf project."""

    alias: str
    project_id: str


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Overleaf MCP server."""

    git_token: str
    projects: dict[str, ProjectConfig]
    default_alias: str
    cache_dir: Path
    git_host: str


def parse_project_id(value: str) -> str:
    """
    Extract an Overleaf project id from a raw id or project URL.

    Parameters
    ----------
    value
        Project id or ``https://www.overleaf.com/project/<id>`` URL.

    Returns
    -------
    str
        Bare project id.

    Raises
    ------
    ConfigError
        If the value is empty.
    """
    stripped = value.strip()
    if not stripped:
        raise ConfigError("Project id must not be empty.")
    if PROJECT_URL_MARKER in stripped:
        remainder = stripped.split(PROJECT_URL_MARKER, 1)[1]
        return remainder.strip("/").split("/", 1)[0]
    return stripped.strip("/")


def parse_projects(raw_projects: str) -> dict[str, ProjectConfig]:
    """
    Parse ``alias:id`` pairs separated by commas.

    Parameters
    ----------
    raw_projects
        Mapping such as ``thesis:abc123,paper:def456``.

    Returns
    -------
    dict[str, ProjectConfig]
        Projects keyed by alias.

    Raises
    ------
    ConfigError
        If the string is empty or an entry has no alias and id.
    """
    stripped = raw_projects.strip()
    if not stripped:
        raise ConfigError(f"{ENV_PROJECTS} must not be empty.")

    projects = {}
    for chunk in stripped.split(","):
        entry = chunk.strip()
        if not entry:
            continue
        if ":" not in entry:
            raise ConfigError(f"Invalid {ENV_PROJECTS} entry '{entry}'. Use alias:project_id.")
        alias, raw_id = entry.split(":", 1)
        alias = alias.strip()
        if not alias:
            raise ConfigError(f"Invalid {ENV_PROJECTS} entry '{entry}'. Alias is empty.")
        projects[alias] = ProjectConfig(alias=alias, project_id=parse_project_id(raw_id))

    if not projects:
        raise ConfigError(f"{ENV_PROJECTS} must declare at least one project.")
    return projects


def default_cache_dir(environ: Mapping[str, str] | None = None) -> Path:
    """
    Return the default clone cache directory.

    Parameters
    ----------
    environ
        Environment mapping. Defaults to ``os.environ``.
    """
    env = os.environ if environ is None else environ
    xdg_cache = env.get("XDG_CACHE_HOME", "").strip()
    if xdg_cache:
        return Path(xdg_cache) / DEFAULT_CACHE_DIRNAME
    return Path.home() / ".cache" / DEFAULT_CACHE_DIRNAME


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
        Parsed token, projects and cache location.

    Raises
    ------
    ConfigError
        If the Git token or project list is missing.
    """
    env = os.environ if environ is None else environ
    token = env.get(ENV_GIT_TOKEN, "").strip()
    if not token:
        raise ConfigError(f"{ENV_GIT_TOKEN} is required.")

    projects = _projects_from_env(env)
    default_alias = _default_alias(projects, env.get(ENV_DEFAULT_PROJECT, "").strip())
    cache_raw = env.get(ENV_CACHE_DIR, "").strip()
    cache_dir = Path(cache_raw) if cache_raw else default_cache_dir(env)
    git_host = env.get(ENV_GIT_HOST, "").strip() or DEFAULT_GIT_HOST

    return Settings(
        git_token=token,
        projects=projects,
        default_alias=default_alias,
        cache_dir=cache_dir,
        git_host=git_host,
    )


def _projects_from_env(env: Mapping[str, str]) -> dict[str, ProjectConfig]:
    """Build the project map from ``OVERLEAF_PROJECTS`` or ``OVERLEAF_PROJECT_ID``."""
    raw_projects = env.get(ENV_PROJECTS, "").strip()
    raw_project_id = env.get(ENV_PROJECT_ID, "").strip()
    if raw_projects:
        return parse_projects(raw_projects)
    if raw_project_id:
        project_id = parse_project_id(raw_project_id)
        return {
            DEFAULT_PROJECT_ALIAS: ProjectConfig(
                alias=DEFAULT_PROJECT_ALIAS,
                project_id=project_id,
            )
        }
    raise ConfigError(f"Set {ENV_PROJECTS} or {ENV_PROJECT_ID}.")


def _default_alias(projects: dict[str, ProjectConfig], requested: str) -> str:
    """Return the default alias, validating ``OVERLEAF_DEFAULT_PROJECT`` if set."""
    if not requested:
        return next(iter(projects))
    if requested not in projects:
        known = ", ".join(sorted(projects))
        raise ConfigError(f"Unknown default project '{requested}'. Known aliases: {known}.")
    return requested
