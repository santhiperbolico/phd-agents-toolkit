"""FastMCP server exposing read-only Taurus cluster tools."""

from fastmcp import FastMCP

from taurus_mcp.config import load_settings
from taurus_mcp.service import TaurusService

mcp = FastMCP(name="taurus")


def get_service() -> TaurusService:
    """Build a service from the current process environment."""
    return TaurusService(load_settings())


@mcp.tool()
def list_dir(path: str) -> str:
    """
    List a directory on Taurus with ``ls -la``.

    Parameters
    ----------
    path
        Remote directory path, for example ``/home/you/project/logs``.
    """
    return get_service().list_dir(path)


@mcp.tool()
def read_file(path: str) -> str:
    """
    Read a remote text file from Taurus (max 1 MiB).

    Parameters
    ----------
    path
        Remote file path.
    """
    return get_service().read_file(path)


@mcp.tool()
def find_files(path: str, name_pattern: str) -> str:
    """
    Find files by name under a remote directory.

    Parameters
    ----------
    path
        Root directory for the search.
    name_pattern
        ``find -name`` pattern, for example ``*.out`` or ``slurm-*.log``.
    """
    return get_service().find_files(path, name_pattern)


@mcp.tool()
def grep_files(path: str, pattern: str) -> str:
    """
    Recursively grep text under a remote path.

    Parameters
    ----------
    path
        File or directory to search on Taurus.
    pattern
        Extended regular expression (``grep -E``).
    """
    return get_service().grep_files(path, pattern)


@mcp.tool()
def squeue_me() -> str:
    """Show the current user's Slurm jobs (``squeue --me``)."""
    return get_service().squeue_me()


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()
