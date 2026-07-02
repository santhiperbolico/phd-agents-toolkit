---
name: code-review
description: >-
  Revisa cambios de código (PR, rama, parche) priorizando corrección, riesgos
  y mantenibilidad. Usar cuando el usuario pida revisar un PR, examinar
  cambios de código, hacer code review, o evaluar una rama o parche.
---

# Revisión de código

## Cuándo usar

- El usuario pide revisar un PR, rama o parche.
- Evaluar calidad, seguridad o mantenibilidad de cambios.
- Se menciona «code review», «revisar cambios», «revisar PR».

## Cuándo NO usar

- Implementar código nuevo.
- Operaciones Git (commit, push) → skill `git-workflow`.

---

## Principios

1. **Severidad:** bloqueantes vs mejoras opcionales.
2. **Evidencia:** atarse al diff o código leído.
3. **Acción:** observaciones verificables.
4. **Contexto mínimo:** solo ficheros tocados y dependencias directas.

---

## Formato de salida

1. **Resumen** (1-3 frases).
2. **Hallazgos:**
   - **Crítico** — antes de merge.
   - **Importante** — debería corregirse.
   - **Opcional** — mejora sugerida.
3. Si no hay problemas relevantes, decirlo explícitamente.

---

## Checklist rápido

- [ ] **Corrección:** lógica, tests y edge cases cubiertos o justificados en el diff.
- [ ] **Diseño:** coherente con el repo y regla `python-errors-and-oop`. Señalar
  desvíos de SOLID, KISS, YAGNI, DRY, etc. solo si afectan al cambio concreto;
  clasificarlos como *Importante* u *Opcional*, nunca pedir refactor masivo ajeno
  al PR.
- [ ] **Secretos:** ningún valor real (tokens, contraseñas, claves) en el diff a no ser que se haya acordado en la regla `secrets-and-safety`.
