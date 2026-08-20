---
name: zotero-phd
description: >-
  Consulta la biblioteca Zotero del usuario (papers, metadatos, abstracts,
  colecciones, anotaciones PDF, BibTeX) en modo lectura vía MCP. Usar cuando
  el usuario hable de papers, artículos, bibliografía, citas, Zotero, PDFs de
  la librería, abstracts, tags o colecciones de referencias.
---

# Zotero PhD — biblioteca en lectura

Usa el MCP **`zotero`** (servidor upstream [zotero-mcp-server](https://github.com/54yyyu/zotero-mcp), PyPI). Antes de cualquier llamada, comprueba que el objetivo es **consultar** la librería, no modificarla.

Instalación y `mcp.json` → [README.md](../README.md).

## Cuándo usar

- Buscar papers, artículos o libros en la librería Zotero del usuario.
- Obtener metadatos, abstract, BibTeX o texto completo de un ítem.
- Listar o explorar **colecciones**, tags o entradas recientes.
- Leer **anotaciones** o notas de un PDF ya indexado en Zotero.
- Resumir, comparar o citar referencias que viven en Zotero (no en un repo git).
- Resolver una clave BetterBibTeX o localizar un DOI en la librería.

## Cuándo NO usar

- **README, docs/ o notas Markdown de repos PhD** → skill `phd-local-docs`.
- **Cluster Taurus, logs remotos, `squeue --me`** → skill `taurus-cluster`.
  Enviar jobs (`sbatch`) → skill `slurm-python-jobs`.
- **Editar LaTeX en Overleaf** → skill `overleaf-mcp`.
- **Tareas, todo, backlog, Notion PhD** → skill `notion-phd-tasks`.
- **Añadir, borrar o modificar ítems** en Zotero (DOI, colecciones, tags, notas nuevas, merge de duplicados). Este flujo PhD es **solo lectura**; si el usuario pide escribir, indica que requiere modo híbrido/API y no está configurado aquí.
- Volcar la librería entera o pegar PDFs completos sin filtrar.

---

## Requisitos de runtime

1. **Zotero desktop abierto** en la máquina del usuario.
2. **API local habilitada:** Zotero → Ajustes → Avanzado → «Permitir que otras aplicaciones en este equipo se comuniquen con Zotero».
3. MCP `zotero` conectado en Cursor (`ZOTERO_LOCAL=true`, sin API key).
4. Librería de datos habitual del usuario: `/home/santhiperbolico/Zotero` (el servidor la detecta; solo usar `ZOTERO_DB_PATH` si el usuario confirma otra ruta).

Si falla la conexión, pide verificar Zotero abierto, API local y el fragmento de `~/.cursor/mcp.json` del README.

---

## Flujo operativo

### 0. Conexión

Usa `GetMcpTools` con el id del servidor (`zotero` o `user-zotero`, según
cómo Cursor prefije los MCP de usuario) para descubrir el esquema antes de
invocar tools. Si el servidor no aparece, remite al README de instalación.

### 1. Acotar la petición

- ¿Buscar por tema, autor, tag o colección? → búsqueda primero.
- ¿Ya hay clave de ítem, citation key o DOI? → ir a metadatos o lookup directo.
- ¿Necesita texto o anotaciones? → metadatos → hijos/adjuntos → fulltext o anotaciones.

### 2. Buscar

Herramientas típicas (nombres pueden llevar prefijo `zotero_`):

| Intención | Tool orientativa |
| --- | --- |
| Búsqueda por palabras | `zotero_search_items` |
| Búsqueda compuesta | `zotero_advanced_search` |
| Por tag | `zotero_search_by_tag` |
| Colecciones | `zotero_get_collections`, `zotero_get_collection_items` |
| Recientes | `zotero_get_recent` |
| Por citation key | `zotero_search_by_citation_key` |

Presenta resultados legibles (título, autores, año, clave, colección/tag relevante). No vuelques JSON crudo salvo petición explícita.

### 3. Leer un ítem

1. `zotero_get_item_metadata` — resumen o BibTeX (`format` según necesidad).
2. `zotero_get_item_children` — adjuntos y notas vinculadas.
3. `zotero_get_item_fulltext` — solo si hace falta el cuerpo (fragmentos razonables).
4. `zotero_get_annotations` / `zotero_get_notes` — highlights y notas del PDF.

### 4. Responder al usuario

- Resume en castellano lo pedido (abstract, hallazgos de anotaciones, lista filtrada, etc.).
- Incluye título, autores, año y clave/citation key cuando existan.
- Para citas LaTeX, ofrece BibTeX obtenido del MCP; no inventes campos.

---

## Reglas críticas

- **Solo lectura:** no llames tools de escritura (`zotero_add_*`, `zotero_update_item`, `zotero_create_*`, `zotero_manage_*`, merge de duplicados, etc.) aunque estén expuestas upstream.
- **No configurar** `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID` ni modo híbrido en ejemplos ni sugerencias de config.
- **Zotero debe estar en marcha**; errores de conexión → checklist del README, no APIs alternativas.
- **Contexto acotado:** preferir metadatos + abstract; fulltext y anotaciones solo del ítem relevante.
- **No mezclar** con docs locales, Overleaf, Notion ni Slurm; redirige a la skill correspondiente.
- **Respuestas al usuario en castellano**; títulos bibliográficos y claves BibTeX tal cual en Zotero.

---

## Salida esperada

Tras cada consulta:

1. Respuesta directa a la pregunta (lista, resumen, cita, comparación breve).
2. Identificadores usados (clave de ítem, citation key, colección).
3. Fragmentos citados solo cuando aporten valor (abstract, anotación concreta).
4. Límites claros si no hay resultados, falta fulltext o el MCP no está conectado.

---

## Referencias

- [README.md](../README.md) — instalación (`make install-zotero`), `mcp.json` y limitaciones
