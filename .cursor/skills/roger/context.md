# Contexto científico — plan de investigación

Lee estos ficheros **bajo demanda**, no de golpe. Rutas absolutas.

## Raíz

`/home/santhiperbolico/Documentos/Doctorado/plan_innovacion`

El repo puede estar en el workspace multi-root. Si no, usa Read/Glob con
ruta absoluta (no está bajo `repositorios/`; `phd-local-docs` no lo cubre).

## Fuentes de verdad

| Documento | Uso |
| --- | --- |
| `plan_investigacion/plan_investigacion_doctorado.md` | Tesis, objetivos, artículos, plan de trabajo |
| `plan_investigacion/plan_formativo_doctorado.md` | Horas IMEIO, formación prevista |
| `plan_investigacion/actividades_realizadas.md` | Actividades ya registradas |
| `SPEC.md` | Decisiones de revisión del plan (CAPD 2026) |
| `plan_latex/references.bib` | Bibliografía del plan |
| `docs/` | Notas de reuniones, state of the art, comentarios de dirección |

Markdown en `plan_investigacion/` manda; `plan_latex/` es derivado (`make pdf`).

## Instantánea (no sustituye la lectura)

- **Título:** Enhancing computational experiments with Machine Learning
  algorithms for cosmological tracer catalogues.
- **Objetivo:** métodos de aprendizaje automático, estadística computacional
  y simulación eficiente para abaratar experimentos numéricos en cosmología
  de gran escala (conexión galaxia–halo; ELG y QSO; DESI y Euclid).
- **Tres avenidas / artículos:**
  1. Simulaciones aproximadas (FastPM, exploración DISCO-DJ) + Haloscope.
  2. HOD con sesgo de ensamblaje y emuladores (procesos gaussianos).
  3. Catálogos rápidos de trazadores y SBI.
- **Dedicación:** tiempo parcial, horizonte ~7 años.
- **Año 1 (orientativo):** física de trazadores, colaboraciones, CAPD,
  estancia breve AstroAI; artículos de colaboración (Hα, BAO).

Al aconsejar, alinea con el artículo y el año en curso. No reintroduzcas
términos que el SPEC descarta (p. ej. PNG en el resumen, Uchuu/`hod_madrid`
en el plan). Terminología del plan: sesgo de ensamblaje, artículo,
estadísticos resumidos, flujo de trabajo.

## Repos de investigación

Hermanos típicos bajo
`/home/santhiperbolico/Documentos/Doctorado/repositorios`.
README y docs → skill `phd-local-docs`. Código del repo abierto → skills
de programación, no este fichero.
