# Documentación de librerías

Documentación general de los repos de investigación que **no vive en cada librería**: specs SDD, análisis de diseño, notas de seguimiento y contexto compartido entre workspace y agentes. El código sigue en cada repo de producto.

## Qué va aquí vs en cada repo

| Aquí (`docs/`) | En cada repo de producto |
| --- | --- |
| Specs y planes antes o durante la implementación | Código, tests y README del proyecto |
| Análisis transversal (integraciones, decisiones de diseño) | Documentación de API y uso cotidiano |
| Enlaces a issues de GitHub y estado de la tarea | Changelog e historial de releases |

## Layout

```text
docs/
  <nombre_repo>/
    <tarea>/
      spec.md          # spec SDD (habitual)
      analysis.md      # u otro markdown según la tarea
```

- **`<nombre_repo>`:** nombre corto del repositorio (p. ej. `density_field_properties`, `get_nebular_emission`).
- **`<tarea>`:** slug estable, habitualmente `issue-<n>-<resumen-corto>` o un nombre descriptivo del trabajo.

En cada fichero, enlaza al issue de GitHub cuando exista y, si aplica, anota el estado de implementación en el repo de producto.

## Índice adicional (runbooks)

| Repo | Documento |
| --- | --- |
| `density_field_properties` | [Rockstar `find_parents` (host halos / PID)](density_field_properties/rockstar-find-parents/find_parents.md) |
### density_field_properties (ejemplos recientes)

| Tarea | Spec | Plan |
| --- | --- | --- |
| Calibración de masa LR (Haloscope / Forero) | [mass-calibration-haloscope/spec.md](./density_field_properties/mass-calibration-haloscope/spec.md) | [implementation-plan.md](./density_field_properties/mass-calibration-haloscope/implementation-plan.md) |
| Haloscope SIM → FastPM | [issue-6-sim-to-fastpm-haloscope/analysis.md](./density_field_properties/issue-6-sim-to-fastpm-haloscope/analysis.md) | — |
