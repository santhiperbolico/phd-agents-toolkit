# Referencia Notion PhD — MCP y ejemplos

## IDs canónicos

```text
PhD page_id:           27a2070c3c28801e9a61f6e18db2bcb1
Tasks database_id:     2cd2070c3c288071a0bceb696238afe6
Tasks data_source_id:  2cd2070c-3c28-806c-acca-000bee6374ed
Default task template: 2cd2070c-3c28-8097-9a7c-f93d2ea2b922
```

## Herramientas MCP (servidor `plugin-notion-workspace-notion`)

| Operación | Herramienta |
| --- | --- |
| Esquema, contenido, ancestros | `notion-fetch` |
| Buscar en PhD | `notion-search` + `page_url` del espacio PhD |
| Listar / filtrar tareas | `notion-query-data-sources` |
| Crear tarea o página | `notion-create-pages` |
| Actualizar tarea o página | `notion-update-page` |
| Comentarios | `notion-get-comments`, `notion-create-comment` |
| Resolver usuarios (Responsable) | `notion-get-users` |

Antes de escribir propiedades de BD, lee el esquema con `notion-fetch` del data source o de la BD.

## Validar alcance PhD

Tras `notion-fetch` de una página candidata, el bloque `ancestor-path` debe incluir:

```xml
<ancestor-...-page url="https://app.notion.com/p/27a2070c3c28801e9a61f6e18db2bcb1" title="PhD"/>
```

La propia página PhD tiene `ancestor-path` vacío; también es válida.

## Consultar tareas por SQL

```json
{
  "data": {
    "data_source_urls": ["collection://2cd2070c-3c28-806c-acca-000bee6374ed"],
    "query": "SELECT url, \"Nombre de la tarea\", \"Estado\", \"Prioridad\", \"date:Plazo:start\" FROM \"collection://2cd2070c-3c28-806c-acca-000bee6374ed\" WHERE \"Estado\" = ? ORDER BY \"date:Plazo:start\" ASC LIMIT 20",
    "params": ["En progreso"]
  }
}
```

## Consultar vista «Por estado»

```json
{
  "data": {
    "mode": "view",
    "view_url": "https://app.notion.com/p/2cd2070c3c288071a0bceb696238afe6?v=2cd2070c3c288086ad25000c600fa8d3"
  }
}
```

## Crear tarea

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "2cd2070c-3c28-806c-acca-000bee6374ed"
  },
  "pages": [
    {
      "template_id": "2cd2070c-3c28-8097-9a7c-f93d2ea2b922",
      "properties": {
        "Nombre de la tarea": "Revisar pipeline HOD",
        "Descripción": "Validar salidas del fit con datos mock",
        "Estado": "Sin empezar",
        "Prioridad": "Alta",
        "date:Plazo:start": "2026-09-15",
        "date:Plazo:is_datetime": 0
      }
    }
  ]
}
```

## Actualizar estado de tarea

```json
{
  "page_id": "<task-page-uuid>",
  "command": "update_properties",
  "properties": {
    "Estado": "En progreso"
  }
}
```

## Buscar dentro del espacio PhD (no tareas)

```json
{
  "query": "HOD machine learning",
  "page_url": "https://app.notion.com/p/27a2070c3c28801e9a61f6e18db2bcb1",
  "page_size": 10
}
```

## Formato de propiedades especiales

| Tipo | Formato en `properties` |
| --- | --- |
| date (Plazo) | `date:Plazo:start`, `date:Plazo:is_datetime` (0 o 1) |
| url (Jira Task, GitHub Issue) | URL completa de la issue |
| checkbox | `__YES__` / `__NO__` |
| person (Responsable) | JSON array de user IDs |

Para Markdown de contenido, consulta `notion-fetch` con `id: "notion://docs/enhanced-markdown-spec"`.

## Otros recursos bajo PhD (solo lectura contextual)

El espacio PhD incluye bases como Navigation y Courses. **No** uses esas bases para tareas; el Registro de tareas cuelga de «Task Report» dentro del mismo árbol PhD.
