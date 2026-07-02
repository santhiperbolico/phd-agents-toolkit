---
name: spec-driven-dev
description: >-
  Desarrollar funcionalidades siguiendo Spec-Driven Development con TDD
  integrado, optimizado para Python. Usar cuando el usuario pida desarrollo
  guiado por especificación, TDD, desarrollo con tests primero, o pida
  implementar una feature completa con cobertura de tests.
---

# Desarrollo guiado por especificación (SDD + TDD)

## Cuándo usar

- El usuario pide implementar una feature "con tests", "con TDD" o "spec-first".
- Se proporciona una especificación (markdown, requisitos, contrato de API) y se pide implementarla.
- El usuario menciona "spec-driven", "SDD", "TDD", "test-first", "red-green-refactor".
- Hay que crear un módulo o servicio nuevo desde cero con cobertura garantizada.

## Cuándo NO usar

- Bugs puntuales con fix obvio.
- Cambios de configuración o infra sin lógica testeable.
- Code review → skill `code-review`.
- Solo formato o linters → `pre-commit-and-lint`.

---

## Flujo resumido

1. **Especificar** — entrada, salida, errores, edge cases (proporcional al tamaño).
2. **Planificar** — unidades testeables; layout del repo; diseño alineado con
   módulos similares (regla `python-errors-and-oop`: SOLID/KISS/YAGNI/DRY de forma
   pragmática, sin refactor desproporcionado).
3. **TDD** — Red → Green → Refactor por comportamiento; `pytest` tras cada paso.
4. **Validar** — cada requisito de la spec tiene al menos un test; `fail_under` del repo.
5. **Cerrar** — `pre-commit-and-lint` + resumen spec → tests.

---

## Spec mínima

```markdown
## Spec: <nombre>

**Entrada:** <tipos y restricciones>
**Salida:** <tipos y garantías>
**Comportamiento:** <requisitos numerados>
**Errores:** <excepciones y cuándo>
**Edge cases:** <vacíos, límites>
```

---

## Reglas críticas

- Spec antes que código; test antes que implementación (salvo helpers triviales).
- Un ciclo Red-Green-Refactor por comportamiento.
- Convenciones del repo: skill `python-coding`, tests con `pytest-and-coverage`.
- Type hints en firmas públicas como parte de la spec ejecutable.

---

## Salida esperada

- Spec (markdown o docstring según tamaño).
- Tests que cubren cada requisito.
- Implementación en verde; pre-commit pasado en ficheros tocados.
- Tabla mental requisito → test que lo verifica.
