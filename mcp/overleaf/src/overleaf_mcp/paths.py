"""Path validation for files inside an Overleaf project clone."""

from pathlib import Path

from overleaf_mcp.errors import UnsafePathError

GIT_DIR_NAME = ".git"


def resolve_project_path(repo_dir: Path, relative_path: str) -> Path:
    """
    Resolve a project-relative path and reject escapes outside the clone.

    Parameters
    ----------
    repo_dir
        Root of the local git clone.
    relative_path
        Path relative to the project root, using POSIX separators.

    Returns
    -------
    Path
        Absolute path inside ``repo_dir``.

    Raises
    ------
    UnsafePathError
        If the path is empty, absolute, inside ``.git``, or escapes the clone.
    """
    stripped = relative_path.strip()
    if not stripped:
        raise UnsafePathError("File path must not be empty.")

    candidate = Path(stripped)
    if candidate.is_absolute():
        raise UnsafePathError("Absolute file paths are not allowed.")

    repo_root = repo_dir.resolve()
    resolved = (repo_root / candidate).resolve()
    if not resolved.is_relative_to(repo_root):
        raise UnsafePathError("File path escapes the project directory.")

    relative = resolved.relative_to(repo_root)
    if GIT_DIR_NAME in relative.parts:
        raise UnsafePathError("Paths inside .git are not allowed.")

    return resolved
