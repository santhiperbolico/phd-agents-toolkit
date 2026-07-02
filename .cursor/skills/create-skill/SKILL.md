---
name: create-skill
description: >-
  Crea skills de Cursor (.cursor/skills/*/SKILL.md) bien estructurados, con
  carga progresiva y activación selectiva. Usar cuando el usuario pida crear,
  escribir o diseñar una skill, pregunte sobre estructura de SKILL.md, o
  necesite decidir si algo debe ser skill, regla o AGENTS.md.
---

# Crear Skills de Cursor

## Cuándo usar

- Crear, escribir o diseñar una skill.
- Decidir skill vs regla vs AGENTS.md.
- Revisar estructura de una skill existente.

## Cuándo NO usar

- Normas globales siempre activas → **regla**.
- Documentación pasiva sin activación → `.md` de referencia.

---

## Paso 0 — Tipo de artefacto

Ver [taxonomia.md](taxonomia.md).

| Necesidad | Artefacto |
| --- | --- |
| Norma fija siempre | **Regla** |
| Capacidad puntual | **SKILL.md** |
| Normas generales del repo | **AGENTS.md** del repo |

---

## Paso 1 — Requisitos

1. Tarea concreta que resuelve.
2. Señales de activación (keywords, tipos de petición).
3. Exclusiones (cuándo NO usar).
4. Ubicación según criterio toolkit vs repo (ver abajo).

---

## Ubicación (toolkit vs repo de producto)

**Criterio:**

- **phd-agents-toolkit:** flujos y capacidades transversales de proyectos PhD — reutilizables en varios repos, sin acoplar a dominio concreto.
- **Repo de producto:** contexto propio — arquitectura, specs, convenciones de negocio; cualquier skill que solo aplique a ese servicio.

Si encaja en ambos lados, priorizar el repo de producto (menos acoplamiento en el toolkit compartido).

**Rutas:**

- Común PhD → `phd-agents-toolkit/.cursor/skills/<nombre>/`
- Solo un repo → `<repo>/.cursor/skills/<nombre>/` o `<repo>/.agents/skills/` si el equipo usa Antigravity

No crear skills en `~/.cursor/skills-cursor/` (reservado a Cursor).

---

## Paso 2 — Tres capas

| Capa | Contenido |
| --- | --- |
| Activación | Cuándo usar / NO usar |
| Operativo | Flujo, reglas críticas, salida esperada |
| Profundización | `patterns.md`, `examples.md` (enlace desde SKILL.md) |

SKILL.md solo capas 1 y 2; **< 500 líneas** (ideal < 300).

---

## Frontmatter

```yaml
---
name: nombre-kebab-case
description: >-
  Qué hace (tercera persona). Usar cuando [triggers concretos].
---
```

---

## Estructura de directorio

```
nombre-skill/
├── SKILL.md
├── patterns.md      # opcional
└── examples.md      # opcional
```

---

## Checklist

- [ ] `name` kebab-case, ≤ 64 caracteres
- [ ] `description` con QUÉ + CUÁNDO
- [ ] Secciones «Cuándo usar» y «Cuándo NO usar»
- [ ] Referencias un solo nivel de profundidad

## Referencias

- [taxonomia.md](taxonomia.md)
- [plantilla.md](plantilla.md)
