---
name: python-coding
description: >-
  Escribe o modifica código Python en repos de investigación siguiendo
  convenciones del repo (estructura, nombres, typing, OOP) y dejándolo listo
  para pre-commit. Usar al implementar features, módulos, pipelines, helpers o
  refactor. Código y docstrings en inglés; respuestas al usuario en castellano.
---

# Codificación Python (proyectos PhD)

## Cuándo usar

- Implementar o modificar código Python en un repo de investigación.
- Crear módulos, clients, pipelines, utilidades o excepciones de dominio.
- El usuario pide código que cumpla estilo del proyecto o pase linters.

## Cuándo NO usar

- Solo ejecutar tests → `pytest-and-coverage`.
- Solo hooks o formato → `pre-commit-and-lint`.
- Solo venv o requirements → `venv-and-deps`.

---

## Flujo recomendado

1. **Contexto del repo:** leer `pyproject.toml`, `.flake8`, CI (`.github/workflows/`) y si existe `.cursor/AGENTS.md` del repo. Venv/deps: skill `venv-and-deps`.
2. **Ubicación:** colocar el código donde ya vivan módulos similares (ver regla `python-structure`).
3. **Implementar** siguiendo reglas activas por `**/*.py` y `language-conventions` (código en **inglés**):
   - `python-naming`, `python-structure`, `python-typing`
   - `python-errors-and-oop`, `python-docstrings`, `python-style`
4. **Calidad:** skill `pre-commit-and-lint` sobre los ficheros tocados.
5. **Tests:** si hay lógica nueva, skill `pytest-and-coverage`.

---

## Reglas críticas (resumen)

| Tema | Regla |
| --- | --- |
| Idioma | Código, comentarios y docstrings en **inglés** |
| Formato | Black 99, isort profile black, py311 (si el repo lo define) |
| Lint | flake8 E,W,F,C; `max_complexity` del repo |
| Nombres | snake_case funciones/módulos; PascalCase clases; `test_*` |
| Typing | Firmas públicas; no mezclar estilos legacy/modernos en un módulo |
| Docstrings | NumPy en API pública; **inglés** |
| Diseño | Principios pragmáticos (regla `python-errors-and-oop`); prioridad al código vecino |

**La configuración del repo manda** sobre este toolkit.

---

## Checklist antes de dar por hecho

- [ ] Ficheros solo en el alcance del encargo (sin reformateo masivo).
- [ ] Código y docstrings en inglés.
- [ ] Imports ordenados y sin unused (isort/flake8).
- [ ] Complejidad ciclomática dentro del límite del repo.
- [ ] Tests añadidos/actualizados si aplica.
- [ ] `pre-commit` en verde.

---

## Profundización

- Patrones y ejemplos: [patterns.md](patterns.md)
