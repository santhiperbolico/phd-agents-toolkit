# Haloscope SIM → FastPM: decisiones de Fase 0 y alcance de verificaciones

| Campo | Valor |
| --- | --- |
| Repo producto | `density_field_properties` |
| Fecha cierre Fase 0 | 2026-09-17 |
| Plan maestro | [`2026-09-17-haloscope-pipeline-implementacion.md`](2026-09-17-haloscope-pipeline-implementacion.md) |
| Referencia científica | Ramakrishnan et al. 2025; calibración masas → Ap. C + Adame et al. 2024 Sect. 4.1 |
| Config 1ª corrida | `density_field_properties/config/haloscope_run.yaml` |

Este documento cierra la **Fase 0 (preflight)** del pipeline Haloscope y fija el alcance de
cada verificación. Con esto se puede iniciar la **Fase 1** (pipeline `env` en producción con
métricas y artefactos).

---

## 1. Resumen ejecutivo

| Punto | Tema | Estado | Decisión |
| --- | --- | --- | --- |
| **H0.1** | Configuración de catálogos y filtros | Cerrado | Ver §2 y `haloscope_run.yaml` |
| **H0.2** | Compatibilidad de ICs / semillas | Cerrado | Mismas fases (DM r(k) ≈ 1 a gran escala) |
| **H0.3** | ¿Calibrar masas? | Cerrado | **Sí** — `CALIBRATE_MASS=True`, abundance matching |
| **H0.4** | Alcance de las verificaciones | Cerrado | Ver §4 |

**Primera corrida de producción:** UNIT hlist (HR) entrena Haloscope; FastPM `rockstar_out_nbody`
(LR) se enriquece con `CALIBRATE_MASS=True`, centrales + `M ≥ 20 m_p` en SIM, **z = 0** (a = 1).

---

## 2. H0.1 — Configuración de la primera ejecución

### 2.1 Simulación de entrenamiento (HR)

| Parámetro | Valor |
| --- | --- |
| Simulación | `fixedAmp_InvPhase_001` (UNIT) |
| Raíz en Taurus | `/data21/UNITSIM/fixedAmp_InvPhase_001` |
| Catálogo Haloscope | Consistent-trees **hlist** `hlists/hlist_1.00000.list.bz2` |
| Ruta alternativa (mismo dataset) | `/data5/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR/outputs/hlists/hlist_1.00000.list.bz2` |
| Redshift | **z = 0** (scale factor **a = 1**) |
| Box | 1000 Mpc/h |
| Cosmología | Ωm = 0.3089, h = 0.6774 (cabeceras Rockstar) |

El pipeline debe admitir **raíz SIM editable**; el YAML fija el default de la 1ª corrida.

### 2.2 Simulación objetivo (LR)

| Parámetro | Valor |
| --- | --- |
| Simulación | FastPM MN5 `fastpm_tfm` |
| Catálogo Rockstar | **`rockstar_out_nbody`** (no `rockstar_out_pm`) |
| Fichero | `out_8.list` → snapshot **8** = **a = 1** = **z = 0** |
| Ruta | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_nbody/out_8.list` |
| Box | 1000 Mpc/h |

**Por qué nbody y no pm (Slack DESI, hilo `C0AU9PGRL30`, 2026-09):**

- En **ambos** runs Rockstar recibe el **mismo snapshot de partículas**; la diferencia es el
  **softening length** en Rockstar, adaptado al cálculo de fuerzas (PM en FastPM vs Plummer en
  Gadget/UNIT).
- Adrian/Manuel: el softening PM es físicamente coherente con FastPM; corrieron **ambas**
  versiones para cuantificar el impacto.
- **Decisión práctica:** `rockstar_out_pm` está **truncado en masa** (~2 M halos, vacío por
  debajo de log₁₀ M ≈ 12.4) y **no sirve** para bins de masa ni abundance matching.
  `rockstar_out_nbody` (~30 M halos) es el único catálogo viable para producción.
- **Validación secundaria:** comparar con `rockstar_out_pm` en el solapamiento de masas altas
  (log₁₀ M ≳ 12.4) para estimar sensibilidad al softening.

### 2.3 Filtros de muestra

| Catálogo | Filtro | Notas |
| --- | --- | --- |
| **UNIT hlist (entrenamiento)** | Centrales (`pid == -1`) | Ya aplicado en `load_unit_sim_training_catalog` |
| **UNIT hlist** | `M200b ≥ 20 × m_p` | m_p = 1.2×10⁹ M☉/h → umbral **2.4×10¹⁰ M☉/h** (log₁₀ M ≈ 10.38) |
| **FastPM nbody (objetivo)** | `M200b > 0` hoy; corte 20 m_p en Fase 1 | Los `.list` FastPM **no tienen columna PID** → no se pueden filtrar centrales en FastPM |

**Asimetría documentada:** entrenamiento en **centrales** UNIT; enriquecimiento sobre **todos**
los halos FastPM detectados por Rockstar nbody. Es una limitación del catálogo, no de las ICs.

### 2.4 Calibración de masas

| Parámetro | Valor |
| --- | --- |
| `CALIBRATE_MASS` | **True** (default y 1ª corrida) |
| Método actual | `abundance_match_mass` en `mass_matching.py` — matching monótono por cuantiles de la HMF |
| Método futuro | RF / XGBoost / NGBoost (Ramakrishnan Ap. C; Forero-Sánchez+22) tras matching posicional; ver §6 |

---

## 3. H0.2 — Verificación de condiciones iniciales (semillas)

### 3.1 Prueba canónica (PASS)

**Script:** `density_field_properties/scripts/verify_fastpm_unit_ics.py --tracer dm`
**Artefactos:** `density_field_properties/output/fastpm_unit_seed_check_dm/r_k.png`, `summary.json`

| Campo | Valor |
| --- | --- |
| FastPM DM | `.../output_01/snap_1.0000/1` |
| UNIT DM | `.../DM_PARTICLES/dm_particles_0.5_128.bz2` |
| mediana r(k), k < 0.05 h/Mpc⁻¹ | **0.9997** |
| Veredicto | **`compatible`** |

**Interpretación:** FastPM y UNIT comparten las **mismas fases** en las condiciones iniciales
(mismo volumen, mismo a = 1). La caída de r(k) a k ~ 1 h/Mpc⁻¹ (r ≈ 0.97) refleja evolución
PM vs N-body, **no** semillas distintas.

### 3.2 Prueba que NO usar para ICs

**Script:** `verify_fastpm_unit_ics.py` modo **halos** (default)
**Artefacto:** `output/fastpm_unit_seed_check/summary.json` → mediana r(k) ≈ **0.35**, veredicto `inconclusive`

**Motivo:** deposita catálogos Rockstar distintos (finder, posible mezcla de criterios, subhalos).
**No invalida las ICs.** No usar este run como gate de semillas.

---

## 4. H0.4 — Nota de alcance (qué demuestra cada verificación)

### 4.1 Tabla de alcance

| Verificación | Qué demuestra | Qué NO demuestra |
| --- | --- | --- |
| **DM r(k) a a = 1** | Mismas ICs / fases | Equivalencia de catálogos de halos |
| **HMF UNIT vs FastPM** | Sesgo de **abundancia** y completitud del finder | Equivalencia halo a halo de M200b |
| **Abundance matching** | Alineación global de la función de masa acumulada | Corrección de scatter individual; recuperación de halos perdidos |
| **r(k) con halos Rockstar** | Mezcla finder + selección + deposición CIC | Compatibilidad de semillas |
| **Matching posicional** (futuro) | Scatter M200b en pares con misma IC | Sustituto obligatorio de `CALIBRATE_MASS` en Haloscope |

### 4.2 Origen de las diferencias halo a halo (con ICs compartidas)

1. **Resolución:** UNIT 4096³ (m_p ~ 1.2×10⁹) vs FastPM 2048³ (m_p ~ 10¹⁰).
2. **Solver:** N-body completo (L-Gadget2) vs PM (fuerzas suavizadas, softening efectivo ~ 244 h⁻¹ kpc).
3. **Rockstar:** softening nbody en FastPM ≠ softening PM “ideal” de Adrian; distinto número de halos detectados.
4. **Definición de masa:** M200b Rockstar en ambos, pero medida sobre densidades distintas.
5. **Selección:** centrales en UNIT hlist vs todos los halos en FastPM (sin PID).

Ninguno de estos puntos implica **semillas diferentes**.

### 4.3 Qué afirmamos en la 1ª corrida

- Entrenamos Haloscope en propiedades secundarias (`cv`, `Spin`, `ca`, `ba`) condicionadas a
  **masa (bin)** y **entorno** (`env`), siguiendo Ramakrishnan et al.
- Las masas FastPM usadas para **asignar bin** pasan por **`M200b_cal`** (abundance matching).
- Haloscope **no modifica M200b** como salida; predice secundarias. La calibración afecta solo
  la asignación de bin de masa.
- La validación científica (Fase 4) debe cuantificar si el enriquecimiento mejora distribuciones,
  correlaciones y clustering frente a UNIT — no asumir éxito por ICs compatibles.

---

## 5. H0.3 — Función de masa y necesidad de calibración

### 5.1 Evidencia (a = 1, centrales UNIT, M ≥ 20 m_p)

**Artefactos:** `density_field_properties/output/halo_hmf_a1_central_min20mp/`

| Catálogo | n_halos |
| --- | ---: |
| UNIT Rockstar `out_128p` | 122 157 903 |
| FastPM Rockstar **nbody** | 29 700 481 |
| FastPM Rockstar pm | 1 981 597 (truncado — no producción) |
| FastPM FoF | 15 537 030 |

**Ratios dn/dlog₁₀M (UNIT / FastPM nbody)** en log₁₀ M ∈ [11.5, 13]: mediana **~0.61** →
**calibración necesaria**.

### 5.2 Método adoptado (1ª corrida)

```text
M200b_cal = abundance_match_mass(M200b_fastpm, M200b_unit_train)
```

Implementación: `haloscope/sim_to_fastpm/mass_matching.py`. Activa con `CALIBRATE_MASS=True`
en `pipeline.py`.

### 5.3 Línea futura (no bloqueante)

RF / XGBoost / NGBoost (Ramakrishnan Ap. C) tras matching posicional FastPM↔UNIT.
Ver plan maestro fase H6-ML-mass.

---

## 6. Trabajo futuro explícito (post Fase 0)

| ID | Tema | Prioridad |
| --- | --- | --- |
| **H6-ML-mass** | RF / XGBoost / NGBoost para M200b (Ap. C) | Media — tras 1ª producción |
| **H6-pm-baseline** | Comparar enriquecimiento pm vs nbody (log₁₀ M ≳ 12.4) | Baja |
| **H3-tidal** | Variante tidal (`T/|U|` + anisotropía) — issue #13 | Fase 3 del plan maestro |

---

## 7. Referencias internas

| Documento | Ubicación |
| --- | --- |
| Plan implementación completo | [`2026-09-17-haloscope-pipeline-implementacion.md`](2026-09-17-haloscope-pipeline-implementacion.md) |
| Config 1ª corrida | `density_field_properties/config/haloscope_run.yaml` |
| Rutas FastPM | `density_field_properties/config/fastpm_folders.md` |
| Análisis HMF | [`../analisis/2026-09-06-halo-hmf-unit-fastpm-a1.md`](../analisis/2026-09-06-halo-hmf-unit-fastpm-a1.md) |
| Ap. C RF masa | [`../analisis/2026-09-09-ramakrishnan-apendice-c-rf-masa.md`](../analisis/2026-09-09-ramakrishnan-apendice-c-rf-masa.md) |
| Calibración masas | [`../analisis/2026-08-27-haloscope-mass-calibration.md`](../analisis/2026-08-27-haloscope-mass-calibration.md) |
| Issue #6 análisis | [`../../docs/density_field_properties/issue-6-sim-to-fastpm-haloscope/analysis.md`](../../docs/density_field_properties/issue-6-sim-to-fastpm-haloscope/analysis.md) |
| Sesión Taurus (histórico) | [`2026-08-27-haloscope-taurus.md`](2026-08-27-haloscope-taurus.md) |
| Issue #13 tidal E2E | [`2026-08-31-issue-13-haloscope-e2e-progress.md`](2026-08-31-issue-13-haloscope-e2e-progress.md) |

---

## 8. Historial

| Fecha | Cambio |
| --- | --- |
| 2026-09-17 | Cierre Fase 0; documento movido desde `density_field_properties/docs/` |
| 2026-09-17 | Cierre H0.1–H0.4; nbody; z=0; CALIBRATE_MASS=True; DM ICs verificadas |
