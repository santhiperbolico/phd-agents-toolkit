# Spec: R(k) y validación con P_gg por propiedad (mstar / OII)

| Campo | Valor |
| --- | --- |
| Repo | `fnl_matching_error_reduction` |
| Rama | `feature/pgg-error-bars-mstar-oii` |
| Plan | [2026-09-14-rk-property-pgg-plan.md](../../../notes/planes-cursor/fnl_variance_reduction_100Pgg/2026-09-14-rk-property-pgg-plan.md) |
| Manifiesto | `configs/manifests/pgg_mstar_oii_selected.csv` (96 jobs) |

## Entrada

- Manifiesto CSV: `job_id`, `object`, `sam`, `property_key`, `bin_lo`, `bin_hi`, `filename`, …
- P_gg NPZ en `pgg_base_dir` con claves `k`, `pk`, `shotnoise`, **`ngal`**
- FastPM fnl=0 en `fastpm_path` (`fof_0.5000/LL-0.200`)
- Config JSON: `configs/pipeline_run_property_pgg_rk.json`

## Salida

**Etapa A** (`output/lower_mass_cut_property_pgg/<Tracer>/<Sam>/`):

- `lower_mass_cut_<property_slug>.json` con `mass_cut_lower`, metadata de propiedad/bin
- `pk_validation_<property_slug>.png`: SAM vs ⟨P(k)⟩ FastPM + banda ±1σ del ensemble
- `lower_mass_cut_property_pgg_summary.json` agregado

**Etapa B** (`output/pk_variance_reduction/property_pgg/<Tracer>/`):

- `R_k_<Sam>_<Tracer>_<property_slug>.txt` y `.png`
- `R_k_property_pgg_summary.json`

## Comportamiento

1. Leer `ngal` del NPZ (`n_gal` o `ngal`; fallback shotnoise solo si faltan ambas).
2. Etapa A: `run_lower_mass_cut_matching` con slug de propiedad; sin plots legacy.
3. Etapa A: media de P(k) augmentado sobre realizaciones FastPM; **una** PNG por job.
4. Gráfica de validación: curva SAM (puntos, sin errorbars) + media FastPM + banda ±1σ.
5. Etapa B: R(k) sintético augmentado; requiere JSON de Etapa A existente.
6. CLI por job: `--config-json`, `--job-id`; piloto con `--n-sims N`.

## Fuera de alcance (descartado en implementación)

- Lectura de `err` del NPZ y errorbars SAM en la PNG de validación.
- `--dry-run` en scripts Etapa A/B.
- Gate automático `validation_status.json` / `--require-validation-passed`.

La revisión humana de PNGs entre etapas es **proceso del grupo**, no código en repo.

## Errores

- `ValueError` si `job_id` no está en el manifiesto.
- `FileNotFoundError` en Etapa B si falta el JSON de Etapa A para ese job.
- `RuntimeError` si el lower mass cut no encuentra candidato válido.

## Edge cases

- Normalizar `galform`/`shark` → `Galform`/`Shark` en paths.
- Slug de propiedad desde suffix del filename (`mstar_9p50000_9p69649`).
- Un `mass_cut_lower` distinto por cada uno de los 96 P_gg.

## Tests

| Requisito | Test |
| --- | --- |
| `ngal` en NPZ | `test_load_external_pgg_npz_reads_ngal_key` |
| Manifest / paths | `test_property_pgg_manifest.py` |
| Plot validación | `test_plot_sam_vs_mean_augmented_pk_writes_png` |
| Orquestador A | `test_run_lower_mass_cut_property_pgg_writes_property_json` |
| Suffix R(k) | `test_build_Rk_basename` |

## Notas de implementación (2026-09-14)

Fase 0 cerrada en rama `feature/pgg-error-bars-mstar-oii`. Slurm:

- `slurm/pipelines/lower_mass_cut_property_pgg_array.slurm` (`--array=1-96`)
- `slurm/pipelines/rk_property_pgg_mstar_oii_array.slurm` (`--array=1-96`)
