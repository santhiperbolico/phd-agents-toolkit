# Análisis: verificación ICs FastPM ↔ UNIT con r(k) en materia DM

| Campo | Valor |
| --- | --- |
| Fecha inicio | 2026-09-06 |
| Fecha resultado | 2026-09-08 |
| Estado | **completado — ICs compatibles** |
| Repo producto | `density_field_properties` |
| Repo notas | `phd-agents-toolkit` |
| Plan relacionado | [`2026-08-31-fastpm-unit-seed-verification-taurus.md`](../planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md) |
| Script | `density_field_properties/scripts/verify_fastpm_unit_ics.py` |
| Slurm DM | `density_field_properties/slurm/verify_fastpm_unit_ics/main_verify_fastpm_unit_ics_dm.slurm` |
| Salida | `density_field_properties/output/fastpm_unit_seed_check_dm/` |

---

## Objetivo

Confirmar si FastPM (`fastpm_MN5/fastpm_tfm`) y UNIT (`fixedAmp_InvPhase_001`) comparten
condiciones iniciales mediante el coeficiente de correlación esférico

`r(k) = P_cross(k) / sqrt(P_UNIT(k) × P_FastPM(k))`

con trazador **partículas DM** (CIC → δ(x) → FFT), no halos Rockstar.

**Criterio Adrián:** mediana r(k) > **0,9** para k < 0,05 h/Mpc → ICs compatibles.

---

## Motivación del trazador DM

La verificación sobre **halos Rockstar** (jobs 98398–98402, agosto 2026) dio mediana
r(k) ≈ **0,17–0,35** a k bajos y llevó al veredicto «ICs NO compatibles». Ese resultado
era un **falso negativo**: el campo CIC de posiciones de halos mezcla incompletitud del
finder, sesgo PM vs N-body y muestreo asimétrico entre catálogos (2 M vs 174 M filas).

El trazador DM mide directamente la alineación de modos de densidad a a = 1.

---

## Configuración del run

| Parámetro | Valor |
| --- | --- |
| `--tracer` | `dm` |
| `--n-grid` | 256 |
| `--dm-batch-size` | 5_000_000 |
| `--k-low-threshold` | 0,05 h/Mpc |
| Box | 1000 Mpc/h |
| m_p | 1,2×10⁹ M☉/h |

### Rutas DM (a = 1)

| Simulación | Ruta | Formato |
| --- | --- | --- |
| FastPM | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/output_01/snap_1.0000/1` | BigFile (`Position`) |
| UNIT | `/data21/UNITSIM/fixedAmp_InvPhase_001/DM_PARTICLES/dm_particles_0.5_128.bz2` | Texto bzip2 |

Cosmología y box ya verificados en headers Rockstar (31 ago): Ω_m = 0,3089,
Ω_Λ = 0,6911, h = 0,6774.

---

## Resultados

### Resumen numérico

| Métrica | Valor |
| --- | ---: |
| **mediana r(k), k < 0,05 h/Mpc** | **1,000** |
| r(k) en k ≈ 0,1 h/Mpc | ≈ 0,998 |
| r(k) en k ≈ 1,0 h/Mpc | ≈ 0,978 |
| r(k) en k ≈ 1,5 h/Mpc | ≈ 0,965 |
| Veredicto script | **compatible** |

### Figura

`r_k.png` en `output/fastpm_unit_seed_check_dm/` — título «FastPM vs UNIT DM matter
cross-correlation». A grandes escalas r(k) ≈ 1; la caída a k altos es física
(solver PM, resolución, evolución no lineal), no indica seeds distintas.

### Comparación trazadores

| Trazador | mediana r(k), k < 0,05 | Veredicto ICs |
| --- | ---: | --- |
| Halos Rockstar (job 98402, 500k centrales) | 0,17 | Falso negativo |
| Halos Rockstar (post-fix PID, sep) | ≈ 0,35 | Inconcluso |
| **Partículas DM** | **1,000** | **ICs compatibles** |

---

## Interpretación

1. **ICs confirmadas.** Los modos de gran escala (k < 0,05) están perfectamente
   correlacionados → FastPM y UNIT comparten la misma realización de fases iniciales
   (`fixedAmp_InvPhase_001`), coherente con la confirmación de Adrián (31 ago).

2. **Caída a k altos es esperable.** A a = 1 el campo DM ya incluye crecimiento y
   colapso no lineal; el solver PM de FastPM difiere del N-body de UNIT en escalas
   pequeñas. Esto no invalida el matching halo a halo en el régimen de masas
   resueltas.

3. **El bloqueo r(k) = 0,17 queda resuelto.** El diagnóstico correcto para ICs es
   DM, no Rockstar. El matching 1-1 por proximidad puede retomarse.

4. **HMF y scatter M200b.** Las discrepancias UNIT vs FastPM N-body observadas el
   6 sep (nota [`2026-09-06-halo-hmf-unit-fastpm-a1.md`](2026-09-06-halo-hmf-unit-fastpm-a1.md))
   deben atribuirse a finder, definición de masa y resolución, no a seeds distintas.

---

## Veredicto

- **ICs compatibles (DM):** **SÍ**
- **Evidencia:** mediana r(k) = **1,000** en k < 0,05 h/Mpc; n_grid = 256;
  trazador `--tracer dm`
- **ICs compatibles (halos):** NO (trazador inadecuado; no usar para este test)
- **Siguiente paso:** matching posicional en subset; scatter M200b en pares;
  informar a Adrián con figura DM

---

## Artefactos

| Fichero | Descripción |
| --- | --- |
| `output/fastpm_unit_seed_check_dm/r_k.png` | Figura r(k) vs k |
| `output/fastpm_unit_seed_check_dm/r_k.csv` | Tabla numérica |
| `output/fastpm_unit_seed_check_dm/summary.json` | Metadatos + veredicto |
| `output/fastpm_unit_ics_dm.out` / `.log` | Logs Slurm (si aplica) |

---

## Referencias de código

```bash
cd /home/arnes/santiago_arranz/density_field_properties
source src/.venv/bin/activate
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

sbatch slurm/verify_fastpm_unit_ics/main_verify_fastpm_unit_ics_dm.slurm
```

```bash
# Smoke local
python scripts/verify_fastpm_unit_ics.py \
    --tracer dm \
    --n-grid 256 \
    --dm-batch-size 5000000 \
    --output-dir output/fastpm_unit_seed_check_dm
```

---

## Siguientes pasos

1. Compartir figura DM con Adrián (sustituye el veredicto negativo de halos).
2. Implementar matching por proximidad (KD-tree, box periódico) en subset 5k–10k halos.
3. Scatter M200b en pares emparejados → tarea HMF / `CALIBRATE_MASS`.
4. Confirmar criterios Rockstar en `rockstar_pm` vs `rockstar_nbody` (Adrián/Manuel).
