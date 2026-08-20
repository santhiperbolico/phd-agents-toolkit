"""FastMCP server exposing Overleaf Git file tools."""

from fastmcp import FastMCP

from overleaf_mcp.config import load_settings
from overleaf_mcp.service import OverleafService

mcp = FastMCP(name="overleaf")


def get_service() -> OverleafService:
    """Build a service from the current process environment."""
    return OverleafService(load_settings())


@mcp.tool()
def list_projects() -> list[dict[str, str | bool]]:
    """List configured Overleaf project aliases and their ids."""
    return get_service().list_projects()


@mcp.tool()
def sync_project(project: str | None = None) -> str:
    """
    Pull the latest files from Overleaf into the local cache.

    Parameters
    ----------
    project
        Project alias. Omit to use the default project.
    """
    return get_service().sync_project(project)


@mcp.tool()
def list_files(project: str | None = None) -> list[str]:
    """
    Pull from Overleaf and list tracked files in the project.

    Parameters
    ----------
    project
        Project alias. Omit to use the default project.
    """
    return get_service().list_files(project)


@mcp.tool()
def read_file(path: str, project: str | None = None) -> str:
    """
    Read a UTF-8 text file from the Overleaf project clone.

    Parameters
    ----------
    path
        Path relative to the project root, for example ``main.tex``.
    project
        Project alias. Omit to use the default project.
    """
    return get_service().read_file(path, project)


@mcp.tool()
def write_file(
    path: str,
    content: str,
    project: str | None = None,
    commit_message: str | None = None,
) -> str:
    """
    Write a text file, commit, and push the change to Overleaf.

    Parameters
    ----------
    path
        Path relative to the project root.
    content
        Full file contents to write.
    project
        Project alias. Omit to use the default project.
    commit_message
        Optional git commit message.
    """
    return get_service().write_file(path, content, project, commit_message)


@mcp.tool()
def delete_file(
    path: str,
    project: str | None = None,
    commit_message: str | None = None,
) -> str:
    """
    Delete a file, commit, and push the removal to Overleaf.

    Parameters
    ----------
    path
        Path relative to the project root.
    project
        Project alias. Omit to use the default project.
    commit_message
        Optional git commit message.
    """
    return get_service().delete_file(path, commit_message=commit_message, project=project)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()
