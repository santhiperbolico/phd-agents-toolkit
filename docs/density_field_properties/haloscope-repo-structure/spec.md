# Spec: estructura del repositorio Haloscope (density_field_properties)

**Repository:** [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties)
**Plan:** [`notes/planes-cursor/2026-09-19-haloscope-repo-structure.md`](../../../notes/planes-cursor/2026-09-19-haloscope-repo-structure.md)
**Pipeline funcional:** [`notes/planes-cursor/2026-09-17-haloscope-pipeline-implementacion.md`](../../../notes/planes-cursor/2026-09-17-haloscope-pipeline-implementacion.md)
**Status:** S0–S3 completados; S6 parcial (2026-09-20) — `read_data/halos/`, `validation/assembly_bias_panel.py`, config JSON del pipeline
**Last updated:** 2026-09-20

---

## 1. Alcance

Esta spec define la **organización del código**, los **contratos de datos** entre capas y los **requisitos estructurales** del pipeline Haloscope. No sustituye las decisiones científicas de Fase 0 ni las tareas funcionales del plan de implementación (filtros, YAML loader, métricas, etc.).

### Incluido

- Paquetes Python, pipelines, layout Slurm y artefactos intermedios.
- Schemas de tablas Parquet HR/LR y enriquecidas.
- Grafo de dependencias e imports permitidos.
- Requisitos R1–R20 verificables.

### Fuera de alcance

- Refactor inmediato del código existente.
- Cambio de nombre del repositorio Git.
- Implementación RF/XGBoost masa (Fase 6).
- Export HOD / Galform / SHARK.

---

## 2. Paquetes y responsabilidades

### 2.1 `read_data`

**Propósito:** lectura de datos crudos sin transformaciones científicas.

| Submódulo | Contenido |
| --- | --- |
| `particles/` | Iteración por lotes de partículas DM (UNIT bz2, FastPM BigFile/snap) |
| `halos/base.py` | `HaloCatalogData`, protocolo `HaloCatalogReader` |
| `halos/rockstar.py` | `.list`, hlist Consistent-Trees |
| `halos/fastpm.py` | Halos nativos BigFile (no Rockstar) |
| `halos/registry.py` | `get_halo_catalog_reader(name)` |
| `cosmology.py` | `Cosmology` desde cabeceras Rockstar |

**Prohibido en este paquete:** filtros `M ≥ 20 m_p`, centrales, abundance matching, join espacial de entorno.

**Origen actual:** `halo_catalog/`, `density_field/particle_io.py`, `cosmology.py`.

---

### 2.2 `environment_properties`

**Propósito:** derivar campos del medio a partir de partículas DM y posiciones de halos.

| Submódulo | Contenido |
| --- | --- |
| `cic/` | Depósito CIC, `DensityFieldInfo`, metadatos de malla |
| `fourier/` | `kgrid`, utilidades FFT |
| `tidal_tensor/` | Campo tensor tidal desde densidad |
| `tidal_anisotropy/` | `ca`, `ba`, índices `T/|U|` por halo |

**Entradas:** fichero de partículas DM; catálogo de posiciones (solo id, x, y, z).

**Salidas:** ficheros de malla + tabla Parquet de descriptores por halo (ver §5.2).

**Origen actual:** `density_field/cic_deposit.py`, `density_field/utils.py`, `density_field/fourrier_transformations.py`, `tidal_tensor.py`, `halo_environment_descriptors/tidal_anisotropy.py`.

---

### 2.3 `preprocessing`

**Propósito:** producir tablas HR/LR listas para `haloscope.fit` / `haloscope.predict`.

| Submódulo | Contenido |
| --- | --- |
| `filters.py` | Centrales, corte masa, snapshot, límites de box |
| `mass_calibration.py` | Abundance matching; futuro ML masa |
| `environment_join.py` | KD-tree `env`; join tidal (`ca`, `ba`, `T/|U|`) |
| `feature_table.py` | Construcción de columnas INPUT/OUTPUT |
| `schemas.py` | Validación dtypes, columnas obligatorias, Parquet schema |

**Reglas científicas (Fase 0):**

- HR (entrenamiento): centrales + `M200b ≥ 20 m_p` cuando `sample.central_only_sim: true`.
- LR (objetivo): calibración opcional vía `haloscope.calibrate_mass`.
- Haloscope **no** modifica `M200b`; usa `M200b_cal` solo para asignación de bin.

**Origen actual:** `sim_to_fastpm/load_catalogs.py`, `mass_matching.py`, `environment.py`, `tidal_features.py`, parte de `config.py`.

---

### 2.4 `haloscope`

**Propósito:** modelo CMVG y operaciones fit/predict únicamente.

| Submódulo | Contenido |
| --- | --- |
| `model.py` | `ConditionalMultiVariateGaussian` (vendored upstream) |
| `training.py` | Fit por bin log M, hold-out interno opcional |
| `predict.py` | Predicción por chunks / bins |
| `bins.py` | Bordes de masa parametrizables (Ap. D Ramakrishnan) |

**API pública mínima:**

```python
def fit_models(
    training_table,
    bin_edges,
    input_features,
    output_features,
    min_bin_size,
    random_seed=None,
):
    """Return dict mapping bin index to fitted CMVG."""


def predict_models(
    models,
    target_table,
    input_features,
    output_features,
    mass_column="M200b_cal",
    random_seed=None,
):
    """Return table with predicted secondary properties."""
```

**Prohibido:** lectura de catálogos, Slurm, plots, assembly bias.

**Origen actual:** `haloscope/haloscope.py`, `sim_to_fastpm/training.py`.

---

### 2.5 `utils`

**Propósito:** helpers reutilizables y visualización **no vinculante** al criterio de publicación.

| Submódulo | Contenido |
| --- | --- |
| `hmf/` | dn/dlog M, ratios entre catálogos, figuras diagnóstico |
| `plotting/` | Helpers matplotlib genéricos (corner, histogramas) |
| `stats/` | KS, correlación, MAE (funciones puras) |
| `paths/` | Resolución rutas relativas a `output/` y config |

**Regla:** si una función define pass/fail del Artículo I, pertenece a `validation/`, no a `utils/`.

---

### 2.6 `validation`

**Propósito:** métricas científicas y informes (Fase 4 del plan maestro).

| Submódulo | Contenido | Estado |
| --- | --- | --- |
| `assembly_bias_panel.py` | PDF panel b₁(M) post-enrich; título según `input_features` | ✅ implementado |
| `holdout.py` | KS/MAE hold-out SIM | pendiente |
| `marginals.py` | Distribuciones marginales post-enrich | pendiente |
| `assembly_bias.py` | b₁(M), colas en entorno (Ramakrishnan Fig. 4) | pendiente (helpers aún en `sim_to_fastpm/assembly_bias.py`) |
| `clustering.py` | P(k), ξ(r) | pendiente |
| `report.py` | Agregación HTML/PDF | pendiente |

**API mínima (panel assembly bias, invocable sin re-ejecutar fit — R15):**

```python
def write_tidal_assembly_bias_panel(
    halos_sim,
    halos_fastpm_enriched,
    repo_root,
    output_dir,
    input_features,
    mass_column_fastpm="M200b",
    assembly_bias_n_grid=128,
) -> Path:
    """Write assembly-bias PDF; title reflects Haloscope INPUT features."""
```

**Origen actual:** `sim_to_fastpm/assembly_bias.py` (helpers numéricos), `sim_to_fastpm/plotting.py` (parte científica). El pipeline **no** contiene lógica de assembly bias; la invoca desde `validation/`.

---

### 2.7 `pipelines/` (fuera de `src/`, raíz repo o bajo `src/density_field_properties/pipelines/`)

**Propósito:** orquestación CLI/Slurm; compone capas sin lógica de dominio duplicada.

| Script | Capas invocadas |
| --- | --- |
| `run_environment_properties.py` | read_data → environment_properties |
| `run_preprocessing.py` | read_data + environment_properties → preprocessing |
| `run_haloscope_enrichment.py` | preprocessing → haloscope → Parquet enriquecido; opcional `validation` |
| `run_validation.py` | validation (+ utils plotting) |

**Orquestación Python (`src/density_field_properties/pipelines/`):**

| Módulo | Responsabilidad |
| --- | --- |
| `config.py` | `HaloscopeEnrichmentConfig`, `load_haloscope_enrichment_config()` |
| `haloscope_enrichment.py` | `run_haloscope_enrichment_pipeline(config)` |

**Entrypoint CLI:** un único argumento `--config` apuntando a JSON (sin flags `--tidal-preset`, `--quick-run`, etc.). Presets en `config/haloscope_run_*.json`.

**Shim legacy:** `haloscope/sim_to_fastpm/pipeline_tidal.py` delega en el pipeline canónico con configs tidal; se elimina en S7.

**Eliminado:** `haloscope_enrichment_tidal.py`, `run_haloscope_enrichment_tidal.py` (sustituidos por JSON + pipeline único).

---

## 3. Grafo de dependencias (imports)

```text
read_data          → (stdlib, numpy, pandas)
environment_properties → read_data
preprocessing      → read_data, environment_properties, utils.stats (opcional)
haloscope          → numpy, pandas, model vendored
utils              → read_data (solo hmf/plotting si necesario)
validation         → utils, preprocessing.schemas, haloscope (solo tipos)
pipelines          → todas las capas anteriores
```

**R1 — Acyclic imports:** ningún paquete bajo `src/density_field_properties/` importa `pipelines/`.

**R2 — haloscope aislado:** `haloscope/` no importa `preprocessing`, `read_data`, ni `validation`.

**R3 — read_data puro:** `read_data/` no importa `environment_properties`, `preprocessing`, ni `haloscope`.

---

## 4. Configuración

### 4.1 Ficheros de run (implementado vs objetivo)

| Fichero | Formato | Contenido | Estado |
| --- | --- | --- | --- |
| `config/haloscope_run.yaml` | YAML | Run SIM→FastPM producción (Fase 0) | existente |
| `config/haloscope_run_env_smoke.json` | JSON | env, subset 8k halos | ✅ |
| `config/haloscope_run_env_production.json` | JSON | env, catálogos completos | ✅ |
| `config/haloscope_run_tidal_smoke.json` | JSON | tidal INPUT, subset | ✅ |
| `config/haloscope_run_tidal_production.json` | JSON | tidal INPUT, producción | ✅ |
| `config/haloscope_run_tidal_*_assembly_bias.json` | JSON | tidal + PDF assembly bias | ✅ |
| `config/environment_properties.yaml` | YAML | Grid CIC, paths DM, snapshot | pendiente |
| `config/paths_taurus.yaml` | YAML | Rutas cluster; **no** commitear secretos | pendiente |

**Objetivo F1.2:** un loader YAML único; los JSON actuales son el contrato interino del pipeline de enrichment hasta unificar con `haloscope_run.yaml`.

### 4.2 Esquema JSON `HaloscopeEnrichmentConfig`

Loader: `load_haloscope_enrichment_config(path)` en `pipelines/config.py`.

```json
{
  "run_name": "haloscope_env_smoke",
  "paths": {
    "sim_hlist": null,
    "fastpm_list": null,
    "repo_root": ".",
    "output_dir": "output/sim_to_fastpm_haloscope"
  },
  "sample": {
    "max_sim_halos": 8000,
    "max_fastpm_halos": 8000,
    "max_descriptor_batch_files": null
  },
  "haloscope": {
    "input_features": ["env"],
    "min_bin_size": 5,
    "run_holdout_validation": true,
    "enriched_parquet_name": "fastpm_out_8_haloscope_enriched.parquet"
  },
  "tidal": {
    "n_grid": 512,
    "unit_descriptors_dir": null,
    "fastpm_descriptors_dir": null
  },
  "validation": {
    "assembly_bias": {
      "enabled": false,
      "n_grid": 128
    }
  },
  "collect_tables": false
}
```

| Sección | Claves | Notas |
| --- | --- | --- |
| `paths.sim_hlist`, `paths.fastpm_list` | str \| null | `null` → defaults de `sim_to_fastpm/config.py` |
| `sample.max_*` | int \| null | `null` → catálogo completo |
| `haloscope.input_features` | list[str] | `env`, `t_over_u`, `tidal_anisotropy`, … |
| `validation.assembly_bias.enabled` | bool | Si true, escribe PDF tras enrich |

### 4.3 Claves obligatorias `haloscope_run.yaml` (objetivo unificado)

Extiende el fichero actual; el loader debe validar:

| Clave | Tipo | Notas |
| --- | --- | --- |
| `sim.root`, `sim.hlist` | str | HR entrenamiento |
| `fastpm.rockstar_dir`, `fastpm.list_name` | str | LR objetivo |
| `sample.central_only_sim` | bool | Default true (Fase 0) |
| `sample.min_m200b_times_mp` | float | Default 20 |
| `haloscope.calibrate_mass` | bool | Default true |
| `haloscope.input_features` | list[str] | `env`, `ca`, `ba`, … |
| `haloscope.output_features` | list[str] | `cv`, `Spin`, `ca`, `ba` |
| `haloscope.env_radius_mpc_h` | float | Default 5 |
| `output.dir` | str | Raíz artefactos run |

**R4 — Single source of truth:** objetivo YAML único (F1.2). Interino: JSON de run en `config/haloscope_run_*.json` + defaults de cluster en `sim_to_fastpm/config.py` hasta unificar loaders.

---

## 5. Contratos de datos

### 5.1 Tabla de preprocesado HR (`hr_training_table.parquet`)

| Columna | dtype | Obligatoria | Origen |
| --- | --- | --- | --- |
| `id` | int64 | sí | read_data |
| `x`, `y`, `z` | float64 | sí | read_data (Mpc/h) |
| `M200b` | float64 | sí | read_data |
| `env` | float64 | sí (modo env) | preprocessing join |
| `ca`, `ba` | float64 | modo tidal | environment_properties + join |
| `T_over_U` | float64 | opcional tidal | environment_properties + join |
| `cv`, `Spin` | float64 | sí (targets) | read_data HR |

### 5.2 Tabla de preprocesado LR (`lr_target_table.parquet`)

| Columna | dtype | Obligatoria | Notas |
| --- | --- | --- | --- |
| `id`, `x`, `y`, `z` | | sí | |
| `M200b` | float64 | sí | masa Rockstar LR |
| `M200b_cal` | float64 | si calibrate_mass | abundance matching vs HR |
| `env` (+ tidal cols) | float64 | según input_features | |

### 5.3 Tabla enriquecida LR (`enriched_*.parquet`)

Columnas LR + predicciones `haloscope.output_features`. **No** sobrescribir `M200b` original.

### 5.4 Artefactos `environment_properties`

```text
output/{run_name}/environment/a{scale}/
  dm_density.dat
  dm_density_info.txt
  tidal_tensor/
  halo_env/tidal_anisotropy.parquet
  manifest.json
```

Columnas mínimas `tidal_anisotropy.parquet`: `id`, `ca`, `ba`; recomendado `T_over_U`, `x`, `y`, `z` para debug.

### 5.5 Manifest entre steps

Cada pipeline step escribe `manifest.json`:

```json
{
  "step": "preprocessing",
  "run_name": "haloscope_production_v1",
  "inputs": {"hr_hlist": "...", "lr_list": "...", "env_parquet": "..."},
  "outputs": {"hr_training_table": "...", "lr_target_table": "..."},
  "code_version": "git-sha",
  "timestamp": "ISO-8601"
}
```

**R5 — Manifest chain:** `run_haloscope_enrichment` falla si falta manifest del paso preprocessing o hashes no coinciden (modo estricto producción).

---

## 6. Requisitos estructurales

| ID | Requisito |
| --- | --- |
| **R1** | Grafo de imports acíclico según §3. |
| **R2** | `haloscope/` sin I/O de catálogos ni dependencia de cluster paths. |
| **R3** | `read_data/` sin filtros científicos de muestra. |
| **R4** | Config run desde YAML; defaults no duplicados en Python tras S2. |
| **R5** | Manifest JSON entre steps de pipeline. |
| **R6** | Schemas Parquet validados en `preprocessing/schemas.py` antes de fit/predict. |
| **R7** | Modo `input_features: [env]` funciona sin artefactos tidal. |
| **R8** | Modo tidal exige `tidal_anisotropy.parquet` + join en preprocessing. |
| **R9** | `M200b_cal` solo en LR cuando `calibrate_mass: true`. |
| **R10** | HR nunca sobrescribe `M200b` por abundance matching. |
| **R11** | Modelos CMVG exportables por bin (`models/bin_*.pkl`). |
| **R12** | Tests unitarios por capa bajo `src/tests/<capa>/`. |
| **R13** | Smoke integración con fixtures sintéticos sin Taurus (`@pytest.mark.integration` para E2E cluster). |
| **R14** | Slurm jobs separados por capa (§7 plan). |
| **R15** | `validation/assembly_bias_panel.py` invocable sin re-ejecutar fit (helpers aún en `sim_to_fastpm/assembly_bias.py`). |
| **R16** | Shims de import deprecados durante S3–S6; eliminados en S7. |
| **R17** | Vendored `haloscope.py` excluido de black/isort (política actual). |
| **R18** | Docstrings NumPy en inglés en código nuevo (convención repo). |
| **R19** | Sin imports dentro de funciones/métodos (convención repo). |
| **R20** | Carpeta `sim_to_fastpm/` ausente al cerrar S7. |

---

## 7. Layout de tests

```text
src/tests/
  read_data/
  environment_properties/
  preprocessing/
  haloscope/
  utils/
  validation/
  pipelines/           # smoke con tmp_path
```

| Requisito | Test previsto |
| --- | --- |
| R3 | Filtros ausentes en readers; tests en preprocessing |
| R6 | `test_schemas_reject_missing_columns` |
| R7 | `test_preprocess_env_only_without_tidal_artifacts` |
| R8 | `test_preprocess_tidal_requires_anisotropy_parquet` |
| R9–R10 | `test_mass_calibration_applies_only_to_lr` |
| R11 | `test_export_import_bin_models_roundtrip` |
| R13 | `test_pipeline_smoke_synthetic_fixtures` |

---

## 8. Slurm

```text
slurm/
  environment_properties/
    main_density_field_cic.slurm
    main_tidal_tensor_field_unit.slurm
    main_tidal_tensor_field_fastpm.slurm
  preprocessing/
    main_preprocessing_haloscope.slurm
  haloscope/
    main_sim_to_fastpm_haloscope.slurm
    main_sim_to_fastpm_haloscope_tidal.slurm
  validation/
    main_haloscope_validation.slurm
```

**R14:** cada script Slurm invoca un único entrypoint en `pipelines/` o `scripts/`, no lógica embebida en bash.

---

## 9. Trazabilidad plan maestro ↔ capas

| Tarea plan maestro | Capa spec |
| --- | --- |
| F1.0 Filtro masa | `preprocessing/filters.py` |
| F1.2 YAML loader | `pipelines/` + validación §4 |
| F1.4–F1.5 Hold-out, marginales | `validation/` |
| F1.6 Export modelos | `haloscope/training.py` |
| F2.1 Bins log M | `haloscope/bins.py` |
| F2.3 HMF gate | `utils/hmf/` + `preprocessing/mass_calibration.py` |
| F3.1–F3.5 Tidal | `environment_properties/` + `preprocessing/environment_join.py` |
| F4.1 Assembly bias | `validation/assembly_bias_panel.py` (+ migrar helpers a `validation/assembly_bias.py`) |
| F4.5 Informe | `validation/report.py` |

---

## 10. Migración y compatibilidad

Durante S3–S6, el repo expone shims:

```python
# density_field_properties/halo_catalog/__init__.py (deprecado)
import warnings
from density_field_properties.read_data.halos.base import HaloCatalogData

warnings.warn("halo_catalog is deprecated; use read_data.halos", DeprecationWarning)
```

**R16:** pytest emite warning test optional `test_no_deprecated_imports_in_new_code`.

Al **S7**, eliminar:

- `haloscope/sim_to_fastpm/`
- `halo_catalog/` (si migrado)
- `density_field/` como paquete top-level (contenido movido)
- `halo_environment_descriptors/`
- `tidal_tensor.py` en raíz de paquete

---

## 11. Errores y edge cases

| Situación | Comportamiento |
| --- | --- |
| Falta columna INPUT en tabla LR | `preprocessing/schemas` raise antes de predict |
| `calibrate_mass: true` sin HR | Error explícito en preprocessing |
| FastPM sin PID y `central_only_fastpm: true` | Error de config; documentado Fase 0 |
| Artefacto tidal ausente con features tidal | Fail fast en preprocessing |
| Bin con `< min_bin_size` halos | Skip bin en fit; log warning |
| Catálogo vacío post-filtros | ValueError con conteos |

---

## 12. Criterios de verificación (Definition of Done estructural)

1. Todos los requisitos R1–R20 cubiertos por tests o checklist manual documentado.
2. Smoke SIM→FastPM (env) pasa con nueva estructura y mismo Parquet schema que baseline Fase 1.
3. Slurm producción actualizable cambiando solo entrypoints, no rutas de datos en cluster.
4. README repo producto: diagrama §3 del plan + tabla de capas §5 del plan.
5. Issue GitHub de tracking migración (recomendado) enlazado a este spec.

---

## 13. Referencias

| Documento | Ubicación |
| --- | --- |
| Plan estructura | `phd-agents-toolkit/notes/planes-cursor/2026-09-19-haloscope-repo-structure.md` |
| Plan fases 0–6 | `phd-agents-toolkit/notes/planes-cursor/2026-09-17-haloscope-pipeline-implementacion.md` |
| Fase 0 decisiones | `phd-agents-toolkit/notes/planes-cursor/2026-09-17-haloscope-phase0-decisions.md` |
| Config 1ª corrida | `density_field_properties/config/haloscope_run.yaml` |
| Haloscope upstream | https://github.com/computationalAstroUAM/haloscope |
