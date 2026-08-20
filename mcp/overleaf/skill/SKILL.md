---
name: overleaf-mcp
description: >-
  Usa el servidor MCP Overleaf para listar, leer, escribir o borrar
  ficheros LaTeX en proyectos de Overleaf. Usar cuando el usuario hable
  de Overleaf, papers en Overleaf, git.overleaf.com, o editar .tex/.bib
  remotos en Overleaf.
---

# Overleaf MCP

## Cuándo usar

- El usuario pide leer o editar un proyecto de Overleaf.
- Hay que listar, crear, modificar o borrar `.tex`, `.bib` u otros ficheros del paper en Overleaf.
- El workspace no tiene el proyecto LaTeX en local y vive en Overleaf.

## Cuándo NO usar

- El `.tex` está en un repo git local del workspace: editar esos ficheros, no Overleaf.
- Compilar PDF, gestionar la cuenta Overleaf o generar tokens.
- El servidor MCP `overleaf` no está conectado: indicar al usuario el README de `mcp/overleaf/`.

## Flujo

1. `list_projects` para ver alias. Si hay varios, pregunta cuál usar o toma el default.
2. `list_files` (hace pull) antes de editar, para no pisar cambios de la UI.
3. `read_file` con la ruta relativa (`main.tex`, `chapters/intro.tex`).
4. `write_file` con el **fichero completo** y un `commit_message` claro. Opcional: `delete_file`.
5. `sync_project` si el usuario ha editado en Overleaf desde el último listado.

## Reglas críticas

- Nunca mostrar, loguear ni commitear `OVERLEAF_GIT_TOKEN`.
- Rutas relativas al raíz del proyecto; nunca `..` ni rutas absolutas.
- Solo texto UTF-8; no reescribir binarios (figuras, PDF).
- `write_file` sobrescribe el fichero entero: leer antes, cambiar lo mínimo, devolver el contenido completo.
- Overleaf Git es una feature de pago/institucional; si las tools fallan por autenticación o «repository not found», decirlo y no improvisar APIs no oficiales.

## Salida esperada

- Cambios ya pusheados a Overleaf (salvo «No changes to commit»).
- Rutas y alias usados, sin secretos.
- Si una tool falla, el mensaje de error de git/config, redactado.

## Referencias

- [README.md](../README.md)
