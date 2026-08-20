# MCP Overleaf

Servidor MCP en Python (FastMCP) para **leer y escribir** proyectos de Overleaf desde Cursor. Overleaf no ofrece una API pública de ficheros: el acceso oficial es la [integración Git](https://docs.overleaf.com/integrations-and-add-ons/git-integration-and-github-synchronization/git-integration.md) (plan de pago o licencia institucional).

## Spec

**Entrada:** token Git de Overleaf, alias de proyecto y rutas relativas al raíz del proyecto.

**Salida:** listados de proyectos/ficheros, contenido UTF-8, o un mensaje corto tras push.

**Comportamiento:**

1. `list_projects` — alias configurados.
2. `sync_project` — `git pull` del clon local.
3. `list_files` — pull y lista de ficheros versionados.
4. `read_file` — lee texto UTF-8 del clon (sin pull).
5. `write_file` — pull, escribe el fichero completo, commit y push.
6. `delete_file` — pull, borra, commit y push.

**Errores:** configuración ausente, alias desconocido, ruta fuera del clon, fichero inexistente, git o contenido no UTF-8.

**Edge cases:** proyecto por defecto si se omite `project`; escritura sin cambios no crea commit; el token no se guarda en la URL del remote.

## Requisitos

- Python 3.11 y `git` en `PATH`.
- Cuenta Overleaf con Git habilitado: en el proyecto, **Menu → Integrations → Git**.
- Token: [Account Settings → Git integration authentication tokens](https://www.overleaf.com/user/settings). Usuario Git: `git`. El token es la contraseña.
- Id del proyecto: en la URL `https://www.overleaf.com/project/<id>`.

## Instalación

Desde la **raíz del toolkit** (el agente no ejecuta `make`/`pip`; hazlo tú):

```bash
sudo apt install python3.11-venv   # una vez, si ensurepip falla
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-mcp
```

Eso instala `~/.local/bin/overleaf-tools`, `~/.local/bin/taurus-tools` y
enlaza las skills `overleaf-mcp` y `taurus-cluster` a `~/.cursor/skills/`.

Para **tests** de este paquete:

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/overleaf
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -U pip
python3.11 -m pip install -e ".[dev]"
pre-commit install
```

## Configuración en Cursor

1. Copia el bloque de `mcp.json.example` (o el combinado `mcp/mcp.json.example`) y **mézclalo** con tus servidores MCP ya configurados (no sustituyas el fichero entero si ya tienes Notion, Slack, etc.).
2. Ruta habitual: `~/.cursor/mcp.json`.
3. Pon el token Git. El comando es `~/.local/bin/overleaf-tools` con `"args": ["mcp"]`. No subas el token a git.

Variables:

| Variable | Obligatorio | Significado |
| --- | --- | --- |
| `OVERLEAF_GIT_TOKEN` | sí | Token Git (`olp_…`) |
| `OVERLEAF_PROJECTS` | una de las dos | `alias:id` separados por comas |
| `OVERLEAF_PROJECT_ID` | una de las dos | Un solo proyecto (alias `default`) |
| `OVERLEAF_DEFAULT_PROJECT` | no | Alias por defecto |
| `OVERLEAF_CACHE_DIR` | no | Clones locales (por defecto `~/.cache/overleaf-mcp`) |
| `OVERLEAF_GIT_HOST` | no | Host Git (por defecto `git.overleaf.com`) |

Ejemplo: `OVERLEAF_PROJECTS=thesis:69a4f7cc4eaf13bd56de5b04`.

Tras guardar `mcp.json`, recarga la ventana de Cursor (**Developer: Reload Window**) y comprueba que el servidor `overleaf` aparece en MCP.

## Tests y pre-commit

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/overleaf
source .venv/bin/activate
pytest
pre-commit run --all-files
```

Los tests usan remotes git locales; no llaman a Overleaf.

## Limitaciones

- Git de Overleaf no soporta ramas. El clon usa `main`.
- Un `write_file` sustituye el fichero entero; conviene leer antes y editar con cuidado.
- Mezclar push Git con comentarios o track-changes de la UI de Overleaf puede perder metadatos.
- Rate limits si se hace polling agresivo; este servidor solo habla con Git cuando el agente llama a una tool.
