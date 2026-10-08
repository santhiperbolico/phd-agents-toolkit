"""FastMCP server exposing PhD documentation search."""

from typing import Any

from fastmcp import FastMCP

from phd_docs.config import build_settings, configure_embedding_runtime
from phd_docs.container import build_query_service

FIND_TOOL_DESCRIPTION = (
    "Search indexed PhD notes, specs, and Zotero PDFs. Use this tool first "
    "when the user asks about past analyses, meeting notes, research plans, "
    "paper content, or documented PhD workflows. The query parameter should "
    "be natural language."
)

mcp = FastMCP(
    name="phd-docs",
    instructions=(
        "Semantic search over PhD notes (notes/), specs (docs/), and the "
        "local Zotero library. Call find_phd_docs before grepping large "
        "Markdown trees when the question is conceptual or bibliographic."
    ),
)


@mcp.tool(description=FIND_TOOL_DESCRIPTION)
def find_phd_docs(query: str, n_results: int = 5) -> list[dict[str, Any]]:
    """
    Search the indexed PhD documentation corpus.

    Parameters
    ----------
    query : str
        Natural-language query.
    n_results : int, optional
        Maximum number of matches to return.

    Returns
    -------
    list[dict[str, Any]]
        Ranked matches serialized to the public schema.
    """
    service = build_query_service(build_settings())
    matches = service.query(query, n_results=n_results)
    return [match.to_dict() for match in matches]


def main() -> None:
    """Run the MCP server over stdio transport."""
    configure_embedding_runtime()
    mcp.run()
