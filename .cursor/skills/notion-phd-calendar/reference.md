# Referencia Notion PhD — Calendario

## IDs canónicos

```text
PhD page_id:              27a2070c3c28801e9a61f6e18db2bcb1
Calendar database_id:     be87b81e046b443aae039b7c8402a67d
Calendar data_source_id:  6286d24b-84d6-4b20-9965-c4619667e8f0
```

## Vistas

| Vista | view_id (sin guiones en URL) |
| --- | --- |
| Calendario | `3c62070c3c2881969e62000c9bd2e376` |
| Próximos | `3c62070c3c2881429172000c054d7003` |

URL de vista: `https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d?v=<view_id>`

## Herramientas MCP

| Operación | Herramienta |
| --- | --- |
| Esquema, contenido, ancestros | `notion-fetch` |
| Listar / filtrar eventos | `notion-query-data-sources` |
| Crear evento | `notion-create-pages` |
| Actualizar evento | `notion-update-page` |
| Buscar en PhD (localizar evento) | `notion-search` + `page_url` del espacio PhD |

## Validar alcance

Tras `notion-fetch` de un evento, `ancestor-path` debe incluir la página PhD o el Calendario PhD bajo PhD.

## Consultar vista «Calendario»

```json
{
  "data": {
    "mode": "view",
    "view_url": "https://app.notion.com/p/be87b81e046b443aae039b7c8402a67d?v=3c62070c3c2881969e62000c9bd2e376"
  }
}
```

## Consultar eventos por SQL

Eventos en un rango de fechas (ejemplo: septiembre 2026):

```json
{
  "data": {
    "data_source_urls": ["collection://6286d24b-84d6-4b20-9965-c4619667e8f0"],
    "query": "SELECT url, \"Evento\", \"Tipo\", \"Ubicación\", \"date:Fecha:start\", \"date:Fecha:end\", \"date:Fecha:is_datetime\" FROM \"collection://6286d24b-84d6-4b20-9965-c4619667e8f0\" WHERE \"date:Fecha:start\" >= ? AND \"date:Fecha:start\" < ? ORDER BY \"date:Fecha:start\" ASC",
    "params": ["2026-09-01", "2026-10-01"]
  }
}
```

Próximos eventos (desde hoy):

```json
{
  "data": {
    "data_source_urls": ["collection://6286d24b-84d6-4b20-9965-c4619667e8f0"],
    "query": "SELECT url, \"Evento\", \"Tipo\", \"date:Fecha:start\" FROM \"collection://6286d24b-84d6-4b20-9965-c4619667e8f0\" WHERE \"date:Fecha:start\" >= ? ORDER BY \"date:Fecha:start\" ASC LIMIT 20",
    "params": ["2026-08-24"]
  }
}
```

Filtrar por tipo:

```json
{
  "data": {
    "data_source_urls": ["collection://6286d24b-84d6-4b20-9965-c4619667e8f0"],
    "query": "SELECT url, \"Evento\", \"date:Fecha:start\" FROM \"collection://6286d24b-84d6-4b20-9965-c4619667e8f0\" WHERE \"Tipo\" = ? ORDER BY \"date:Fecha:start\" ASC",
    "params": ["Reunión"]
  }
}
```

## Crear evento con hora

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "6286d24b-84d6-4b20-9965-c4619667e8f0"
  },
  "pages": [
    {
      "properties": {
        "Evento": "Reunión con director",
        "Tipo": "Reunión",
        "Ubicación": "Despacho 3.14",
        "Descripción": "Revisión avance HOD",
        "date:Fecha:start": "2026-09-02T10:00:00",
        "date:Fecha:is_datetime": 1,
        "Todo el día": "__NO__"
      }
    }
  ]
}
```

## Crear evento de día completo

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "6286d24b-84d6-4b20-9965-c4619667e8f0"
  },
  "pages": [
    {
      "properties": {
        "Evento": "Plazo entrega informe",
        "Tipo": "Plazo",
        "date:Fecha:start": "2026-09-15",
        "date:Fecha:is_datetime": 0,
        "Todo el día": "__YES__"
      }
    }
  ]
}
```

## Crear evento con rango (varios días u horas)

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "6286d24b-84d6-4b20-9965-c4619667e8f0"
  },
  "pages": [
    {
      "properties": {
        "Evento": "Conferencia COSMO",
        "Tipo": "Conferencia",
        "date:Fecha:start": "2026-10-05",
        "date:Fecha:end": "2026-10-07",
        "date:Fecha:is_datetime": 0,
        "Todo el día": "__YES__"
      }
    }
  ]
}
```

## Actualizar fecha de un evento

```json
{
  "page_id": "<event-page-uuid>",
  "command": "update_properties",
  "properties": {
    "date:Fecha:start": "2026-09-03T11:00:00",
    "date:Fecha:is_datetime": 1
  }
}
```

## Formato de propiedades especiales

| Tipo | Formato en `properties` |
| --- | --- |
| date (Fecha) | `date:Fecha:start`, `date:Fecha:end`, `date:Fecha:is_datetime` (0 o 1) |
| checkbox (Todo el día) | `__YES__` / `__NO__` |
| select (Tipo) | Uno de: Reunión, Plazo, Seminario, Conferencia, Clase, Personal, Otro |

## Calendario vs tareas

| Necesidad | Dónde |
| --- | --- |
| Cita en agenda, reunión con hora, seminario, plazo como fecha en calendario | Calendario PhD |
| Trabajo pendiente, backlog, estado de progreso | Registro de tareas (`notion-phd-tasks`) |

Un mismo hito puede existir en ambos sitios solo si el usuario lo pide explícitamente.
