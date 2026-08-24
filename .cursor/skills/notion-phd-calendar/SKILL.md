---
name: notion-phd-calendar
description: >-
  Consulta, crea y modifica eventos en el Calendario PhD de Notion (reuniones,
  plazos, seminarios, clases, etc.). Usar cuando el usuario hable de calendario,
  agenda, eventos, citas, reuniones programadas, plazos con hora o actividades
  con fecha en Notion; no usar para tareas del Registro de tareas.
---

# Notion PhD — calendario de eventos

Usa el MCP `plugin-notion-workspace-notion`. Opera **solo** en la base **Calendario PhD** bajo el espacio PhD.

## Cuándo usar

- Listar eventos (hoy, esta semana, un mes, un rango de fechas).
- Crear reuniones, plazos, seminarios, clases u otros eventos con fecha.
- Modificar fecha, hora, tipo, ubicación o descripción de un evento.
- Buscar eventos por título, tipo o fecha.

## Cuándo NO usar

- **Tareas** del Registro de tareas → skill `notion-phd-tasks`.
- Contenido fuera del espacio PhD o fuera del Calendario PhD.
- Borrar eventos sin confirmación explícita del usuario.
- Crear eventos «por si acaso» sin petición del usuario.

---

## Recursos fijos

| Recurso | URL |
| --- | --- |
| Espacio PhD | https://app.notion.com/p/27a2070c3c28801e9a61f6e18db2bcb1 |
| Calendario PhD (BD) | https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d |
| Data source calendario | `collection://6286d24b-84d6-4b20-9965-c4619667e8f0` |

**Regla:** cualquier mención de calendario, agenda o eventos con fecha → opera **solo** en Calendario PhD.

---

## Flujo operativo

### 0. Conexión

Si falla el MCP, pide al usuario verificar la conexión Notion en Cursor.

### 1. Leer eventos

1. `notion-fetch` del Calendario PhD si hace falta refrescar el esquema.
2. Consulta con `notion-query-data-sources`:
   - **Vista existente** (`mode: "view"`) para calendario mensual o lista de próximos.
   - **SQL** para filtros ad hoc (rango de fechas, tipo, texto en título).
3. Para detalle de un evento, `notion-fetch` con la URL del evento.
4. Presenta resultados legibles (tabla: evento, fecha/hora, tipo, ubicación, URL). No vuelques JSON crudo.

Vistas útiles:

| Vista | URL |
| --- | --- |
| Calendario (mensual) | https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d?v=3c62070c3c2881969e62000c9bd2e376 |
| Próximos (lista) | https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d?v=3c62070c3c2881429172000c054d7003 |
| Tabla (todas) | https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d |

### 2. Crear evento

1. Extrae **Evento** (título, obligatorio), **Fecha** (obligatoria), y opcionalmente tipo, ubicación, descripción, todo el día, rango horario.
2. `notion-create-pages` con:
   - `parent`: `{ "type": "data_source_id", "data_source_id": "6286d24b-84d6-4b20-9965-c4619667e8f0" }`
   - Propiedades según esquema (título en **Evento**).
3. Confirma con título, fecha, tipo y enlace al evento creado.

Valores por defecto si el usuario no indica lo contrario:

- **Tipo:** `Otro`
- **Todo el día:** `__NO__` (con hora si la da; si solo da día, marcar todo el día)

### 3. Modificar evento

1. `notion-fetch` del evento para ver propiedades actuales.
2. `notion-update-page` con `update_properties` para fecha, tipo, ubicación, descripción o todo el día.
3. `update_content` / `insert_content` solo si el usuario pide notas en el cuerpo de la página.
4. Confirma qué cambió y enlaza el evento.

### 4. Eliminar evento

Solo con confirmación explícita. Notion MCP no expone borrado directo de páginas de forma segura; informa al usuario y sugiere archivar o borrar manualmente en Notion si no hay herramienta disponible.

---

## Esquema del Calendario PhD (resumen)

| Propiedad | Tipo | Notas |
| --- | --- | --- |
| Evento | title | Obligatorio al crear |
| Fecha | date | `date:Fecha:start`, `date:Fecha:end`, `date:Fecha:is_datetime` |
| Tipo | select | `Reunión`, `Plazo`, `Seminario`, `Conferencia`, `Clase`, `Personal`, `Otro` |
| Ubicación | text | Sala, enlace Zoom, etc. |
| Descripción | text | Detalle breve |
| Todo el día | checkbox | `__YES__` / `__NO__` |

Detalle de propiedades, SQL de ejemplo y convenciones MCP → [reference.md](reference.md).

---

## Reglas críticas

- **Eventos siempre en Calendario PhD**; no crear filas de calendario en otras bases.
- **Fetch antes de escribir** en eventos desconocidos.
- **Ediciones mínimas** en contenido del cuerpo.
- **No borrar** sin confirmación explícita.
- **Respuestas al usuario en castellano**; nombres de propiedades Notion tal cual en la BD.
- **Plazos como tarea de trabajo** → Registro de tareas; **plazos como cita en agenda** → Calendario PhD.

---

## Salida esperada

Tras cada operación, resume:

1. Qué se hizo (leer / crear / actualizar).
2. Identificador clave (título o URL).
3. Fecha y cambios relevantes.
4. Enlace Notion cuando exista.

Si no hay resultados, dilo claramente y sugiere ampliar el rango de fechas o el filtro.

---

## Referencias

- [reference.md](reference.md) — esquema completo, herramientas MCP y ejemplos de llamadas
- Skill `notion-phd-tasks` — tareas y pendientes (no eventos de calendario)
