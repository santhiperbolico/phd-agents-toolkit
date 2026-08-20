"""Read-only filesystem and Slurm helpers for Taurus."""

from taurus_mcp.config import Settings
from taurus_mcp.errors import (
    BinaryFileError,
    OutputLimitError,
    ReadLimitError,
    UnsafePathError,
)
from taurus_mcp.paths import validate_remote_path
from taurus_mcp.ssh import CommandRunner, SshClient

MAX_READ_BYTES = 1024 * 1024
MAX_OUTPUT_LINES = 500
MAX_FIND_RESULTS = 200
MAX_GREP_MATCHES = 200

BINARY_FILE_MARKERS = (
    "executable",
    "shared object",
    "ELF",
    "data",
    "archive",
    "compressed",
    "image",
    "audio",
    "video",
    "font",
)


class TaurusService:
    """Read-only operations on the Taurus cluster."""

    def __init__(
        self,
        settings: Settings,
        runner: CommandRunner | None = None,
    ) -> None:
        self.settings = settings
        self._ssh = SshClient(settings, runner=runner)

    def list_dir(self, path: str) -> str:
        """
        List a remote directory with ``ls -la``.

        Parameters
        ----------
        path
            Directory path on Taurus.

        Returns
        -------
        str
            ``ls -la`` output.
        """
        remote_path = validate_remote_path(path)
        output = self._ssh.run("ls", "-la", "--", remote_path)
        return _limit_lines(output, MAX_OUTPUT_LINES)

    def read_file(self, path: str) -> str:
        """
        Read a remote text file with a size cap.

        Parameters
        ----------
        path
            File path on Taurus.

        Returns
        -------
        str
            UTF-8 text content.

        Raises
        ------
        BinaryFileError
            If ``file`` reports a non-text type.
        ReadLimitError
            If the file exceeds ``MAX_READ_BYTES``.
        UnsafePathError
            If the path is unsafe.
        """
        remote_path = validate_remote_path(path)
        file_type = self._ssh.run("file", "--brief", "--", remote_path).strip()
        _reject_binary_file_type(file_type)
        raw = self._ssh.run(
            "head",
            "-c",
            str(MAX_READ_BYTES + 1),
            "--",
            remote_path,
        )
        encoded = raw.encode("utf-8")
        if len(encoded) > MAX_READ_BYTES:
            raise ReadLimitError(
                f"File exceeds read limit of {MAX_READ_BYTES} bytes: {remote_path}"
            )
        if b"\0" in encoded:
            raise BinaryFileError(f"File looks binary (null bytes): {remote_path}")
        return raw

    def find_files(self, path: str, name_pattern: str) -> str:
        """
        Find files by name under a remote directory.

        Parameters
        ----------
        path
            Root directory for the search.
        name_pattern
            Pattern passed to ``find -name`` (for example ``*.log``).

        Returns
        -------
        str
            Newline-separated paths, capped at ``MAX_FIND_RESULTS``.
        """
        remote_path = validate_remote_path(path)
        pattern = _validate_name_pattern(name_pattern)
        output = self._ssh.run(
            "find",
            "--",
            remote_path,
            "-type",
            "f",
            "-name",
            pattern,
        )
        return _limit_result_lines(output, MAX_FIND_RESULTS)

    def grep_files(self, path: str, pattern: str) -> str:
        """
        Recursively grep text under a remote path.

        Parameters
        ----------
        path
            File or directory to search.
        pattern
            Extended regular expression for ``grep -E``.

        Returns
        -------
        str
            Matching lines from ``grep -r -n -E``, capped at ``MAX_GREP_MATCHES``.
        """
        remote_path = validate_remote_path(path)
        grep_pattern = _validate_grep_pattern(pattern)
        output = self._ssh.run(
            "grep",
            "-r",
            "-n",
            "-E",
            "-I",
            "--",
            grep_pattern,
            remote_path,
            allowed_returncodes=frozenset({0, 1}),
        )
        return _limit_result_lines(output, MAX_GREP_MATCHES)

    def squeue_me(self) -> str:
        """
        Return the current user's Slurm queue.

        Returns
        -------
        str
            Output of ``squeue --me``.
        """
        return self._ssh.run("squeue", "--me").rstrip("\n")


def _validate_name_pattern(name_pattern: str) -> str:
    """Return a trimmed find name pattern or raise UnsafePathError."""
    stripped = name_pattern.strip()
    if not stripped:
        raise UnsafePathError("Name pattern must not be empty.")
    if "\0" in stripped:
        raise UnsafePathError("Name pattern must not contain null bytes.")
    return stripped


def _validate_grep_pattern(pattern: str) -> str:
    """Return a trimmed grep pattern or raise UnsafePathError."""
    stripped = pattern.strip()
    if not stripped:
        raise UnsafePathError("Grep pattern must not be empty.")
    if "\0" in stripped:
        raise UnsafePathError("Grep pattern must not contain null bytes.")
    return stripped


def _reject_binary_file_type(file_type: str) -> None:
    """Raise BinaryFileError when file(1) output suggests a non-text file."""
    lowered = file_type.lower()
    if "cannot open" in lowered or "no such file" in lowered:
        return
    if "text" in lowered or "empty" in lowered or "ascii" in lowered:
        return
    for marker in BINARY_FILE_MARKERS:
        if marker.lower() in lowered:
            raise BinaryFileError(f"Refusing to read non-text file: {file_type}")
    if lowered.startswith("directory"):
        raise BinaryFileError(f"Path is a directory, not a file: {file_type}")


def _limit_lines(output: str, max_lines: int) -> str:
    """Return output if it fits, otherwise raise OutputLimitError."""
    lines = output.splitlines()
    if len(lines) <= max_lines:
        return output.rstrip("\n")
    raise OutputLimitError(
        f"Output exceeds {max_lines} lines ({len(lines)} total). " "Narrow the path or search."
    )


def _limit_result_lines(output: str, max_lines: int) -> str:
    """Return capped newline-separated results or raise OutputLimitError."""
    stripped = output.rstrip("\n")
    if not stripped:
        return ""
    lines = stripped.splitlines()
    if len(lines) > max_lines:
        raise OutputLimitError(
            f"Results exceed {max_lines} entries ({len(lines)} total). "
            "Use a narrower path or pattern."
        )
    return stripped
