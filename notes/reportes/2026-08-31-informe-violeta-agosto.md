# Informe de actividad — agosto 2026

| Campo | Valor |
| --- | --- |
| Fecha | 2026-08-31 |
| Audiencia | Violeta González-Pérez (tutor) |
| Estado | borrador |
| Repo / tema | GNE, Euclid Hα, Haloscope FastPM, phd-agents-toolkit |

**De:** Santiago Arranz Sanz  
**Fuentes:** DMs Slack (Euclid + DESI), Registro de tareas Notion, notas en `phd-agents-toolkit`

---

## Resumen

Agosto se repartió entre tres líneas: **(1)** cierre de la discrepancia Shark/Galform en GNE (Griffin+19 + luminosidad instantánea), **(2)** regeneración masiva de líneas de emisión y cortes Hα para Euclid, y **(3)** retoma intensa de **Haloscope FastPM** en Taurus (fix tidal #12, pipeline E2E #13, calibración de masas y verificación de ICs). La PR de GNE está lista para revisión; Haloscope avanzó mucho en código y smoke tests, pero la verificación de ICs con Adrián arrojó **r(k) incompatible** (mediana 0,17 frente al umbral 0,9), lo que bloquea el matching 1-1 por ahora.

---

## Actualización — 4 sep 2026 (pre-status 7 sep)

### GNE — cerrado

- [PR #39](https://github.com/galform/get_nebular_emission/pull/39) **mergeada** (1 sep 2026, `viogp`); [issue #37](https://github.com/galform/get_nebular_emission/issues/37) cerrada.
- Comentario aclaratorio en issue #37 actualizado (4 sep): **Bravo+25** = `L(ṁ_hh + ṁ_sb)`; **Griffin+19** = `L_hh + L_sb` ([comentario](https://github.com/galform/get_nebular_emission/issues/37#issuecomment-5485238012)).
- Dudas de Violeta en DM Euclid (suma ṁ vs suma L por canal; Lbol-function) respondidas.
- Tarea Notion [TODO's GNE repositorio](https://app.notion.com/p/3cd2070c3c2880d7baa4f31c6f200153) → **Listo**.

### Cortes Hα Euclid

- Cortes recalculados con Griffin+19 + luminosidad instantánea; **hechos**.
- A la espera de **revisión de datos** por el equipo (Nicola/Santi/Violeta).
- **Pendiente de decisión:** reducción de varianza en los 100 espectros de potencia (fnl100); confirmar si el grupo quiere que se ejecute.

### Sin cambio respecto a agosto

- Haloscope FastPM (#12, #13, matching ICs) — ver secciones 3 y 8.

---

## Actualización — 6 sep 2026 (pre-status 7 sep)

### Haloscope — campos FoF bigfile (cerrado)

- Documentados **Rdisp**, **Vdisp**, **RVdisp** y **Task** del catálogo FoF FastPM (bigfile `LL-0.200`, a = 0.5, sim `fastpm_N1` fnl100).
- **Rdisp / Vdisp / RVdisp:** tensores de segundos momentos del grupo FoF (espacial, velocidad y cruzado r–v); calculados en `FastPM/libfastpm/fof.c`.
- **Task:** rank MPI de paralelización (`ThisTask`), no magnitud física.
- Nota local: [`notes/notas/2026-09-06-fastpm-fof-bigfile-campos.md`](../notas/2026-09-06-fastpm-fof-bigfile-campos.md)
- Notion Notes: [FastPM FoF bigfile](https://app.notion.com/p/3d32070c3c288156b8f1f569f5fbc603)
- Análisis detallado: [`notes/analisis/2026-09-06-fastpm-fof-bigfile-fields.md`](../analisis/2026-09-06-fastpm-fof-bigfile-fields.md)

### Sin cambio respecto al 4 sep

- Pipeline Haloscope #13 — commit/push y validación T/|U| vs Rockstar pendientes (trabajo en Taurus).
- Matching FastPM ↔ UNIT — bloqueado por r(k) = 0,17.

---

## 1. GNE — Incongruencias Shark vs Galform

**Tarea Notion:** [Incongruencias Flujos Shark y Galform](https://app.notion.com/p/3652070c3c2880d091f8f7485d983b01) — **To Review**

### Qué se hizo

- Diagnóstico de la diferencia ~3 magnitudes en cortes Hα: tratamiento temporal distinto del AGN (Griffin+19 con duty cycle en Galform vs luminosidad instantánea en Shark).
- Implementación del método **Griffin+19** con flag `Lagn_insta` en `get_nebular_emission`.
- Comparación de funciones de luminosidad bolométrica AGN (SB/HH por separado, `f_q` = 1 vs 10).
- **PR abierta:** [galform/get_nebular_emission#39](https://github.com/galform/get_nebular_emission/pull/39) contra `main`.
- **Issue:** [#37](https://github.com/galform/get_nebular_emission/issues/37) con dos puntos abiertos para revisión:
  1. Semántica de `Lagn_insta=True` (¿saltar cálculo instantáneo es correcto?).
  2. Método `get_Lagn_G19`: suma de `mdot` vs suma de `L(mdot)`.
- Tests: 11 passed (`test_Lagn.py`, `test_griffin_lagn_insta.py`).
- Spec y documentación en `phd-agents-toolkit/docs/get_nebular_emission/gne-griffin-lagn-insta/`.

### Coordinación Slack con Violeta

- Pediste comparar **Lbol** en tres niveles: tablas Galform → input GNE → salida GNE (pendiente de cerrar).
- La discusión con Claudia Lagos sigue abierta; acordasteis no dar por cerrada la discrepancia hasta su respuesta.
- El fix de la componente SB en Shark implica ~**20 % menos QSOs**; las fracciones de luminosidad AGN parecen similares a Galform (~5 %), por lo que el impacto en resultados finales podría ser moderado.

### Pendiente

- Revisión de la PR #39.
- Ejecutar GNE completo (Galform + Shark, SU/fnl0/fnl100, snapshots 65–109) tras merge.
- Comparación Lbol en tres niveles que pediste.

---

## 2. Cortes Hα para Euclid (z ~ 1)

**Tarea Notion:** [Corte Hα para Euclid en z~1](https://app.notion.com/p/3092070c3c2880768ea1eea96da7d8a8) — **To Review**

### Qué se hizo

- Cortes para **iz87, iz90, iz97, iz98** (Shark y Galform, fnl0/fnl100).
- Regeneración masiva de `lines.hdf5` en Shark tras corregir un bug en la config del script de generación (se borraron y relanzaron todas las líneas).
- Líneas de Galform en `/data21/users/vgonzalez/Data/Galform_to_copy/` (pendiente mover a `Galform/` cuando Violeta revise permisos de escritura).
- Espectros de potencia y comunicación a Nicola/Santi para iz87 e iz97.

### Pendiente (bloque 5 de la tarea)

- **Recalcular cortes con Griffin+19 + luminosidad instantánea** (depende del merge de la PR GNE).
- Ajuste fino del corte de flujo (zoom + interpolación) donde no encaja bien con Reyes-Peraza.
- fnl100: falta iz96 en Shark; ejecuciones en curso para redshifts altos.

---

## 3. Haloscope FastPM (`density_field_properties`)

Línea principal de fin de mes. Cinco tareas/issues activas.

### 3.1 Fix tidal anisotropy — Issue [#12](https://github.com/computationalAstroUAM/density_field_properties/issues/12)

**Tarea Notion:** [Investigar Haloscope FastPM](https://app.notion.com/p/39f2070c3c2880fab66dcc655be99ee9) — **En progreso**

- Rama `fix/12-tidal-descriptor-columns`, commit `1d6e571`.
- Causa raíz: `np.savetxt` recibía tupla en lugar de matriz 2D (8 columnas por halo); además `get_grid_cell` mapeaba mal los ejes.
- Tests nuevos en verde.
- **Pendiente:** merge/PR y rerun de batches en cluster para validar en datos reales.

### 3.2 Pipeline E2E tidal — Issue [#13](https://github.com/computationalAstroUAM/density_field_properties/issues/13)

**Avance del 31 ago** (working tree local, sin commit):

| Entregable | Estado |
| --- | --- |
| Notebook `SIM_to_FASTPM_unitsim_fastpm_mn5_tidal.ipynb` | ✅ |
| Módulos `tidal_features.py`, `pipeline_tidal.py` | ✅ |
| CLI `run_sim_to_fastpm_haloscope_tidal.py` | ✅ |
| Slurm smoke + producción | ✅ |
| Tests unitarios (3 passed) | ✅ |
| Smoke E2E local en Taurus | ✅ |
| Run Slurm catálogo completo | ❌ |
| Test integración pytest | ❌ |
| Validación numérica T/\|U\| vs Rockstar | ❌ |

Inputs: columna Rockstar **T/\|U\|** (`t_over_u`) + `tidal_anisotropy` de descriptores de entorno.

Nota detallada: [`notes/planes-cursor/2026-08-31-issue-13-haloscope-e2e-progress.md`](../planes-cursor/2026-08-31-issue-13-haloscope-e2e-progress.md).

### 3.3 Calibración de masas FastPM ↔ UNIT

**Tarea Notion:** [Comparación masas FastPM vs UNIT](https://app.notion.com/p/3ab2070c3c288089814ec11fb2afb7cc) — **En progreso**

- Nota de análisis: [`notes/analisis/2026-08-27-haloscope-mass-calibration.md`](../analisis/2026-08-27-haloscope-mass-calibration.md).
- Revisión del apéndice C de Ramakrishnan et al. 2025: Haloscope no recalibra masas; para FastPM↔UNIT hace falta medir HMF y, si procede, abundance matching.
- Conclusión preliminar: el problema principal no es M200b vs M200c, sino **FoF vs Rockstar**, alineación z/box/ICs y sesgo PM/N-body.

### 3.4 Matching FastPM ↔ UNIT — Issue bloqueante

**Tarea Notion:** [Matching de halos FastPM ↔ UNIT](https://app.notion.com/p/3ab2070c3c2880cca1c2c1c8a4a8190d) — **En progreso**

**31 ago — confirmación Adrián (Slack Cosmology-UAM):**

- FastPM MN5 = UNIT 4096 `fixedAmp_InvPhase_001`.
- Mismas seeds; matching por proximidad (sin particle IDs en UNIT).

**31 ago — verificación r(k) en Taurus:**

| Run | N halos | mediana r(k), k < 0,05 h/Mpc | Veredicto |
| --- | --- | --- | --- |
| Job 98402 (referencia) | 500k centrales | **0,17** | ICs **NO compatibles** |

- Headers OK: box 1000 Mpc/h, cosmología Planck-like idéntica.
- Snapshot UNIT: `out_128p.list.bz2` (a = 1; corregido: `out_8` FastPM también es a = 1, no z ≈ 1).
- Script: `scripts/verify_fastpm_unit_ics.py` + job Slurm.
- **No iniciar matching 1-1** hasta resolver discrepancia con Adrián o repetir con campo DM.

Nota detallada: [`notes/planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md`](../planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md).

---

## 4. Infraestructura — `phd-agents-toolkit` (24 ago)

Sesión de 5 h documentada en Notion; [PR #3](https://github.com/santhiperbolico/phd-agents-toolkit/pull/3) mergeada:

- MCP correo UPM, MCP Slack session (Euclid/DESI).
- Skills Roger y Notion calendario.
- Carpeta `notes/` con plantillas y planes Cursor de las sesiones de Taurus.
- Specs SDD para GNE Griffin y Haloscope en `docs/`.

---

## 5. Otras coordinaciones Slack

| Tema | Canal | Resumen |
| --- | --- | --- |
| Visita Carolina Cuesta (Flatiron) | DM Euclid (Violeta, Angie, Santiago) | Propuesta de visita de 1 día en octubre; Carol confirma disponibilidad |
| fnl100 todos los redshifts | DM DESI (Violeta, Miguel, Santiago) | Acordado correr fnl100 incluyendo redshifts altos; reducción de barras de error en curso |
| Permisos Galform en data21 | DM DESI | Líneas en `Galform_to_copy`; mover a `Galform/` cuando Violeta revise permisos |
| Paper PNG / batch DESI | `png_unitsim` | Gestión de coautores y timing arXiv (menos relevante para desarrollo) |

---

## 6. Estado de tareas Notion (resumen)

| Tarea | Estado | Avance agosto |
| --- | --- | --- |
| Incongruencias Shark/Galform | **Listo** | PR #39 mergeada; issue #37 cerrada |
| TODO's GNE repositorio | **Listo** | Cerrado 4 sep; comentario aclaratorio en #37 |
| Corte Hα Euclid z~1 | **To Review** | Cortes Griffin+insta hechos; revisión datos pendiente |
| Investigar Haloscope FastPM | **En progreso** | Fix #12; pipeline #13; Rdisp bigfile documentado (6 sep) |
| Matching FastPM ↔ UNIT | **En progreso** | Adrián confirma ICs; r(k) incompatible |
| Comparación masas | **En progreso** | Nota Ramakrishnan; HMF sin medir aún |

---

## 7. Bloqueos y decisiones pendientes

1. ~~**Revisión PR GNE #39**~~ — cerrado (merge 1 sep; issue #37 cerrada).
2. ~~**Comparación Lbol** en tres niveles~~ — cerrado (sin discrepancias entre etapas del pipeline).
3. **Revisión cortes Hα** — datos enviados; esperando feedback del equipo.
4. **fnl100 / reducción de varianza** — pendiente confirmar si ejecutar los 100 espectros de potencia.
5. **ICs FastPM ↔ UNIT** — Adrián dice mismas seeds, pero r(k) = 0,17. ¿Escalar con él antes de matching?
6. **Permisos escritura** en `/data21/users/vgonzalez/Data/Galform/`.
7. **Visita Carolina Cuesta** — ¿proceder a contactarla para octubre?

---

## 8. Plan para septiembre (propuesta)

| Prioridad | Acción |
| --- | --- |
| Alta | ~~Merge PR GNE~~ → cortes Hα Griffin+insta **hechos**; validación datos pendiente |
| Alta | Resolver discrepancia r(k) con Adrián (param files, P(k) en DM, FastPM nbody) |
| Alta | Commit/push pipeline Haloscope #13; smoke Slurm con assembly bias |
| Media | Merge fix #12; rerun descriptores tidales |
| Media | HMF en subset FastPM vs UNIT |
| Baja | Contacto Carolina Cuesta (octubre) |

---

## Referencias y enlaces

- Notas planes: [`notes/planes-cursor/`](../planes-cursor/) — `2026-08-25`, `2026-08-27`, `2026-08-31`
- Análisis masas: [`notes/analisis/2026-08-27-haloscope-mass-calibration.md`](../analisis/2026-08-27-haloscope-mass-calibration.md)
- Docs GNE: [`docs/get_nebular_emission/gne-griffin-lagn-insta/`](../../docs/get_nebular_emission/gne-griffin-lagn-insta/)
- Docs Haloscope: [`docs/density_field_properties/issue-6-sim-to-fastpm-haloscope/`](../../docs/density_field_properties/issue-6-sim-to-fastpm-haloscope/)
- Análisis FoF bigfile: [`notes/notas/2026-09-06-fastpm-fof-bigfile-campos.md`](../notas/2026-09-06-fastpm-fof-bigfile-campos.md), [`notes/analisis/2026-09-06-fastpm-fof-bigfile-fields.md`](../analisis/2026-09-06-fastpm-fof-bigfile-fields.md)
- Status Violeta (próximo): [Notion 2026-09-07 calendario](https://app.notion.com/p/3cd2070c3c288152883dc6871ab2ccc1) · [Informe semanal](https://app.notion.com/p/3d32070c3c288170b380eebc9c058a48)
