# Plan: mass calibration methods (implementation)

**Spec:** [spec.md](./spec.md)
**Repo (product):** `density_field_properties`
**Approach:** Spec-driven + TDD per phase; minimal surface change to Haloscope orchestration.

---

## Overview

```text
Phase 0 ─ Config wiring + dispatcher skeleton (AM unchanged)
Phase 1 ─ Shared halo_matching kernel
Phase 2 ─ matching_1to1 end-to-end
Phase 3 ─ matching_ml (sub-box + regressor registry)
Phase 4 ─ Validation scripts, docs, production JSON presets
```

Each phase ends with: tests green, pre-commit on touched files, example JSON snippet.

---

## Phase 0 — Configuration and dispatch

**Goal:** Read `mass_calibration` from JSON; route to AM only; remove hardcoded
`CALIBRATE_MASS` from pipeline hot path.

**Tasks**

1. Extend `HaloscopeEnrichmentConfig` with `MassCalibrationConfig` dataclass
   (`enabled`, `method`, `matching`, `matching_ml`, column names).
2. Parse from JSON in `load_haloscope_enrichment_config`; map legacy `calibrate_mass`
   if present at top level.
3. Thread `MassCalibrationConfig` through `build_preprocessing_context` /
   `PreprocessingContext` (replace bool-only `calibrate_mass` or extend with nested settings).
4. Refactor `calibrate_lr_mass` → `apply_mass_calibration(lr, hr, config)` with
   `method == abundance_matching` calling existing logic.
5. Unknown method → `ValueError`.

**Tests**

- Config parse: defaults → AM + enabled matches old `CALIBRATE_MASS = True`.
- Dispatch: mock HR/LR → same output as current `calibrate_lr_mass`.

**Files:** `pipelines/config.py`, `preprocessing/context.py`, `mass_calibration.py`,
`haloscope_enrichment.py`, `run_defaults.py` (deprecate constant or mirror default only).

**Exit criteria:** All existing preprocessing tests pass; no behaviour change for default JSON.

---

## Phase 1 — Halo matching kernel

**Goal:** Pure function(s) implementing Forero §3.1, reusable by methods 2 and 3.

**Tasks**

1. Add `preprocessing/halo_matching.py`:
   - Inputs: HR/LR DataFrames (positions, masses), box size, matching hyperparameters.
   - Outputs: table of pairs `(lr_index, hr_index, hr_mass)` or sparse assignment
     `lr_index → hr_mass | None`.
   - Periodic `cKDTree` on LR positions (reuse patterns from `n_halos_env.py`).
2. Unit tests with **tiny synthetic catalogs** (known geometry, forced conflicts).
3. Property test: at most one HR mass per LR after iteration; matched masses equal HR `M200b`.

**Non-goals:** No ML, no sub-box, no pipeline wiring yet.

**Exit criteria:** ≥95% coverage on matching module; documented complexity acceptable for
1e6 halos (benchmark note in docstring, no optimization yet).

---

## Phase 2 — `matching_1to1`

**Goal:** Full-sample matching; write `M200b_cal` and optional trace columns.

**Tasks**

1. Implement `apply_matching_1to1` in `mass_calibration.py` (or sibling module).
2. Wire dispatcher branch `matching_1to1`.
3. Unmatched LR → `M200b_cal = NaN` (fixed; no config).
4. Update `validate_lr_target_table` if NaN masses allowed (Haloscope bins skip NaN —
   confirm in `predict_models` / bin mask).
5. Align `config/haloscope_run.yaml` with three methods.

**Tests**

- Integration via `build_feature_tables` with synthetic HR/LR.
- Schema: `M200b_cal` present when enabled; unmatched NaN count matches expectation.

**Exit criteria:** Smoke config template `config/haloscope_run_matching_1to1_smoke.json`
(document paths only, no cluster paths required for CI).

---

## Phase 3 — `matching_ml`

**Goal:** Train on train sub-box; predict full LR; configurable regressor.

**Tasks**

1. Add `preprocessing/mass_calibration_ml.py`:
   - `mask_subbox(df, subbox, box_size)` with periodic wrap if needed.
   - Build `(X, y_keep, y_log_m_hr)` from matching labels on train LR/HR subset.
   - `RegressorFactory` from `regressor.type` + `params`.
   - `fit_and_predict` / `load_and_predict` with joblib.
2. Dispatcher branch `matching_ml`.
3. Optional dependency: `xgboost` guarded by import; skip XGB tests in CI if not installed
   (pytest marker `@pytest.mark.optional_xgb`).
4. Feature builder: map config `ml_features` to columns (including derived log columns).

**Tests**

- Factory returns sklearn RF with 2 outputs.
- Sub-box excludes halos outside bounds.
- Saved model reload reproduces predictions on fixed seed data.

**Exit criteria:** Fiducial Forero-like RF params in example JSON; document `keep_threshold: null`
vs `0.99`.

---

## Phase 4 — Validation and production

**Goal:** Scientific sanity on UNIT–FastPM pair (manual / cluster); close implementation.

**Tasks**

1. Script `scripts/validate_mass_calibration.py` (optional): HMF compare raw LR,
   `M200b_cal`, HR; summary JSON (mirror HMF preflight style).
2. Production JSON presets under `config/` for each method.
3. Link validation targets to Forero-Sánchez et al. (2022) figures (see spec References).
4. Spec **accepted** (2026-09-28); mark this plan complete when Phase 0–3 merge in product repo.

**Cluster / data:** Not required for CI; document Slurm one-liner using existing `slurm/` patterns.

---

## Dependency notes

| Package | Phase | Required |
| --- | --- | --- |
| `scikit-learn` | 3 | Yes (likely already in env) |
| `joblib` | 3 | Yes |
| `xgboost` | 3 | Optional |

Add to `environment.yml` only when Phase 3 merges XGBoost tests into default env.

---

## Test map (spec → tests)

| Spec requirement | Test module (planned) |
| --- | --- |
| AM unchanged | `test_mass_calibration.py` (existing) |
| Config parse | `test_haloscope_config_mass_calibration.py` |
| Matching kernel | `test_halo_matching.py` |
| matching_1to1 | `test_mass_calibration_matching.py` |
| matching_ml | `test_mass_calibration_ml.py` |
| Feature table integration | extend `test_feature_table.py` |

---

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Matching O(N_HR × k) slow on full Gpc³ | Phase 1 benchmark; optional spatial tiling later (YAGNI) |
| Column names differ Rockstar vs hlist | Catalog loader mapping table in spec appendix (Phase 2) |
| Many NaN after 1:1 (expected for unmatched LR) | HMF / validate script; Haloscope only on matched subset |
| XGBoost not in conda env | Optional extra; sklearn sufficient for v1 |

---

## Suggested branch / PR split

1. PR1: Phase 0 + Phase 1 (config + matching kernel).
2. PR2: Phase 2 (`matching_1to1`).
3. PR3: Phase 3 (`matching_ml` + joblib).
4. PR4: Phase 4 validation script + config presets.

Keeps reviews small and bisect-friendly.

---

## Decisions (2026-09-28)

| Topic | Decision |
| --- | --- |
| IC / paired simulations | Document only; **no** runtime IC preflight in calibration code |
| `max_*_halos` smoke subsample | **No** warnings or extra config |
| Unmatched LR in `matching_1to1` | **`M200b_cal = NaN`**; excluded from Haloscope bins |
| Calibrated mass on match | **HR** `M200b` assigned to matched LR |
| `matching_1to1` execution | In-process matching on loaded catalogs (no cached pair table in v1) |
