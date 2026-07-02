---
name: create-rule
description: >-
  Crea reglas de Cursor (.cursor/rules/*.mdc) con frontmatter correcto y
  alcance preciso. Usar cuando el usuario pida crear, escribir o modificar
  una regla, pregunte sobre .cursor/rules/, alwaysApply, globs, o
  convenciones persistentes del agente.
---

# Crear Reglas de Cursor

## Cuándo usar

- Crear, escribir o modificar una regla `.mdc`.
- Definir estándares persistentes para el agente.
- Preguntas sobre `alwaysApply` o `globs`.

## Cuándo NO usar

- Capacidad puntual bajo demanda → **skill**.
- Documentación pasiva → `.md` en `.cursor/` o README.
- Normas portables a cualquier IDE → **AGENTS.md** del repo de producto.

---

## Modos de aplicación

| Modo | Frontmatter |
| --- | --- |
| Siempre | `alwaysApply: true` (sin globs) |
| Por archivo | `globs: **/*.py`, `alwaysApply: false` |
| Inteligente | `alwaysApply: false` sin globs; buena `description` |

---

## Formato .mdc

```markdown
---
description: Frase corta
globs: **/*.py
alwaysApply: false
---

# Título

Instrucciones accionables...
```

---

## Principios

- **< 50 líneas** de contenido por regla.
- **Una preocupación** por archivo.
- **Accionable**, con ejemplos bueno/malo si ayuda.
- No duplicar skills.

---

## Ubicación (toolkit vs repo de producto)

**Criterio:**

- **phd-agents-toolkit:** convenciones transversales de proyectos de doctorado — reutilizables en varios repos, sin acoplar a dominio concreto.
- **Repo de producto:** contexto propio — arquitectura, specs, convenciones de negocio; cualquier regla que solo aplique a ese servicio.

Si encaja en ambos lados, priorizar el repo de producto (menos acoplamiento en el toolkit compartido).

**Rutas:**

- Común → `phd-agents-toolkit/.cursor/rules/`
- Solo un producto → `<repo>/.cursor/rules/`

---

## Checklist

- [ ] `.mdc` en `.cursor/rules/`
- [ ] `description` y `alwaysApply` presentes
- [ ] No `alwaysApply: true` con `globs`
- [ ] Nombre kebab-case (`python-error-handling.mdc`)

## Referencias

- Skill `create-skill` y [taxonomia.md](../create-skill/taxonomia.md)
