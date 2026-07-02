# Taxonomía: Skill vs Regla vs AGENTS.md

## Tabla de decisión

| Pregunta | Sí → | No → |
| --- | --- | --- |
| ¿Norma fija que aplica SIEMPRE? | **Regla** | Siguiente |
| ¿Norma según contexto de archivos? | **Regla** (globs) | Siguiente |
| ¿Capacidad puntual bajo demanda? | **SKILL.md** | Siguiente |
| ¿Instrucciones generales del repo? | **AGENTS.md** | **Otro .md** |

## Comparativa

| Aspecto | Regla | SKILL.md | AGENTS.md |
| --- | --- | --- | --- |
| Carga | Estática | Progresiva | Manual / índice |
| Tokens | Siempre o por glob | Solo si se activa | Cuando se lee |
| Ubicación típica | `.cursor/rules/*.mdc` | `.cursor/skills/*/SKILL.md` | `.cursor/AGENTS.md` |

## Errores comunes

- Normas globales dentro de una skill → mover a regla.
- Capacidad puntual en AGENTS.md → extraer a skill.
- Skill genérica («backend») → estrechar alcance.

## Combinar regla + skill

- **Regla:** guardrail («commits en inglés», «respuestas en castellano»).
- **Skill:** how-to («cómo ejecutar pre-commit en este layout»).
