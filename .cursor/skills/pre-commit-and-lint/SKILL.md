---
name: pre-commit-and-lint
description: >-
  Prepara comandos de pre-commit y linters (black, isort, flake8) para que los
  ejecute el usuario. Usar cuando haya que pasar hooks o corregir formato antes
  de commit o PR.
---

# Pre-commit y linters

## Cuándo usar

- Pasar pre-commit antes de commit o PR.
- Corregir errores de black, isort o flake8.
- Instalar o ejecutar hooks por primera vez en un repo.
- El usuario menciona «pre-commit», «linter», «flake8», «formatear código».

## Cuándo NO usar

- Solo ejecutar tests → skill `pytest-and-coverage`.
- Crear venv o instalar requirements → skill `venv-and-deps`.
- Repos sin Python o sin `src/.pre-commit-config.yaml`.

---

## Directorio de trabajo

- **`src/`** del repo de producto (habitual)
- Config en `src/pyproject.toml`, `src/.flake8`, `src/.pre-commit-config.yaml`.
- Desde `src/`, `pre-commit run --all-files` usa `pyproject.toml` del directorio.

## Valores habituales (Black / isort)

Salvo que el `pyproject.toml` del repo diga otra cosa (regla `python-style`):

- **Black:** `line-length = 99`, `target-version = py311`.
- **isort:** `profile = black`, `line_length = 99`.
- **flake8:** `E, W, F, C`; `max_line_length = 99`; `max_complexity` en `.flake8`.

---

## Instalación (una vez por clon)

Si falta venv o dependencias, skill `venv-and-deps`: dar comandos al usuario;
no ejecutar `pip install` desde el agente.

```bash
cd <repo>/src                   # habitual; o cd <repo> si .venv está en raíz
source .venv/bin/activate       # o source ../.venv/bin/activate
pre-commit install
```

---

## Ejecutar hooks

**No ejecutes `pre-commit` en el terminal del agente** (output largo, consume
contexto). Da los comandos al usuario cuando lo pida o haga falta validar; continúa según el resultado que reporte.

### Si se han creado nuevos ficheros deben añadirse al stage

```bash
git add <ficheros_modificados>
```

### Todo el repo (habitual)

```bash
cd <repo>/src
pre-commit run --all-files
```

### Archivos concretos

```bash
cd <repo>/src
pre-commit run --files modulo/fichero.py
```

### Hook individual

```bash
cd <repo>/src
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

---

## Orden típico de fallos

1. **pre-commit-hooks** — espacios finales, EOF, YAML/JSON.
2. **flake8** — estilo y complejidad (`src/.flake8`).
3. **black** — reformatea; puede requerir nuevo stage.
4. **isort** — orden de imports; puede requerir nuevo stage.

Suele bastar **dos ejecuciones** (auto-fix + verificación)

---

## Uso pragmático (tokens)

No repetir esta skill en cada respuesta. Comandos copy-paste desde `src/`;
priorizar `pre-commit run --files …` sobre `--all-files` en alcance acotado.

---

## Pre-commit obligatorio

No ejecutar `pre-commit`, `black`, `isort` ni `flake8` desde el agente (ni a
mano como sustituto). Si no está instalado, dar comandos de «Instalación» al
usuario y esperar confirmación.

---

## Reglas críticas

- **Pre-commit instalado:** requisito previo; no hay atajo manual con linters sueltos.
- **No `# noqa`:** si flake8 falla, corregir el código; no añadir `# noqa` para
  silenciar el hook y pasar CI (ver regla `python-style`).
- No asumir versión global de flake8; la del hook del repo manda.
- No reformatear fuera del alcance del encargo, salvo imperativa necesidad
  (regla `python-style`); salvo que el hook lo exija en ficheros ya tocados.
- `max_complexity` y exclusiones vienen de `.flake8` del repo objetivo.

---

## Tras escribir código Python

Al cerrar una tarea de implementación (skill `python-coding` o SDD):

```bash
cd <repo>/src
pre-commit run --files modulo/fichero.py
```

Desde la raíz git, si hace falta:

```bash
pre-commit run --config src/.pre-commit-config.yaml --files src/modulo/fichero.py
```

---

## Salida esperada

- Comandos listos para copiar (usuario ejecuta en su terminal).
- Si el usuario reporta fallos: error concreto (fichero/línea) y siguiente comando.
- Si hubo auto-fix: indicar re-stage y segunda pasada de pre-commit.
