# MCP Taurus

Servidor MCP en Python (FastMCP) para **consulta de solo lectura** al cluster Taurus desde Cursor, vía SSH. No envía jobs ni modifica ficheros remotos.

## Spec

**Entrada:** rutas remotas legibles por tu usuario SSH, patrones de búsqueda y expresiones regulares.

**Salida:** listados de directorios, contenido de texto (UTF-8, máx. 1 MiB), rutas encontradas, coincidencias de grep o la cola Slurm del usuario.

**Tools:**

1. `list_dir` — `ls -la` en una ruta remota.
2. `read_file` — lee texto con tope de 1 MiB; rechaza binarios obvios.
3. `find_files` — `find … -name` bajo un directorio (máx. 200 resultados).
4. `grep_files` — `grep -r -n -E` recursivo (máx. 200 líneas).
5. `squeue_me` — ejecuta exactamente `squeue --me`.

**Errores:** ruta vacía o con `..`, fichero binario o demasiado grande, salida truncada por límites, fallo SSH.

**Seguridad:** no hay ejecución genérica de comandos; solo binarios allowlist (`ls`, `find`, `grep`, `head`, `file`, `squeue`). Sin escrituras (`sbatch`, `scancel`, `rm`, etc.).

## Requisitos

- Python 3.11 y el binario `ssh` en `PATH`.
- Acceso SSH ya configurado al cluster, por ejemplo en `~/.ssh/config`:

  ```
  Host taurus
      HostName taurus.ft.uam.es
      User tu_usuario
  ```

- Autenticación por clave SSH (sin contraseñas en git ni en `mcp.json`).

## Instalación

Desde la **raíz del toolkit** (el agente no ejecuta `make`/`pip`; hazlo tú):

```bash
sudo apt install python3.11-venv   # una vez, si ensurepip falla
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-mcp
```

Eso instala `~/.local/bin/taurus-tools`, `~/.local/bin/overleaf-tools` y enlaza
las skills `taurus-cluster` y `overleaf-mcp` a `~/.cursor/skills/`.

Para **tests** de este paquete, usa un venv local (en esta máquina `/usr/bin/python` es Python 2; usa `python3.11`):

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/taurus
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -U pip
python3.11 -m pip install -e ".[dev]"
pre-commit install
```

## Configuración en Cursor

Cursor **no** instala paquetes Python dentro de `.cursor/`. El CLI vive en `~/.local/bin/taurus-tools` tras `make install-mcp`.

1. Copia el bloque de `mcp.json.example` (o el combinado `mcp/mcp.json.example`) y **mézclalo** con tus servidores MCP ya configurados. No sustituyas el fichero entero.
2. Ruta habitual: `~/.cursor/mcp.json`.
3. Si Cursor no expande `~`, usa la ruta absoluta `$HOME/.local/bin/taurus-tools`.

Variables:

| Variable | Obligatorio | Significado |
| --- | --- | --- |
| `TAURUS_SSH_HOST` | no | Alias SSH (por defecto `taurus`) |

Ejemplo mínimo en `mcp.json`:

```json
{
  "mcpServers": {
    "taurus": {
      "command": "~/.local/bin/taurus-tools",
      "args": ["mcp"],
      "env": {
        "PATH": "~/.local/bin:/usr/share/cursor/resources/app/resources/helpers:/usr/bin:/bin",
        "TAURUS_SSH_HOST": "taurus"
      }
    }
  }
}
```

Tras guardar `mcp.json`, recarga la ventana de Cursor (**Developer: Reload Window**) y comprueba que el servidor `taurus` aparece en MCP.

## Tests y pre-commit

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/taurus
source .venv/bin/activate
pytest
pre-commit run --all-files
```

Los tests simulan SSH con mocks; no conectan a Taurus.

## Limitaciones (v1)

- Solo lectura: no `sbatch`, `scancel`, `ssh_execute` genérico ni escritura SFTP.
- Sin allowlist de rutas (puedes leer lo que tu usuario SSH pueda leer).
- `read_file` limitado a 1 MiB y ficheros de texto.
- `squeue_me` solo ejecuta `squeue --me` sin flags extra.
- Para **enviar** jobs Slurm sigue la skill `slurm-python-jobs`; este MCP es para inspección remota y monitorización de cola desde el portátil.
