# Notas PhD

Carpeta central para **notas personales de doctorado**: reuniones, investigación, reportes y planes de trabajo con Cursor. Vive en `phd-agents-toolkit` para que el agente las encuentre con el workspace multi-root.

## Qué va aquí vs en `docs/`

| Aquí (`notes/`) | En `docs/` |
| --- | --- |
| Notas de reuniones, apuntes, reportes para ti o el grupo | Specs SDD y análisis ligados a issues/repos de producto |
| Planes de sesión con Cursor | Documentación técnica transversal de implementación |
| Borradores y seguimiento informal | Contexto compartido antes/durante código en un repo concreto |

## Estructura

```text
notes/
  README.md                 # este fichero
  _templates/               # plantillas al crear una nota nueva
  analisis/                 # análisis de datos, papers, hipótesis
  reportes/                 # informes listos para compartir (tutor, grupo, paper)
  reuniones/                # actas y seguimiento de reuniones
  notas/                    # apuntes rápidos, ideas, lecturas
  planes-cursor/            # planes de implementación y sesiones con el agente
```

## Convención de nombres

Usa **slug en minúsculas**, sin espacios, separado por guiones:

| Tipo | Patrón | Ejemplo |
| --- | --- | --- |
| Reunión | `YYYY-MM-DD-<tema>.md` | `2026-08-24-seguimiento-tutor.md` |
| Reporte | `YYYY-MM-DD-<tema>.md` | `2026-03-15-resultados-matching.md` |
| Análisis | `YYYY-MM-DD-<tema>.md` o `<tema>.md` si es iterativo | `fastpm-halos-analisis.md` |
| Nota | `YYYY-MM-DD-<tema>.md` o `<tema>.md` | `lectura-springel-2005.md` |
| Plan Cursor | `YYYY-MM-DD-<tema>.md` | `2026-08-24-issue-5-catalogos.md` |

Copia la plantilla desde `_templates/` al crear un fichero nuevo.

## Enlaces útiles en cada nota

Cuando aplique, enlaza:

- Issue o PR de GitHub del repo de producto
- Entrada en Zotero (clave de cita o DOI)
- Página de Notion (tarea o reunión)
- Spec en `docs/<repo>/<tarea>/`
- Paper en Overleaf

## Uso con Cursor

1. Abre el workspace `Notas-Doctorado` (o cualquier workspace que incluya `phd-agents-toolkit`).
2. Pide al agente: «resume mis reuniones del último mes», «busca análisis sobre X en `notes/`», etc.
3. Para implementación guiada: crea un plan en `planes-cursor/` y referencia el issue o spec en `docs/`.

## Privacidad

Por defecto las notas se versionan en git. Si alguna nota no debe subirse, guárdala fuera del repo o añade su patrón a `.gitignore` local (no versionado).
