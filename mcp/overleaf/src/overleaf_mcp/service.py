"""High-level Overleaf operations used by MCP tools."""

from collections.abc import Callable

from overleaf_mcp.config import ProjectConfig, Settings
from overleaf_mcp.errors import UnknownProjectError
from overleaf_mcp.git_workspace import GitWorkspace

DEFAULT_WRITE_MESSAGE = "Update {path} via overleaf-mcp"
DEFAULT_DELETE_MESSAGE = "Delete {path} via overleaf-mcp"


class OverleafService:
    """Resolve project aliases and run git-backed file operations."""

    def __init__(
        self,
        settings: Settings,
        remote_url_for: Callable[[str], str] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        settings
            Loaded MCP settings.
        remote_url_for
            Optional factory that maps a project id to a git remote URL.
            Tests use this to point at a local repository.
        """
        self.settings = settings
        self._remote_url_for = remote_url_for

    def list_projects(self) -> list[dict[str, str | bool]]:
        """
        Return configured project aliases.

        Returns
        -------
        list[dict[str, str | bool]]
            Alias, project id and whether the alias is the default.
        """
        rows = []
        for alias, project in self.settings.projects.items():
            rows.append(
                {
                    "alias": alias,
                    "project_id": project.project_id,
                    "default": alias == self.settings.default_alias,
                }
            )
        return rows

    def sync_project(self, project: str | None = None) -> str:
        """
        Clone if needed and pull the latest Overleaf commits.

        Parameters
        ----------
        project
            Project alias. The default project is used when omitted.

        Returns
        -------
        str
            Short status message.
        """
        workspace = self._workspace(project)
        workspace.pull()
        return f"Synced project '{self._resolve(project).alias}'."

    def list_files(self, project: str | None = None) -> list[str]:
        """
        Pull and list tracked files in a project.

        Parameters
        ----------
        project
            Project alias. The default project is used when omitted.

        Returns
        -------
        list[str]
            Relative file paths.
        """
        workspace = self._workspace(project)
        workspace.pull()
        return workspace.list_files()

    def read_file(self, path: str, project: str | None = None) -> str:
        """
        Read a text file from the local clone.

        Parameters
        ----------
        path
            Path relative to the project root.
        project
            Project alias. The default project is used when omitted.

        Returns
        -------
        str
            File contents.
        """
        return self._workspace(project).read_file(path)

    def write_file(
        self,
        path: str,
        content: str,
        project: str | None = None,
        commit_message: str | None = None,
    ) -> str:
        """
        Write a text file and push it to Overleaf.

        Parameters
        ----------
        path
            Path relative to the project root.
        content
            Full file contents.
        project
            Project alias. The default project is used when omitted.
        commit_message
            Optional git commit message.

        Returns
        -------
        str
            Short status message.
        """
        message = commit_message or DEFAULT_WRITE_MESSAGE.format(path=path)
        return self._workspace(project).write_file(path, content, message)

    def delete_file(
        self,
        path: str,
        project: str | None = None,
        commit_message: str | None = None,
    ) -> str:
        """
        Delete a file and push the removal to Overleaf.

        Parameters
        ----------
        path
            Path relative to the project root.
        project
            Project alias. The default project is used when omitted.
        commit_message
            Optional git commit message.

        Returns
        -------
        str
            Short status message.
        """
        message = commit_message or DEFAULT_DELETE_MESSAGE.format(path=path)
        return self._workspace(project).delete_file(path, message)

    def remote_url(self, project_id: str) -> str:
        """
        Build the Git remote URL for a project id.

        Parameters
        ----------
        project_id
            Overleaf project id.

        Returns
        -------
        str
            HTTPS Git URL.
        """
        if self._remote_url_for is not None:
            return self._remote_url_for(project_id)
        return f"https://{self.settings.git_host}/{project_id}"

    def _resolve(self, project: str | None) -> ProjectConfig:
        alias = project or self.settings.default_alias
        try:
            return self.settings.projects[alias]
        except KeyError as exc:
            known = ", ".join(sorted(self.settings.projects))
            raise UnknownProjectError(
                f"Unknown project '{alias}'. Known aliases: {known}."
            ) from exc

    def _workspace(self, project: str | None) -> GitWorkspace:
        resolved = self._resolve(project)
        repo_dir = self.settings.cache_dir / resolved.project_id
        return GitWorkspace(
            repo_dir=repo_dir,
            remote_url=self.remote_url(resolved.project_id),
            git_token=self.settings.git_token,
            cache_dir=self.settings.cache_dir,
        )
