# Spec: LR halo mass calibration (Haloscope preprocessing)

**Repository:** [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties)
**Implementation plan:** [implementation-plan.md](./implementation-plan.md)
**Status:** accepted (2026-09-28)
**Scope:** preprocessing step before Haloscope bin fit / predict (`build_feature_tables` →
`calibrate_lr_mass`).
**Reference:** Forero-Sánchez et al. (2022), MNRAS 513, 4318–4331,
[doi:10.1093/mnras/stac1239](https://doi.org/10.1093/mnras/stac1239).

---

## Goal

Support three explicit mass-calibration methods for the LR (FastPM) catalog used in
`run_haloscope_enrichment.py`, selectable from run JSON/YAML. All methods must preserve
the existing contract toward Haloscope:

- HR table keeps raw `M200b` (no calibration on HR).
- LR table receives a calibrated mass column (default name `M200b_cal`) when calibration
  is enabled.
- `build_feature_tables` returns `(hr_table, lr_table, mass_column)` where
  `mass_column` is the LR column used for log-mass bin assignment in
  `enrich_fastpm_catalog`.

---

## Preconditions (matching-based methods)

Methods `matching_1to1` and `matching_ml` assume (operator responsibility, **no IC check in
code**):

1. HR and LR catalogs from **paired initial conditions** (same fixed-amplitude / phase-paired
   setup as UNIT).
2. Positions and masses in the same box frame and units (Mpc/h, Msun/h).
3. Sufficient columns for matching (at minimum `x`, `y`, `z`, `M200b` on both sides; optional
   `id` for traceability).

Implementation validates only data shape and columns (empty catalogs, missing columns), not
simulation pairing. Do not silently fall back to another method if matching fails.

---

## Method catalogue

| Method key | Description | HR catalog at apply time |
| --- | --- | --- |
| `abundance_matching` | Current behaviour: rank-based AM of LR masses onto HR mass function | Not required |
| `matching_1to1` | Full-sample spatial + mass-distance matching; assign **HR** mass to matched LR | Required |
| `matching_ml` | 1:1 matching on a **train sub-box** → supervised labels → ML fit → predict on remaining LR | Not required after model is trained |

When `calibrate_mass` is `false`, skip calibration; `mass_column` is raw `M200b` (unchanged).

---

## Shared outputs and columns

### Required LR columns after calibration (when enabled)

| Column | All methods | Notes |
| --- | --- | --- |
| `M200b_cal` | Yes | Mass used for Haloscope bins on LR |
| `M200b` | Yes | Unchanged raw LR mass |

### Optional columns (matching methods)

| Column | Purpose |
| --- | --- |
| `mass_calib_matched` | Boolean: LR halo received a 1:1 HR partner |
| `mass_calib_hr_id` | HR identifier of partner (if ids exist) |
| `mass_calib_p_keep` | Model-estimated keep probability (`matching_ml` only) |
| `mass_calib_method` | String echo of method key (debug / provenance) |

### Unmatched LR policy (`matching_1to1`)

**Fixed:** unmatched LR halos get `M200b_cal = NaN` (row kept). They are excluded from
Haloscope bin assignment and do not receive secondary-property predictions. No config flag
for `raw` or `drop` in v1.

---

## Method 1: `abundance_matching`

**Behaviour:** identical to `abundance_match_mass` in
`preprocessing/mass_calibration.py`.

**Entrada:** LR and HR `M200b` arrays (full catalogs, no spatial alignment required beyond
same cosmology).

**Salida:** `M200b_cal` on every LR halo; `mass_column` = `M200b_cal`.

**Errores:** empty HR or LR mass sample → `ValueError`.

---

## Method 2: `matching_1to1`

**Behaviour:** For each HR halo (above optional particle/mass cuts), find LR candidates
within `r_match_mpc_h`, rank by combined spatial and mass distance (Forero eq. 1),
resolve HR–HR conflicts on the same LR by preferring smaller spatial separation,
iterate up to `max_matching_iterations`.

**Target mass:** for each **matched LR**, set `M200b_cal` to the **HR partner `M200b`**
(not the LR mass).

**Hyperparameters (configurable, defaults from Forero-Sánchez Table 2):**

| Parameter | Default | Meaning |
| --- | --- | --- |
| `k_neighbours` | 10 | LR candidates per HR (kd-tree) |
| `r_match_mpc_h` | 5.0 | Search radius (Mpc/h) |
| `max_mass_distance` | 0.95 | \|M_LR − M_HR\| / M_HR threshold |
| `max_matching_iterations` | 5 | Conflict-resolution loops |
| `hr_mass_column` | `M200b` | HR mass for matching |
| `lr_mass_column` | `M200b` | LR mass for matching distance |

**Scope:** run matching on the HR/LR sample loaded for the pipeline (including when
`max_sim_halos` / `max_fastpm_halos` truncate for smoke runs). No extra warnings or flags
for subsampling.

**Salida:** matched LR → `M200b_cal`; unmatched → `NaN`; `mass_column` = `M200b_cal` only
if at least one finite calibrated mass exists, else error.

---

## Method 3: `matching_ml`

Two phases: **label construction** (matching on train sub-box) and **inference** (ML on
all LR halos in the run, typically full box minus optional holdout).

### 3.1 Train sub-box

Define an axis-aligned region in comoving Mpc/h:

```json
"train_subbox": {
  "x_min_mpc_h": 0.0,
  "x_max_mpc_h": 500.0,
  "y_min_mpc_h": 0.0,
  "y_max_mpc_h": 1000.0,
  "z_min_mpc_h": 0.0,
  "z_max_mpc_h": 1000.0
}
```

Only HR/LR halos inside this region participate in **matching for labels**. Matching
uses the same algorithm and hyperparameters as `matching_1to1`.

**Training rows (per LR halo in train sub-box):**

| Target | Matched | Unmatched |
| --- | --- | --- |
| `y_log_m_hr` | log10(M200b_HR) | 0.0 (Forero convention) |
| `y_keep` | 1.0 | 0.0 |

Features `X` are LR-side only (see § Feature set).

**Inference region:** default = all LR halos in the pipeline load (full box). Optional
`infer_subbox` restricts prediction (debug only); production default is full LR catalog.

### 3.2 ML model (multi-target regression)

Predict **two targets jointly** (Forero-style):

- `p_keep` ∈ [0, 1] (probability LR should be kept as HR-like).
- `log10_m_hr_pred` (calibrated log mass).

**Model registry (config `regressor`):**

| `regressor.type` | Backend | Notes |
| --- | --- | --- |
| `sklearn_random_forest` | `sklearn.ensemble.RandomForestRegressor` | Fiducial in Forero; multi-output native |
| `sklearn_extra_trees` | `ExtraTreesRegressor` | Same API |
| `xgboost` | `xgboost.XGBRegressor` with `MultiOutputRegressor` **or** native multi-target if enabled | Optional dependency |
| `custom` | Reserved | Plugin path by import string (YAGNI until needed) |

**Shared regressor params (JSON object `regressor.params`):** passed through to the
backend after validation (e.g. `n_estimators`, `max_depth`, `random_state`, `n_jobs`).

**Post-processing:**

1. `M200b_cal = 10 ** log10_m_hr_pred` where prediction is valid.
2. Optional filter: if `keep_threshold` is set (default **null** = no filter, unlike
   Forero 0.99), set `M200b_cal = NaN` where `p_keep < keep_threshold`.

Document default **no threshold** for Haloscope compatibility; Forero-faithful runs set
`keep_threshold: 0.99`.

### 3.3 Model persistence (optional)

| Config | Behaviour |
| --- | --- |
| `model_path` null | Fit on every pipeline run (train sub-box only) |
| `model_path` set, file exists | Load, skip fit, infer only |
| `model_path` set, fit requested | Fit and overwrite (explicit flag `write_model: true`) |

Serialization: `joblib` (`.joblib`) bundling regressor + feature column list + method
metadata + config hash.

### 3.4 Feature set

Config list `ml_features`: column names on **LR table after input-feature attachers**
(e.g. `M200b`, `Vmax`, `env`, tidal columns) **or** dedicated FoF columns mapped in
catalog loaders.

Default feature set (Forero-like, when columns exist):

- `log10_M200b` derived from `M200b`
- `delta` or documented proxy
- `log10_sigma_v` or documented proxy

Missing columns → fail at fit time with `SchemaValidationError` listing gaps.

---

## Configuration schema (JSON)

Nested under `mass_calibration` in Haloscope run config:

```json
{
  "mass_calibration": {
    "enabled": true,
    "method": "abundance_matching",
    "calibrated_column": "M200b_cal",
    "matching": {
      "k_neighbours": 10,
      "r_match_mpc_h": 5.0,
      "max_mass_distance": 0.95,
      "max_matching_iterations": 5
    },
    "matching_ml": {
      "train_subbox": { "x_min_mpc_h": 0.0, "x_max_mpc_h": 500.0,
        "y_min_mpc_h": 0.0, "y_max_mpc_h": 1000.0,
        "z_min_mpc_h": 0.0, "z_max_mpc_h": 1000.0 },
      "ml_features": ["log10_M200b", "delta", "log10_sigma_v"],
      "regressor": {
        "type": "sklearn_random_forest",
        "params": { "n_estimators": 10, "max_depth": 64, "random_state": 42 }
      },
      "keep_threshold": null,
      "model_path": null,
      "write_model": false
    }
  }
}
```

Backward compatibility:

- Top-level legacy `calibrate_mass: true` maps to `mass_calibration.enabled`.
- Absent `method` → `abundance_matching`.
- Replace hardcoded `CALIBRATE_MASS` in `run_defaults.py` with config-driven values.

---

## Integration points (code)

| Location | Change |
| --- | --- |
| `pipelines/config.py` | Parse `mass_calibration` into `HaloscopeEnrichmentConfig` |
| `preprocessing/context.py` | Pass method + params (or nested settings object) |
| `preprocessing/mass_calibration.py` | Dispatch by method; keep AM functions |
| New `preprocessing/halo_matching.py` | 1:1 matching kernel (shared by methods 2 and 3) |
| New `preprocessing/mass_calibration_ml.py` | Sub-box mask, fit, predict, joblib I/O |
| `preprocessing/feature_table.py` | Call dispatcher after feature attach |
| `config/haloscope_run.yaml` | Document three methods |
| Tests | One module per method + matching kernel + config parse |

No change to `run_haloscope_enrichment.py` CLI surface beyond existing `--config`.

---

## Errors

| Condition | Exception |
| --- | --- |
| Unknown `method` | `ValueError` |
| No matched pairs in train sub-box (`matching_ml`) | `ValueError` |
| ML fit with missing feature columns | `SchemaValidationError` |
| All LR `M200b_cal` NaN after calibration | `ValueError` (Haloscope would fail anyway) |

---

## Edge cases

- **Periodic boundaries:** matching kd-tree must use same periodic convention as `env`
  feature (box size from config).
- **Central-only filters:** applied before matching if already in loaders; HR/LR cuts
  must be documented asymmetric (FastPM may include satellites).
- **Duplicate LR assignment:** resolved by iterative HR loop (Forero), not greedy single pass.

---

## Validation (acceptance)

1. **AM:** existing tests in `test_mass_calibration.py` remain green.
2. **matching_1to1:** synthetic periodic box with known pairs → correct `M200b_cal` and
   `mass_calib_matched`.
3. **matching_ml:** train on sub-box of synthetic data; infer on held-out region; RMSE on
   log mass for matched population; `p_keep` higher for matched than unmatched on average.
4. **Integration:** env-only smoke JSON with each method produces enriched Parquet with
   finite predictions (production config separate).

---

## References

- Forero-Sánchez et al. (2022): matching §3.1, AM benchmark §4.1, RF §5.1.
- Current AM: `preprocessing/mass_calibration.py`.
- Haloscope bin column: `haloscope/predict.py` (`mass_column_fastpm`).
