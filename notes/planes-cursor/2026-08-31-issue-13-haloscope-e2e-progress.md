# Issue #13 — progreso E2E Haloscope (tidal inputs)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-08-31 |
| Issue | [#13](https://github.com/computationalAstroUAM/density_field_properties/issues/13) — End-to-end Haloscope workflow tests (Rockstar T/|U| column) |
| Repo de producto | `density_field_properties` |
| Plan padre | [`2026-09-17-haloscope-pipeline-implementacion.md`](2026-09-17-haloscope-pipeline-implementacion.md) (Fase 3) |
| Estado | En progreso — smoke E2E local OK; producción Slurm pendiente |

---

## Resumen

Variante del flujo Haloscope SIM→FastPM que usa como **input features**:

- `t_over_u` — columna Rockstar `T/|U|` (índice 37 en FastPM `.list`, 56 en UNIT hlist)
- `tidal_anisotropy` — columna 6 en `*_halo_environment_descriptors.txt`

Incluye notebook ligero (`QUICK_RUN=True`), CLI, jobs Slurm (smoke + full), tests unitarios y smoke E2E verificado en Taurus.

**Cambios aún sin commit** en `density_field_properties` (working tree local).

---

## Entregables

| Entregable | Ruta | Estado |
| --- | --- | --- |
| Notebook tidal E2E | `notebooks/SIM_to_FASTPM_unitsim_fastpm_mn5_tidal.ipynb` | ✅ |
| Features + merge descriptores | `src/density_field_properties/haloscope/sim_to_fastpm/tidal_features.py` | ✅ |
| Pipeline + assembly bias PDF | `src/density_field_properties/haloscope/sim_to_fastpm/pipeline_tidal.py` | ✅ |
| Config (`TIDAL_INPUT_FEATURES`, smoke paths) | `src/density_field_properties/haloscope/sim_to_fastpm/config.py` | ✅ |
| Carga `t_over_u` en catálogos | `src/density_field_properties/haloscope/sim_to_fastpm/load_catalogs.py` | ✅ |
| CLI smoke / full | `scripts/run_sim_to_fastpm_haloscope_tidal.py` | ✅ |
| Slurm smoke | `slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal_smoke.slurm` | ✅ |
| Slurm producción | `slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal.slurm` | ✅ |
| Tests unitarios | `src/tests/haloscope/test_tidal_features.py` (3 passed) | ✅ |
| Smoke parquet | `output/sim_to_fastpm_haloscope_tidal_smoke/fastpm_out_8_haloscope_tidal_enriched.parquet` | ✅ |

---

## Criterios de aceptación (#13)

| Criterio | Estado |
| --- | --- |
| Procedimiento de test documentado | 🟡 Parcial — notebook §9, docstring del script, esta nota |
| Test automatizado o smoke script | 🟡 Parcial — CLI + unit tests; falta pytest de integración E2E |
| Notas sobre tolerancias vs Rockstar `T/|U|` | ❌ Pendiente |
| Run Slurm catálogo completo | ❌ Script listo, no ejecutado |
| PDF assembly bias en smoke | ❌ Pendiente validar con `--assembly-bias` en Slurm |

---

## Comandos

```bash
cd /home/arnes/santiago_arranz/density_field_properties
conda activate density_field_properties
export PYTHONPATH=src

# Smoke local (QUICK_RUN)
python scripts/run_sim_to_fastpm_haloscope_tidal.py --quick-run --assembly-bias

# Smoke Slurm
sbatch slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal_smoke.slurm

# Producción Slurm
sbatch slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal.slurm
```

---

## Bloqueos / riesgos

1. **Quick run + 1 batch de descriptores:** tras merge por celda CIC quedan muy pocos halos FastPM con `tidal_anisotropy` (~1 en prueba local). Mitigación: `--max-descriptor-batches 3` o subir `SMOKE_MAX_DESCRIPTOR_BATCH_FILES` en `config.py`.
2. **Issue #12:** descriptores tidales deben tener 8 columnas antes de confiar en runs largos.
3. **Sin commit/push** al 2026-08-31.

---

## Siguiente

1. Smoke Slurm con `--assembly-bias` → revisar PDF + parquet.
2. Pytest de integración E2E (skip si no hay catálogos en cluster).
3. Run producción cuando `squeue` libre y descriptores validados.
4. Check numérico `t_over_u` cargado vs columna Rockstar en halo de referencia.

---

## Comentario para GitHub (copiar/pegar)

Bloque en inglés listo para pegar en [#13](https://github.com/computationalAstroUAM/density_field_properties/issues/13):

```markdown
## Progress update (2026-08-31)

Tidal-input variant of the Haloscope SIM→FastPM workflow is implemented and smoke-tested locally on Taurus. Input features: Rockstar **`T/|U|`** (`t_over_u`) and precomputed **`tidal_anisotropy`** from halo environment descriptor batches.

### Done

| Item | Path |
| --- | --- |
| E2E notebook (`QUICK_RUN=True`, assembly-bias section) | `notebooks/SIM_to_FASTPM_unitsim_fastpm_mn5_tidal.ipynb` |
| Descriptor load + grid merge | `haloscope/sim_to_fastpm/tidal_features.py` |
| Pipeline + assembly-bias PDF helper | `haloscope/sim_to_fastpm/pipeline_tidal.py` |
| CLI (`--quick-run`, `--assembly-bias`) | `scripts/run_sim_to_fastpm_haloscope_tidal.py` |
| Slurm smoke / full | `slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal_smoke.slurm`, `..._tidal.slurm` |
| Unit tests (3 passed) | `src/tests/haloscope/test_tidal_features.py` |
| Smoke output | `output/sim_to_fastpm_haloscope_tidal_smoke/fastpm_out_8_haloscope_tidal_enriched.parquet` |

Rockstar `T/|U|` column indices: FastPM `.list` → 37; UNIT hlist → 56.

### Acceptance criteria status

- **Documented test procedure:** partial (notebook §9 + script docstring + plan note in `phd-agents-toolkit`)
- **Automated / scripted smoke:** partial (CLI + unit tests; dedicated integration pytest still TODO)
- **Numerical tolerances vs Rockstar `T/|U|`:** not documented yet
- **Full-catalog Slurm run:** script ready, not submitted yet

### How to run

```bash
cd density_field_properties
export PYTHONPATH=src
python scripts/run_sim_to_fastpm_haloscope_tidal.py --quick-run --assembly-bias
# or: sbatch slurm/sim_to_fastpm/main_sim_to_fastpm_haloscope_tidal_smoke.slurm
```

### Known limitations

- With `QUICK_RUN` and a single descriptor batch, grid-cell merge leaves very few FastPM halos with valid `tidal_anisotropy` (~1 in local smoke). Use `--max-descriptor-batches 3` for a more representative smoke.
- Changes are in the local working tree (not committed yet).
- Depends on tidal descriptors having 8 columns (#12).

### Next steps

1. Slurm smoke with `--assembly-bias` and review PDF + parquet.
2. Add integration pytest (fixed subset, skip if catalogs missing).
3. Full Slurm run when queue is free and tidal descriptors are validated.
4. Document explicit `t_over_u` vs Rockstar column check on a reference halo.
```
