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
