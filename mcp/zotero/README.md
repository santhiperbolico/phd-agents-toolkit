# MCP Zotero (terceros)

Integración con la biblioteca Zotero del usuario desde Cursor mediante el servidor MCP upstream **[54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp)** (PyPI: `zotero-mcp-server`).

Este directorio **no contiene código Python del servidor**: solo documentación y un ejemplo de configuración. El binario lo instala el usuario con `uv`/`uvx`; Cursor solo **registra** el comando a ejecutar.

Skill asociada: `mcp/zotero/skill/SKILL.md` (se enlaza a `~/.cursor/skills/zotero-phd` con `make install-zotero`).

## Spec (alcance PhD)

**Entrada:** consultas sobre papers, metadatos, colecciones, tags, abstracts, anotaciones o BibTeX de la librería Zotero del usuario.

**Salida:** resultados de búsqueda legibles, metadatos, fragmentos de fulltext/anotaciones o export BibTeX según la tool invocada.

**Modo configurado aquí:** lectura local (`ZOTERO_LOCAL=true`). Requiere Zotero desktop en marcha y API local habilitada. **Sin** API key ni escritura en la librería.

**Comportamiento típico (solo lectura):**

1. Buscar ítems por palabra clave, tag, colección o citation key.
2. Obtener metadatos o BibTeX de un ítem.
3. Listar adjuntos, notas y anotaciones PDF.
4. Leer fulltext cuando Zotero lo tenga indexado (Zotero 7+).

**Errores habituales:** Zotero cerrado, API local desactivada, MCP no registrado en Cursor, ruta de datos distinta a la esperada.

## Requisitos

- Python 3.10+ y [`uv`](https://docs.astral.sh/uv/) en el `PATH` (proporciona `uvx`).
- **Zotero 7+** (acceso local a fulltext).
- Zotero desktop **abierto** durante el uso del MCP.
- API local activada: **Ajustes → Avanzado → «Permitir que otras aplicaciones en este equipo se comuniquen con Zotero»** (en Zotero 9 el texto puede variar ligeramente; ver [documentación upstream](https://stevenyuyy.com/zotero-mcp/)).
- Directorio de datos del usuario (habitual): `/home/santhiperbolico/Zotero`. El servidor intenta detectarlo desde el perfil de Zotero; solo hace falta `ZOTERO_DB_PATH` si la base `zotero.sqlite` está en otra ruta.

## Cómo encaja Cursor (importante)

Cursor **no** instala servidores MCP Python dentro de `.cursor/`.

| Qué | Dónde |
| --- | --- |
| Registro del comando que Cursor lanza | `~/.cursor/mcp.json` (o equivalente del cliente) |
| Paquete Python del servidor | Instalado por el usuario con `uvx` o `uv tool` (global, fuera del repo) |
| Este repo | Skill + README + `mcp.json.example` |

No se versiona ni se «vendorea» el paquete upstream en `phd-agents-toolkit`.

## Instalación (ejecutar tú; el agente no corre `pip`/`uv tool install`)

### Opción A — `make install-zotero` (recomendada en este equipo)

No hace falta `uv`. Reutiliza el mismo venv 3.11 que Taurus/Overleaf
(`~/.local/share/phd-agents-mcp/venv`):

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-zotero
~/.local/bin/zotero-mcp --help
```

### Opción B — `uvx` (si instalas uv)

`uv`/`uvx` **no vienen con Ubuntu**. Instalador oficial (evita el snap):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version
uvx zotero-mcp-server --help
```

El paquete PyPI registra el alias **`zotero-mcp-server`** apuntando al mismo entrypoint que **`zotero-mcp`**.

## Configuración en Cursor

1. Copia el fragmento de `mcp.json.example` y **mézclalo** con tus servidores MCP existentes. **No sustituyas** el fichero entero.
2. Ruta habitual: `~/.cursor/mcp.json`.
3. **No** añadas `ZOTERO_API_KEY` ni `ZOTERO_LIBRARY_ID` (solo lectura local).
4. Tras guardar, recarga Cursor (**Developer: Reload Window**) y comprueba que el servidor **`zotero`** aparece conectado.

Si Cursor no encuentra el comando, usa la ruta absoluta `/home/santhiperbolico/.local/bin/zotero-mcp`.

### Variables (modo lectura PhD)

| Variable | Obligatorio | Significado |
| --- | --- | --- |
| `ZOTERO_LOCAL` | sí | `"true"` — API local de Zotero (sin API key) |
| `ZOTERO_DB_PATH` | no | Ruta a `zotero.sqlite` si no está en la ubicación detectada |
| `ZOTERO_MCP_TOOLSETS` | no | Grupos opcionales de tools upstream; por defecto no hace falta tocarlo |

**No configurar** en este flujo: `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (implican modo web/híbrido y escritura).

## Comando exacto elegido para `mcp.json`

Registro recomendado (Opción A, `make install-zotero`):

```json
"command": "~/.local/bin/zotero-mcp",
"args": [],
"env": {
  "PATH": "~/.local/bin:/usr/share/cursor/resources/app/resources/helpers:/usr/bin:/bin",
  "ZOTERO_LOCAL": "true"
}
```

Si Cursor no expande `~`, usa `/home/santhiperbolico/.local/bin/zotero-mcp`.

Alternativa con `uvx`:

```json
"command": "uvx",
"args": ["zotero-mcp-server"],
"env": { "ZOTERO_LOCAL": "true" }
```

Ver `mcp.json.example` completo.

## Limitaciones

- **Solo lectura** con `ZOTERO_LOCAL=true` sin credenciales web: no añadir ítems, editar metadatos, crear colecciones ni borrar entradas desde el agente PhD.
- Zotero desktop debe permanecer abierto; sin API local no hay conexión.
- Fulltext y anotaciones dependen de lo indexado en Zotero; no sustituye un visor PDF externo para documentos no procesados.
- Búsqueda semántica, Scite y otros extras upstream requieren dependencias adicionales (`[semantic]`, `[scite]`, etc.) y configuración extra; **fuera del alcance mínimo** de este toolkit.
- El servidor upstream expone muchas tools; la skill `zotero-phd` limita el uso del agente a **consulta**.

## Referencias upstream

- Repositorio: https://github.com/54yyyu/zotero-mcp
- Documentación: https://stevenyuyy.com/zotero-mcp/
- PyPI: https://pypi.org/project/zotero-mcp-server/
