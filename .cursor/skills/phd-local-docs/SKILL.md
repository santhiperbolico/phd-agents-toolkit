---
name: phd-local-docs
description: >-
  Busca y resume documentación Markdown (README, docs/, notas) en repos PhD
  hermanos bajo la carpeta local de repositorios, aunque no estén en el
  workspace de Cursor. Usar cuando el usuario pregunte por README, docs,
  documentación, notas, cómo funciona un repo PhD, estructura de proyecto o
  convenciones de un repo que no está abierto en el workspace.
---

# Documentación local — repos PhD

El workspace de Cursor suele incluir solo `phd-agents-toolkit` y `Notas-Doctorado`.
El resto de repos de investigación viven como **hermanos** en la misma carpeta
padre y el agente puede no verlos si no busca fuera del workspace.

Usa **Glob**, **Grep** y **Read** con rutas **absolutas** bajo la raíz fija
indicada abajo. No hace falta MCP ni scripts.

## Cuándo usar

- Preguntas sobre **README**, `docs/`, notas `.md` o documentación de un repo PhD.
- «¿Cómo funciona X?», «¿Qué hace el repo Y?», estructura, convenciones o
  pipelines descritos en Markdown.
- El usuario nombra un repo conocido (p. ej. `fnl_matching_error_reduction`,
  `hod_madrid_py`) y **no** está en el workspace actual.
- Comparar documentación entre repos o localizar dónde está explicado un flujo.
- Buscar en `Notas-Doctorado` u otro repo hermano sin abrirlo en el workspace.

## Cuándo NO usar

- **Papers en Overleaf** → MCP/skill `overleaf-mcp`.
- **Bibliografía, Zotero, citas de la librería** → skill `zotero-phd`.
- **Cluster Taurus, logs remotos, `squeue --me` desde el portátil** → skill
  `taurus-cluster`. Enviar jobs (`sbatch`) → skill `slurm-python-jobs`.
- **Editar código de producto** en un repo **ya presente** en el workspace →
  trabajar directamente en ese repo; no hace falta ampliar la búsqueda a hermanos.
- **Tareas, todo, backlog, Notion PhD** → skill `notion-phd-tasks`.
- Volcar repositorios enteros o ficheros enormes sin filtrar.

---

## Raíz de búsqueda

| Recurso | Ruta absoluta |
| --- | --- |
| Carpeta padre de repos PhD | `/home/santhiperbolico/Documentos/Doctorado/repositorios` |

**Regla:** todas las rutas en Glob/Grep/Read deben ser absolutas desde esa raíz
(o incluir el segmento completo hasta el fichero). No asumir que el workspace
contiene el repo objetivo.

### Repos conocidos (hermanos)

| Repo | Uso típico (orientativo) |
| --- | --- |
| `phd-agents-toolkit/notes/` | Notas PhD: reuniones, análisis, reportes, planes Cursor |
| `phd-agents-toolkit/docs/` | Specs SDD y análisis ligados a repos de producto |
| `Notas-Doctorado` | Workspace Cursor (puede apuntar al toolkit + notas) |
| `phd-agents-toolkit` | Reglas, skills, MCP del toolkit |
| `fnl_matching_error_reduction` | Matching / reducción de error FNL |
| `density_field_properties` | Propiedades del campo de densidad |
| `hod_madrid_py` | HOD Madrid (Python) |
| `get_nebular_emission` | Emisión nebular |
| `halo_catalog_mock` | Catálogo mock de halos |
| `HODfit2sim` | Ajuste HOD a simulaciones |
| `analysesim` | Análisis de simulaciones |
| `prep_gne_input` | Preparación de entrada GNE |
| `run_setup` | Setup / arranque de pipelines |

Si el usuario cita otro nombre bajo la misma carpeta padre, buscar igualmente;
la tabla no es exhaustiva.

---

## Flujo operativo

### 0. Acotar la petición

1. Identifica **repo** (si lo hay), **tema** (setup, datos, Slurm descrito en
   docs — solo lectura aquí —, API interna, etc.) y si el fichero podría estar
   en el workspace actual.
2. Si el repo **ya está** en el workspace y la tarea es **editar código**,
   deja de usar esta skill y opera en ese repo.

### 1. Localizar documentación (prioridad)

Buscar en este orden, acotando al repo si se conoce:

1. `{RAIZ}/{repo}/README.md`
2. `{RAIZ}/{repo}/docs/**/*.md`
3. `{RAIZ}/phd-agents-toolkit/notes/**/*.md` (notas personales PhD)
4. `{RAIZ}/{repo}/*.md` en la raíz del repo
5. Si no hay repo claro: `Glob` con `**/README.md`, `**/docs/**/*.md` o
   `phd-agents-toolkit/notes/**/*.md` bajo `{RAIZ}`, luego filtrar con `Grep`.

Sustituye `{RAIZ}` por
`/home/santhiperbolico/Documentos/Doctorado/repositorios`.

**Glob — ejemplo (README de un repo):**

```text
/home/santhiperbolico/Documentos/Doctorado/repositorios/fnl_matching_error_reduction/README.md
```

**Glob — ejemplo (docs de un repo):**

```text
/home/santhiperbolico/Documentos/Doctorado/repositorios/hod_madrid_py/docs/**/*.md
```

**Grep — ejemplo (tema en Markdown, excluyendo ruido):**

- `path`: `/home/santhiperbolico/Documentos/Doctorado/repositorios`
- `glob`: `**/*.md` (o `**/docs/**/*.md` si el tema suena a documentación formal)
- `pattern`: términos clave del usuario (case-insensitive si conviene)

### 2. Leer con criterio

1. `Read` solo los ficheros más relevantes (README primero, luego secciones
   concretas de `docs/`).
2. Si un `.md` es muy largo, lee por trozos (`offset`/`limit`) o usa `Grep`
   dentro del fichero antes de cargarlo entero.
3. Cruza resultados: un README puede remitir a `docs/` o a otro repo hermano.

### 3. Responder

1. Resume en castellano lo esencial para la pregunta del usuario.
2. Cita rutas absolutas a los ficheros usados (formato de cita del agente:
   bloques `startLine:endLine:path` cuando aporte contexto).
3. Indica lagunas («no hay `docs/`», «solo README genérico») en lugar de inventar.

---

## Exclusiones en búsqueda

No indexar ni leer contenido de utilidad dudosa en estas rutas (omitir en Glob/Grep
o acotar el `path` para no entrar en ellas):

| Patrón / carpeta | Motivo |
| --- | --- |
| `.venv/`, `venv/` | Dependencias locales |
| `.git/` | Metadatos Git |
| `__pycache__/` | Bytecode |
| `node_modules/` | Dependencias JS |
| `.pytest_cache/` | Caché de tests |
| Binarios de datos grandes | `.fits`, `.h5`, `.npy`, `.pkl`, etc. |

Prioriza **Markdown** y texto; no sustituyas documentación por lectura masiva
de código salvo que el usuario lo pida explícitamente.

---

## Reglas críticas

- **Rutas absolutas** bajo `/home/santhiperbolico/Documentos/Doctorado/repositorios`;
  no confiar solo en el árbol del workspace.
- **Prioridad README → docs/ → *.md en raíz** antes de ampliar a todo `**/*.md`.
- **No volcar repos:** resumen ejecutivo + citas puntuales; evita pegar ficheros
  enteros.
- **No editar** repos hermanos salvo petición explícita; esta skill orienta la
  **lectura** de documentación.
- **No mezclar** con Slurm en vivo, Notion ni Overleaf; redirige a la skill
  correspondiente si la petición deriva hacia allí.
- **Respuestas al usuario en castellano**; nombres de repos y rutas tal cual en disco.

---

## Salida esperada

Tras cada consulta, entrega:

1. **Respuesta directa** a la pregunta (qué hace el repo, dónde está explicado X,
   pasos de setup documentados, etc.).
2. **Fuentes** — lista breve de rutas absolutas a los `.md` leídos o encontrados.
3. **Citas** — fragmentos concretos (con referencia de líneas) solo cuando
   aporten valor; no más de lo necesario.
4. **Límites** — si la documentación no existe, está desactualizada o solo está
   en código/comentarios, dilo y sugiere el siguiente paso (p. ej. abrir el repo
   en el workspace o preguntar al usuario).

Si la búsqueda no devuelve nada útil, indícalo claramente y enumera qué patrones
y repos se intentaron.
