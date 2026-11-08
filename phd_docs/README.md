# phd-docs

RAG index for PhD notes, specs, and the local Zotero PDF library.

## Sources

Configured in `docs/phd_docs.json` at the toolkit root:

- `phd-agents-toolkit/notes/**/*.md`
- `phd-agents-toolkit/docs/**/*.md`
- All PDF attachments in the local Zotero data directory

Optional overrides: copy `docs/phd_docs.local.example.json` to
`docs/phd_docs.local.json` (gitignored).

## Install

Requires the `claudia-docs` package from `claudia_devenv`:

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-phd-docs
```

## Usage

```bash
phd-docs look
phd-docs sync
phd-docs query "haloscope mass calibration"
phd-docs sync --full
```

Index data lives in `~/.phd-docs/` by default.

## Environment

| Variable | Default | Meaning |
| --- | --- | --- |
| `PHD_TOOLKIT_ROOT` | auto-detected | Path to `phd-agents-toolkit` |
| `PHD_DOCS_HOME` | `~/.phd-docs` | ChromaDB and sync state |
| `PHD_DOCS_EMBEDDING_DEVICE` | `cpu` | Torch device for embeddings (`cpu` recommended on laptops with small GPU) |
| `CLAUDIA_DOCS_COLLECTION` | `phd_docs` | Chroma collection name |

## MCP

After `make install-phd-docs`, merge `mcp/phd-docs/mcp.json.example` into
`~/.cursor/mcp.json` and reload Cursor. Tool: `find_phd_docs`.
