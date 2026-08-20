"""Validate remote paths passed to SSH commands."""

from taurus_mcp.errors import UnsafePathError

PARENT_DIR = ".."


def validate_remote_path(path: str) -> str:
    """
    Validate a remote filesystem path before passing it to SSH.

    Parameters
    ----------
    path
        Remote path relative to the SSH user's home or absolute on Taurus.

    Returns
    -------
    str
        Trimmed path.

    Raises
    ------
    UnsafePathError
        If the path is empty, starts with ``-``, contains null/newline
        bytes, or uses parent segments.
    """
    if "\0" in path or "\n" in path:
        raise UnsafePathError("Remote path must not contain null or newline bytes.")
    stripped = path.strip()
    if not stripped:
        raise UnsafePathError("Remote path must not be empty.")
    if stripped.startswith("-"):
        raise UnsafePathError("Remote path must not start with '-'.")
    segments = stripped.replace("\\", "/").split("/")
    if PARENT_DIR in segments:
        raise UnsafePathError("Remote path must not contain '..' segments.")
    return stripped
