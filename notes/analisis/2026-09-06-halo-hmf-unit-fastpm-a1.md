# Análisis: función de masa de halos UNIT vs FastPM a a = 1

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-06 |
| Estado | primera ejecución completada; segunda en cola (criterio acotado) |
| Repo producto | `density_field_properties` |
| Repo notas | `phd-agents-toolkit` |
| Script | `density_field_properties/scripts/compare_halo_hmf.py` |
| Módulo | `density_field_properties/halo_catalog/mass_function.py` |
| Slurm (todos los halos) | `slurm/compare_halo_hmf/main_compare_halo_hmf.slurm` |
| Slurm (centrals + 20 mp) | `slurm/compare_halo_hmf/main_compare_halo_hmf_central_min20mp.slurm` |

---

## Objetivo

Comparar la **función de masa de halos (HMF)** a **a = 1** entre:

| Etiqueta | Catálogo | Definición de masa |
| --- | --- | --- |
| `unit` | `/data21/UNITSIM/.../ROCKSTAR/out_128p.list.bz2` | M200b (Rockstar) |
| `fastpm_fof` | `.../output_01/fof_1.0000` | M_FOF = N_part × m_p |
| `fastpm_rockstar_pm` | `.../rockstar_out_pm/out_8.list` | M200b (Rockstar sobre PM) |
| `fastpm_rockstar_nbody` | `.../rockstar_out_nbody/out_8.list` | M200b (Rockstar sobre N-body) |

Normalización: `dn/dln M` con volumen `(1000 Mpc/h)³`. Bins log₁₀ M uniformes en **[10.0, 14.5]** con **20 bins**; centros en el **punto medio** de cada bin (`np.histogram`).

---

## Ejecución 1 — todos los halos (`output/halo_hmf_a1/`)

**Job Slurm:** `99216` (completado).

**Opciones:** `--include-subhalos` (sin filtro `PID == -1`).

### Conteos totales

| Catálogo | n_halos |
| --- | ---: |
| UNIT | 173 775 328 |
| FastPM FOF | 15 537 030 |
| Rockstar PM | 1 981 597 |
| Rockstar N-body | 29 864 633 |

### Primer bin con datos (log₁₀ M al centro del bin)

| Catálogo | Primer bin poblado |
| --- | ---: |
| UNIT | 10.11 |
| Rockstar N-body | 10.34 |
| FastPM FOF | 11.46 |
| Rockstar PM | 12.36 |

### Hallazgos principales

#### 1. Rockstar PM vs Rockstar N-body (diferencia extrema)

No es una discrepancia física de la HMF, sino de **completitud del finder**:

- **PM:** Rockstar sobre campo PM suavizado → pocos objetos, **corte alto** (~10^12.3 M☉/h en muestra aleatoria).
- **N-body:** Rockstar sobre snapshot completo → ~15× más halos (30 M vs 2 M).

La curva PM **solo existe en masas altas**; por debajo de log₁₀ M ≈ 12.4 el catálogo está vacío.

#### 2. UNIT vs FastPM (diferencia grande en todo el rango)

Factores combinados:

| Efecto | Impacto |
| --- | --- |
| Resolución / m_p | UNIT resuelve hasta log₁₀ M ~ 9.4; FastPM PM/FOF no llega a la cola baja |
| Definición de masa | M200b (Rockstar) ≠ M_FOF (N_part × m_p) |
| Física PM vs N-body | FastPM suaviza escalas pequeñas; cambia formación y fusión de halos |
| Subhalos incluidos | UNIT con 174 M objetos; la cola baja está dominada por subestructura |
| Box y cosmología | Misma caja 1000 Mpc/h, Ω_m, h compatibles |

En bins donde hay solapamiento (log₁₀ M ≳ 11.5), UNIT sigue **por encima** de N-body/FOF en factor ~2–3.

#### 3. FastPM FOF vs Rockstar

FOF nativo (15.5 M halos) y Rockstar N-body (29.9 M) no coinciden: distinto algoritmo de agrupación, distinta masa (M_FOF vs M200b), distinto umbral efectivo de resolución.

#### 4. Detalle PID en catálogos Rockstar FastPM

Los `out_8.list` de FastPM **no tienen columna `PID`** en el header (55 columnas, tensores de inercia). El filtro de centrales **no aplica** a FastPM Rockstar; sí a UNIT (`PID` en columna 33 de filas de 34 campos). Ver nota [`2026-09-06-fastpm-rockstar-pid-detection.md`](2026-09-06-fastpm-rockstar-pid-detection.md).

---

## Ejecución 2 — criterio acotado (`output/halo_hmf_a1_central_min20mp/`)

**Motivación:** acercar la comparación a un régimen más “apples-to-apples” eliminando la cola de baja masa poco resuelta y los subhalos en UNIT.

**Opciones:**

- Sin `--include-subhalos` → **solo centrales** donde existe `PID == -1` (efectivo en UNIT).
- `--min-m200b-times-mp 20` → M > 20 × m_p con `m_p = 1.2×10⁹` M☉/h (`DM_MASS_PARTICLE_MSUN_H` en `config.py`).
  - Umbral absoluto: **2.4×10¹⁰ M☉/h** (log₁₀ M ≈ 10.38).
- Mismos bins log₁₀ M que la ejecución 1.

**Aplicación del corte de masa por catálogo:**

| Catálogo | Campo filtrado | Interpretación del corte 20 m_p |
| --- | --- | --- |
| UNIT / Rockstar | M200b | Corte de completitud estándar en M200b |
| FastPM FOF | M_FOF = N × m_p | Equivalente a **N_part ≥ 20** en el grupo FOF |
| Rockstar PM / N-body | M200b | Mismo umbral en M200b (sin filtro central posible) |

**Nota:** el header Rockstar de UNIT cita `m_p = 1.247×10⁹` M☉/h; usamos **1.2×10⁹** del config compartido FastPM–UNIT para homogeneizar el corte entre simulaciones.

**Job Slurm:** `99217` (`halo_hmf_central`, enviado 2026-09-06).

**Artefactos esperados:**

- `output/halo_hmf_a1_central_min20mp/hmf_comparison.png`
- `output/halo_hmf_a1_central_min20mp/hmf_comparison.csv`
- `output/halo_hmf_a1_central_min20mp/summary.json`

---

## Interpretación esperada tras la ejecución 2

| Efecto que debería reducirse | Motivo |
| --- | --- |
| Exceso de UNIT en log₁₀ M ≲ 11 | Subhalos eliminados + corte 20 m_p |
| Separación UNIT–N-body en masa intermedia | Menos objetos no resueltos en la cola |
| Curva PM | Seguirá muy baja (catálogo PM incompleto por construcción) |

Lo que **no** desaparecerá:

- Diferencia M200b vs M_FOF.
- Gap PM vs N-body (distintos inputs al finder).
- Sesgo físico PM vs simulación N-body de alta resolución.

---

## Recomendaciones para siguientes pasos

1. Tras completar la ejecución 2, **superponer ambos PNG** y cuantificar ratios UNIT/N-body en log₁₀ M ∈ [11.5, 13].
2. Para Haloscope / matching: valorar **abundance matching** de masas (`mass_matching.py`) además de comparar HMF cruda.
3. No usar **Rockstar PM** como referencia de HMF; tratarlo como catálogo truncado en masa.
4. Comparación más limpia FastPM vs UNIT: solo **Rockstar N-body FastPM** vs **UNIT centrales**, mismo corte 20 m_p, rango log₁₀ M ≥ 11.5.

---

## Referencias de código

```bash
# Ejecución local (smoke)
PYTHONPATH=src python scripts/compare_halo_hmf.py --output-dir output/halo_hmf_a1 --include-subhalos

# Ejecución acotada
PYTHONPATH=src python scripts/compare_halo_hmf.py \
    --min-m200b-times-mp 20 \
    --output-dir output/halo_hmf_a1_central_min20mp
```

```bash
# Slurm
sbatch slurm/compare_halo_hmf/main_compare_halo_hmf_central_min20mp.slurm
```
