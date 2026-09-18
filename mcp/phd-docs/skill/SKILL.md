---
name: phd-rag-docs
description: >-
  Búsqueda semántica RAG sobre notas PhD, specs en docs/ y PDFs indexados de
  Zotero mediante el MCP phd-docs. Usar cuando el usuario pregunte por análisis
  previos, reuniones, planes Cursor, papers de la biblioteca o contexto
  documentado del doctorado. Preferir find_phd_docs antes de volcar notes/ o
  Zotero manualmente.
---

# Documentación PhD con RAG

Usa el MCP **`phd-docs`** y la tool **`find_phd_docs`**.

## Cuándo usar

- Preguntas conceptuales sobre investigación ya documentada en `notes/` o `docs/`.
- «¿Qué análisis hice sobre X?», «¿Qué papers tengo sobre Y?», «resume mis notas de haloscope».
- Buscar contexto en PDFs de Zotero ya indexados (contenido, abstract, anotaciones).
- Comparar ideas entre notas personales y bibliografía indexada.

## Cuándo NO usar

- **BibTeX, metadatos puntuales o anotaciones en vivo** de un ítem concreto → skill `zotero-phd`.
- **Fichero Markdown exacto por nombre** cuando el índice puede estar desactualizado → skill `phd-local-docs` (Glob/Grep).
- **Overleaf, Taurus, Notion, correo UPM** → skills correspondientes.

## Flujo

1. Comprueba que el MCP `phd-docs` está conectado.
2. Llama **`find_phd_docs`** con la pregunta en lenguaje natural.
3. Resume en castellano citando `title`, `path` y `source_type` de los metadatos.
4. Si no hay resultados útiles, indica ejecutar `make sync-phd-docs` y usa `phd-local-docs` como fallback.

## Mantenimiento del índice

Tras cambios en `notes/`, `docs/` o nuevos PDFs en Zotero:

```bash
make sync-phd-docs
```

Primera sync o cambio de modelo: puede tardar varios minutos.

## Skills relacionadas

| Skill | Para qué |
| --- | --- |
| `phd-local-docs` | Lectura léxica de Markdown fuera del índice |
| `zotero-phd` | Consulta directa a Zotero (BibTeX, ítem concreto) |
| `roger` | Asesor científico con contexto del doctorado |
