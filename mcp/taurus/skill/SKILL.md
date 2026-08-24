---
name: taurus-cluster
description: >-
  Inspecciona ficheros, logs y datos en el cluster Taurus y consulta la cola
  Slurm del usuario con el MCP taurus (solo lectura, vía SSH). Usar cuando el
  usuario hable de Taurus, logs remotos, squeue, jobs en el cluster o leer
  datos en taurus.ft.uam.es desde el portátil.
---

# Taurus cluster (MCP)

## Cuándo usar

- Listar directorios, leer logs o ficheros de datos en Taurus.
- Buscar ficheros por nombre o grep en rutas remotas.
- Ver el estado de los jobs del usuario con `squeue --me` **desde el portátil**.
- Inspeccionar salidas de Slurm, checkpoints o resultados ya generados en el cluster.

## Cuándo NO usar

- **Enviar o cancelar jobs** (`sbatch`, `scancel`, `srun` interactivo): usar la skill `slurm-python-jobs` cuando el flujo sea lanzar pipelines con los `.slurm` del repo de producto.
- Editar o borrar ficheros remotos (este MCP es solo lectura).
- Zotero, Overleaf, correo UPM o documentación local del repo de investigación.
- El servidor MCP `taurus` no está conectado: indicar al usuario el README de `mcp/taurus/`.

## Flujo

1. Comprobar que el MCP `taurus` (o `user-taurus`) está activo en Cursor.
2. Usar las tools MCP (no `ssh` ad hoc para escrituras):
   - `list_dir(path)` — contenido de un directorio remoto.
   - `read_file(path)` — texto hasta 1 MiB.
   - `find_files(path, name_pattern)` — p. ej. `*.out`, `slurm-*.log`.
   - `grep_files(path, pattern)` — búsqueda recursiva con regex extendida.
   - `squeue_me()` — cola Slurm del usuario.
3. Si hace falta **enviar** un job, cambiar a `slurm-python-jobs` (repo de producto, mutex de un job activo, `sbatch slurm/...`).

## Reglas críticas

- No ejecutar comandos SSH genéricos desde el agente; usar solo las tools del MCP `taurus`.
- No intentar escribir, borrar ni lanzar jobs a través de este MCP.
- Rutas remotas sin segmentos `..`; preferir rutas absolutas bajo `$HOME` del usuario en Taurus.
- `read_file` es para texto; no forzar lectura de binarios grandes.
- La autenticación usa la clave SSH del usuario (`Host taurus` en `~/.ssh/config`); no pedir ni guardar contraseñas en el repo.

## Relación con otras skills

| Necesidad | Skill / artefacto |
| --- | --- |
| Leer logs, datos, grep, `squeue --me` desde el portátil | **taurus-cluster** (este MCP) |
| Enviar pipelines pesados con `sbatch` | **slurm-python-jobs** |
| Editar LaTeX en Overleaf | **overleaf-mcp** |

## Referencias

- [README.md](../README.md)
- Skill `slurm-python-jobs` — envío de jobs cuando ya estás en el flujo del repo de producto
