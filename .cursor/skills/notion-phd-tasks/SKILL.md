---
name: notion-phd-tasks
description: >-
  Lee, crea y modifica tareas en el Registro de tareas de Notion del PhD, y
  accede al resto del espacio PhD con alcance restringido. Usar siempre que el
  usuario hable de tareas, todo, pendientes, backlog, estado de trabajo o
  gestión en Notion; también al leer o editar páginas del espacio PhD que no
  sean tareas.
---

# Notion PhD — tareas y espacio de trabajo

Usa el MCP `plugin-notion-workspace-notion`. Antes de crear o modificar, comprueba que el objetivo cae dentro del alcance permitido (ver abajo).

## Cuándo usar

- Listar, buscar, crear, actualizar o cerrar **tareas**.
- Consultar estado, plazo, prioridad o responsable de una tarea.
- Registrar progreso o notas en una tarea concreta.
- Leer o editar **páginas del espacio PhD** que no sean tareas (notas, cursos, navegación, etc.).

## Cuándo NO usar

- Contenido fuera del espacio PhD y fuera del Registro de tareas.
- Operaciones que el usuario no haya pedido explícitamente (no crear tareas «por si acaso»).
- Cambios masivos o borrado de páginas sin confirmación del usuario.

---

## Alcance y restricciones

| Contexto | Lectura | Creación / edición |
| --- | --- | --- |
| **Tareas** | Registro de tareas | Registro de tareas |
| **Resto de Notion PhD** | Páginas bajo el espacio PhD | Solo bajo el espacio PhD |

### Recursos fijos

| Recurso | URL |
| --- | --- |
| Espacio PhD | https://app.notion.com/p/27a2070c3c28801e9a61f6e18db2bcb1 |
| Registro de tareas (BD) | https://app.notion.com/p/2cd2070c3c288071a0bceb696238afe6 |
| Data source tareas | `collection://2cd2070c-3c28-806c-acca-000bee6374ed` |

**Regla de tareas:** cualquier mención de tareas, pendientes, todo o backlog → opera **solo** en el Registro de tareas.

**Regla fuera de tareas:** limita búsqueda, lectura y escritura al espacio PhD. Antes de modificar una página, haz `notion-fetch` y verifica que aparece en `ancestor-path` la página PhD (URL anterior). Si no pertenece al espacio, **no modifiques**; informa al usuario.

---

## Flujo operativo

### 0. Conexión

Si falla el MCP, pide al usuario verificar la conexión Notion en Cursor. Opcional: `notion-fetch` con `id: "self"` para confirmar workspace y usuario.

### 1. Identificar intención

- ¿Es sobre **tareas**? → continúa con la sección «Tareas».
- ¿Es otra cosa del PhD? → continúa con «Contenido PhD (no tareas)».

### 2. Tareas — leer

1. `notion-fetch` del Registro de tareas si hace falta refrescar el esquema.
2. Consulta con `notion-query-data-sources`:
   - **Vista existente** (`mode: "view"`) cuando el usuario pida un tablero o vista concreta.
   - **SQL** para filtros ad hoc (estado, plazo, prioridad, texto en título).
3. Para detalle de una fila, `notion-fetch` con la URL de la tarea.
4. Presenta resultados legibles (tabla resumida: nombre, estado, plazo, prioridad, URL). No vuelques JSON crudo.

Vistas útiles del Registro de tareas:

| Vista | URL |
| --- | --- |
| Todas las tareas | https://app.notion.com/p/2cd2070c3c288071a0bceb696238afe6?v=2cd2070c3c2888026b253000c5c52c8d1 |
| Por estado (board) | https://app.notion.com/p/2cd2070c3c288071a0bceb696238afe6?v=2cd2070c3c288086ad25000c600fa8d3 |
| Lista de tareas | https://app.notion.com/p/2cd2070c3c288071a0bceb696238afe6?v=2cd2070c3c2888024a44d000c46619e99 |

### 3. Tareas — crear

1. Extrae título (obligatorio), descripción, estado, plazo, prioridad, responsable, enlace Jira si aplica.
2. `notion-create-pages` con:
   - `parent`: `{ "type": "data_source_id", "data_source_id": "2cd2070c-3c28-806c-acca-000bee6374ed" }`
   - Propiedades según esquema (título en **Nombre de la tarea**).
   - Plantilla por defecto opcional: `template_id: "2cd2070c-3c28-8097-9a7c-f93d2ea2b922"` (`Nuevo/a tarea`).
3. Confirma con título, propiedades clave y enlace a la tarea creada.

Valores por defecto razonables si el usuario no indica lo contrario:

- **Estado:** `Sin empezar`
- **Prioridad:** `Medio`

### 4. Tareas — modificar

1. `notion-fetch` de la tarea para ver propiedades y contenido actuales.
2. `notion-update-page`:
   - `update_properties` para estado, plazo, prioridad, descripción, responsable, Jira Task.
   - `update_content` / `insert_content` para notas en el cuerpo (edición mínima; evita `replace_content` salvo petición explícita).
3. Al marcar trabajo en curso: **Estado** → `En progreso`. Al cerrar: **Estado** → `Listo`.
4. Confirma qué cambió y enlaza la tarea.

### 5. Contenido PhD (no tareas)

1. `notion-search` con `page_url` del espacio PhD para acotar la búsqueda.
2. `notion-fetch` del resultado antes de editar; valida `ancestor-path`.
3. Crear páginas hijas con `notion-create-pages` y `parent.page_id` dentro del árbol PhD.
4. Editar con `notion-update-page` (mismos comandos que en tareas, pero solo si la página pertenece al espacio PhD).

---

## Esquema del Registro de tareas (resumen)

| Propiedad | Tipo | Notas |
| --- | --- | --- |
| Nombre de la tarea | title | Obligatorio al crear |
| Descripción | text | |
| Estado | status | `Sin empezar`, `On Hold`, `En progreso`, `To Review`, `Listo` |
| Plazo | date | Usar `date:Plazo:start` y `date:Plazo:is_datetime` |
| Prioridad | select | `Alta`, `Medio`, `Baja` |
| Responsable | person | IDs de usuario vía `notion-get-users` |
| Jira Task | url | |

Detalle de propiedades, SQL de ejemplo y convenciones MCP → [reference.md](reference.md).

---

## Reglas críticas

- **Tareas siempre en el Registro de tareas**; no crear filas de tarea en otras bases del PhD.
- **Fuera de tareas, solo espacio PhD**; rechaza lectura/escritura fuera de ese árbol.
- **Fetch antes de escribir** en bases de datos o páginas desconocidas.
- **Ediciones mínimas** en contenido (`update_content` > `replace_content`).
- **No borrar** páginas o filas sin confirmación explícita del usuario.
- **Respuestas al usuario en castellano**; nombres de propiedades Notion tal cual en la BD.

---

## Salida esperada

Tras cada operación, resume:

1. Qué se hizo (leer / crear / actualizar).
2. Identificador clave (título o URL).
3. Cambios relevantes (estado, plazo, etc.).
4. Enlace Notion cuando exista.

Si no hay resultados o el alcance no es válido, dilo claramente y sugiere el filtro o permiso que falta.

---

## Referencias

- [reference.md](reference.md) — esquema completo, herramientas MCP y ejemplos de llamadas
