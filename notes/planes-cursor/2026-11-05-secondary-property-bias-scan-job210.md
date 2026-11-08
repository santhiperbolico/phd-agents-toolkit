# Plan Cursor: Phase 1 secondary-property bias scan (job 210)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-11-05 |
| Estado | en curso (T1–T7 implementados; T8 pendiente de corrida producción) |
| Repo de producto | `fnl_matching_error_reduction` |
| Rama de trabajo | `feature/secondary-property-bias-scan` (creada desde `feature/pgg-error-bars-mstar-oii`) |
| Spec / plan maestro | [Phase1_secondary_property_bias_scan.md](./Phase1_secondary_property_bias_scan.md) |

## Objetivo

Implementar el pipeline de diagnóstico Phase 1 (escaneo `b(M, q)` y test de muestra extrema) en
`fnl_matching_error_reduction`, ejecutarlo primero sobre **manifest job_id = 210**, y documentar
la decisión del *gate* (`r_extreme ≤ 1 + tol` vs Phase 1b).

## Contexto

### Caso de referencia (job 210)

Fila en `configs/manifests/pgg_mstar_oii_selected.csv`:

| Campo | Valor |
| --- | --- |
| `job_id` | 210 |
| `object` | LRG1 |
| `snapshot` | 109 (z ≈ 0.5232 vía metadata LRG1) |
| `sam` | galform |
| `property` / `property_key` | ssfr |
| `bin_lo` / `bin_hi` | −0.27832 / −0.18112 |
| `fnl` | fnl0 |
| `filename` | `P_gg_LRG1_fnl0_galform_ssfr_m0p27832_m0p18112.npz` |

Es el bin Galform LRG1 sSFR citado en la spec (amplitud FastPM ~2× respecto a `P_gg`, optimizador
de masa saturado). Encaja con el objetivo del gate Phase 1.

### Estado del repo al abrir la rama

- Rama activa: `feature/secondary-property-bias-scan` (base
`feature/pgg-error-bars-mstar-oii`, incluye `lower_mass_cut_property_pgg` y manifest CSV).
- `FastPMCatalogReader` en `read_data/fastpm.py` solo carga ID, posición y `Length`; **no** lee
aún `Rdisp`, `Vdisp`, `InitialPosition`, etc. → T1 debe ampliar o añadir un lector FoF dedicado.
- Reutilizar utilidades de manifest y rutas `P_gg` ya presentes en la rama base (no cherry-pick desde
otra rama).

### Rutas y datos (a fijar en JSON de config)

- `fastpm_path`, `fof_snapshot`, `fof_subdir`: alinear con configs existentes
(`fof_0.5000`, `LL-0.200`, ruta FastPM N2048 accesible en el entorno de ejecución).
- `pgg_base_dir`: directorio que contiene el NPZ del manifest (local `output/P_gg` o ruta compartida
del cluster según máquina).
- `N_SAM`: obtener del NPZ (`n_gal` o campo equivalente) o del JSON de lower-mass-cut si ya existe
para este bin; registrar la fuente en `scan_extreme.json`.

## Alcance

- **Incluido:** T1–T7 de la spec maestra; config + CLI + Slurm para **un** job (`job_id: 210`);
salidas bajo `output/secondary_property_bias_scan/...`; tests pytest; nota breve en
`docs/conclusions/` tras la primera corrida válida (T8).
- **Fuera de alcance:** Phase 1b (campos de entorno), Phase 2 (sampler paramétrico), Phase 3
(`R(k)` / `b_φ`); segundo caso ELG del plan maestro (solo si job 210 no basta para cerrar T8).

## Orden de implementación (agente)

Cada bloque termina con tests del bloque + `pre-commit` en ficheros tocados.

### Bloque A — T1 Catálogo y semántica FoF

1. Localizar snapshot FoF en BigFile (misma convención que `lower_mass_cut_matching`).
2. Extender lectura: `Length`, `Position`, `InitialPosition`, `Rdisp`, `Vdisp` (6 componentes);

   documentar en código constante `RDisp_COMPONENT_ORDER` tras verificar en fuente FastPM / T1 checks.
3. Script o función de inspección (puede ser subcomando del pipeline): `N_catalogue`, `min(Length)`,

   masa mínima FoF, comparar con hipótesis `M_cut ≈ 1.51e11` = catálogo completo.
4. Checks 4.4b: correlación `q` vs `log M` (tras T2), fracción eigenvalues negativos, escala

   `tr V` vs `M`.

**Entregable:** módulo o funciones en `matching/` + log/README fragment en conclusión T1.

### Bloque B — T2 Propiedades

1. Nuevo `src/fnl_matching/matching/secondary_properties.py` (funciones puras, sin imports internos).
2. Implementar: ensamblado 3×3, trazas, `virial_ratio`, desplazamiento periódico, `shape_r` /

   `anisotropy_v` con máscara `Length >= length_shape_min`.
3. `percentile_within_mass_bins` con edges configurables.

**Entregable:** `src/tests/matching/test_secondary_properties.py` (rotaciones, orden tensor erróneo,
 percentiles dentro de bins).

### Bloque C — T3 Selección

1. Máscaras celda `(mass_bin, quantile_bin)` y muestra extrema con fracción `f = N_SAM / N_cat`

   por bin de masa (rank determinista).
2. Tests: `N_extreme == N_SAM`, estabilidad del rank.

### Bloque D — T4 Pipeline

1. `src/fnl_matching/pipelines/secondary_property_bias_scan.py`:
   - Carga una IC (`fastpm_i_sim` o índice fijo en config).
   - Resuelve entrada manifest por `job_id` (210 por defecto en config de prueba).
   - Carga `P_gg`, alinea convención shot-noise con `get_pk_halos` (pregunta abierta #2 de la spec).
   - Bucle propiedades: celdas + extremos low/high `q`; splits `length_splits`.
2. Métricas: `r_cell`, `b_rel`, `r_extreme`, decisión gate.

### Bloque E — T5 Config / CLI / Slurm

1. `configs/pipeline_run_secondary_property_bias_scan_job210.json` (o nombre equivalente).
2. `scripts/pipelines/run_secondary_property_bias_scan.py` (patrón de `run_lower_mass_cut_matching.py`).
3. `slurm/pipelines/secondary_property_bias_scan.slurm` (1 tarea, `job_id=210`).

### Bloque F — T6 Figuras

1. `b_rel` vs masa por quantil; `P_extreme/P_gg` vs `k`; diagnóstico `q` vs masa.
2. Rutas: `output/secondary_property_bias_scan/galform/LRG1/ssfr_m0p27832_m0p18112/<property>/`.

### Bloque G — T7 Tests de pipeline

1. `src/tests/pipelines/test_secondary_property_bias_scan.py` con mocks de `get_pk_halos` y catálogo pequeño.

### Bloque H — T8 Ejecución y reporte

1. Activar venv, `export PYTHONPATH=src`, pytest completo del alcance.
2. Correr pipeline en IC de referencia (local si cabe en memoria; si no, Slurm).
3. `docs/conclusions/secondary_property_bias_scan_job210.md`: tablas gate, sin interpretación física

   más allá de los números.

## Criterios de aceptación

- [x] Rama `feature/secondary-property-bias-scan` contiene el pipeline Phase 1 completo (T1–T7).
- [x] Config ejecutable apuntando a `job_id=210` y manifest `pgg_mstar_oii_selected.csv`.
- [ ] `scan_cells.csv` y `scan_extreme.json` generados para al menos una IC de referencia.
- [ ] Gate documentado (viable / no viable / Phase 1b) con `tol` y `r_extreme` numéricos.
- [ ] `pytest` del módulo nuevo en verde; pre-commit en ficheros Python tocados.
- [ ] Sin commit/push salvo petición explícita del usuario.

## Riesgos (priorizados para job 210)

1. Catálogo FoF muy grande en memoria → lectura por columnas necesarias o batch (reutilizar generator

   de `fastpm.py` si se generaliza).
2. Propiedades de forma inestables en halos `Length ~ 15` → respetar splits y no interpretar shape

   en cola baja de masa.
3. `N_SAM` mal definido → validar contra NPZ antes del test extremo.

## Notas de sesión

### 2026-11-05

- Rama `feature/secondary-property-bias-scan` recreada desde `feature/pgg-error-bars-mstar-oii`
(solicitud «pgg-errors-nars»: no existe esa rama remota/local; se usó la rama PGG del repo).
- Caso de prueba fijado: manifest **job_id 210** (Galform LRG1 ssfr bin negativo).
- Implementación T1–T7 en rama `feature/secondary-property-bias-scan`: lector FoF extendido,
`secondary_properties.py`, pipeline, config job 210, CLI, Slurm, tests (15 passed).
- Pendiente T8: ejecutar scan completo (~30M halos × muchas celdas; usar Slurm).

## Resultado

Pendiente — PR futura desde `feature/secondary-property-bias-scan` cuando T1–T8 cumplan criterios.
