# AGENTS.md — phd-agents-toolkit

**Propósito:** toolkit compartido de reglas y skills para Vibecoding con Cursor en **proyectos de doctorado** (investigación, análisis, simulaciones, pipelines de datos). No es un repo de producto.

**Última revisión:** 2026-07-02.

---

## Cómo activar este toolkit

1. Incluir `phd-agents-toolkit` en un **workspace multi-root** de Cursor — ver [README.md](../README.md#workspace-en-cursor-multi-root).
2. Trabajar desde ese workspace al usar agentes en repos de investigación.
3. Reglas y skills **específicas de un proyecto** siguen en el `.cursor/` de cada repo.

---

## Qué va aquí vs en cada repo

Este toolkit recoge lo **transversal** de los proyectos de doctorado: convenciones Python, calidad, Git y flujo con agentes. Lo **propio de una línea de investigación** queda en el `.cursor/` (y documentación asociada) de cada repo.

- **Aquí:** reglas y skills reutilizables, sin acoplarlas a un dominio concreto.
- **En cada repo:** contexto del proyecto — metodología, datasets, convenciones de dominio y reglas que solo aplican allí.

Con el workspace multi-root, Cursor combina ambos: el agente ve este toolkit y, al trabajar en un repo concreto, también sus reglas y skills locales.

---

## Idioma

| Artefacto | Idioma |
| --- | --- |
| Respuestas del agente al usuario | **Castellano** |
| Código, comentarios, docstrings | **Inglés** |
| Mensajes de commit y PR | **Inglés** |
| Reglas y skills de este toolkit | **Castellano** |

Detalle → regla `language-conventions`.

---

## Reglas (`.cursor/rules/`)

Cada regla es un fichero `.mdc` con frontmatter (`alwaysApply`, `globs`, etc.). Cursor las carga automáticamente según ese frontmatter.

**Dónde mirar:** `.cursor/rules/` en este repo (y en el `.cursor/` del repo de investigación, si aplica).

**Qué cubren:**

- **Siempre activas:** idioma (agente vs código), principios de diseño (KISS, DRY, YAGNI, etc.).
- **Bajo demanda:** Git (commits, ramas, permisos), secretos y seguridad.
- **Por fichero Python (`**/*.py`):** estilo, naming, estructura, typing, errores/OOP, docstrings.

---

## Skills (`.cursor/skills/`)

Cada skill vive en su carpeta con un `SKILL.md`. Cursor las activa bajo demanda según la tarea.

**Qué cubren:**

- **Código Python:** convenciones al implementar o modificar código.
- **Calidad:** pre-commit, linters, pytest y cobertura.
- **Entorno:** venv y dependencias.
- **Flujo de trabajo:** Git, SDD/TDD, code review.
- **Cluster:** Slurm para scripts Python pesados (`slurm-python-jobs`).
- **Mantenimiento del toolkit:** crear o editar reglas y skills.

---

## Principios para agentes

1. **Contexto mínimo:** abrir el repo de investigación y skills/reglas necesarias.
2. **El repo manda:** `pyproject.toml`, `fail_under`, `max_complexity`, layout de carpetas.
3. **Secretos:** nunca tokens, API keys ni credenciales en respuestas o commits.
4. **Skills locales:** dominio específico (astrofísica, sistemas electorales, etc.) → `.cursor/` del repo además de este toolkit.
5. **Código mergeable:** tras cambios Python, pasar pre-commit/linters en ficheros tocados.
6. **Venv y pip:** no ejecutar creación de `.venv` ni `pip install` en el terminal del agente; comprobar si existe y **dar los comandos al usuario** (skill `venv-and-deps`).
7. **Idioma:** responder en castellano; escribir código y commits en inglés.

---

## Checklist rápido

- ¿Workspace incluye `phd-agents-toolkit`?
- ¿`.venv` existente y activado?
- ¿Pre-commit en verde en el alcance del cambio?
- ¿Tests según el repo?
- ¿Respuestas en castellano y código en inglés?
