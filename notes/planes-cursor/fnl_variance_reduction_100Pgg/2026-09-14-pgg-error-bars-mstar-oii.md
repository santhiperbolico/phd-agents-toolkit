# Plan Cursor: barras de error con P_gg (mstar y OII)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-14 |
| Estado | Fase 0 implementada |
| Spec | [spec.md](../../../docs/fnl_matching_error_reduction/pgg-error-bars-mstar-oii/spec.md) |
| Repo de producto | `fnl_matching_error_reduction` |
| Rama | `feature/pgg-error-bars-mstar-oii` |
| Issue / spec | Petición del grupo (Olivia/Miguel) — reducción de errores en plots |

**Anexos:**

- [Plan de implementación R(k)](./2026-09-14-rk-property-pgg-plan.md)
- [Catálogo completo + criterio de selección](./2026-09-14-pgg-error-bars-mstar-oii-catalog.md)
- [Lista de rutas seleccionadas (96)](./2026-09-14-pgg-error-bars-mstar-oii-paths.txt)
- [Manifiesto CSV](./2026-09-14-pgg-error-bars-mstar-oii-manifest.csv)

## Objetivo

Calcular barras de error para los plots de b_φ usando los espectros `P_gg`
precomputados, empezando por **mstar** y **OII** (`log10_OII_lum`) en el
**primer, medio y último** bin de cada propiedad (3 de 5), para todos los
tracers y ambos SAMs.

## Contexto (petición del grupo)

- Espectros en `/home/olivia/Miguel/GP_codes_SAM/clustering_and_bool_lumy/b_phi_priors/P_gg/`
- Bins de propiedades en `.../property_bins/nbinEQ5_LRG3_{galform,shark}.pkl`
  (mismos edges para todos los tracers; verificado en disco para LRG3 galform).
- Simulación: `fnl100`
- Estrategia: 3 bins representativos por propiedad en lugar de los 5 completos.
- `L_bol` queda pendiente hasta que terminen de regenerarse los nuevos bins.

### Mapeo tracer → snapshot SAM y redshift

| Tracer | n (iz) | z | a |
|--------|--------|---|-----|
| QSO-6 | 65 | 3.037 | 0.2477 |
| QSO-5 | 74 | 2.308 | 0.3023 |
| QSO-4 | 81 | 1.833 | 0.353 |
| QSO | 87 | 1.48 | 0.4032 |
| ELG | 90 | 1.321 | 0.4309 |
| LRG3 | 98 | 0.9436 | 0.5145 |
| LRG2 | 104 | 0.7018 | 0.5876 |
| LRG1 | 109 | 0.5232 | 0.6565 |

### Bins seleccionados (nbinEQ5)

| Propiedad | Clave en pickle / filename | Bins usados | Edges (LRG3 galform) |
|-----------|---------------------------|-------------|----------------------|
| mstar | `mstar` | 1º, 3º, 5º de 5 | [9.50000, 9.69649], [9.90654, 10.15730], [10.50350, 12.00000] |
| OII | `log10_OII_lum` | 1º, 3º, 5º de 5 | [39.00000, 39.64443], [40.10221, 40.56051], [41.08099, 44.00000] |

### Convención de nombre de fichero

```text
P_gg_<OBJ>_<simul>_<sam>_<prop>_<bin_val_0>_<bin_val_1>.npz
```

- `<OBJ>`: LRG1, LRG2, LRG3, ELG, QSO, QSO-4, QSO-5, QSO-6
- `<simul>`: `fnl100`
- `<sam>`: `galform` o `shark`
- `<prop>`: `mstar` o `log10_OII_lum`
- `<bin_val_*>`: valor del edge con 5 decimales y `.` sustituido por `p`
  (p. ej. `9.69648738` → `9p69649`)

**Total de jobs en esta fase:** 96 (8 tracers × 2 SAMs × 2 propiedades × 3 bins)

**Verificación en disco (2026-09-14):** los 96 ficheros existen en `P_gg/`.

## Alcance

- **Incluido:** mstar y OII; bins 1º, 3º y 5º; galform y shark; 8 tracers.
- **Fuera de alcance (fase 1):** `L_bol` y el resto de propiedades; bins 2º y 4º.

## Pasos

Ver detalle en [2026-09-14-rk-property-pgg-plan.md](./2026-09-14-rk-property-pgg-plan.md).

0. **Fase 0:** infraestructura de código (fix `ngal`, manifest, paths, plot
   validación SAM vs ⟨P(k)⟩ FastPM, orquestadores, configs, Slurm) — **hecho**
   en rama `feature/pgg-error-bars-mstar-oii`.
1. **Etapa A:** `lower_mass_cut` por P_gg → JSON + 1 PNG (SAM puntos vs ⟨P(k)⟩
   FastPM + banda ±1σ).
2. **Revisión** manual de espectros con el grupo (sin gate automático en repo).
3. **Etapa B:** R(k) tras revisión; requiere JSON de Etapa A por job.
4. Extender a `L_bol` cuando estén listos los nuevos bins.

## Criterios de aceptación

- [x] Infraestructura Fase 0 en repo de producto (tests + pre-commit).
- [ ] Los 96 jobs de la tabla 1 están definidos y ejecutables en cluster.
- [ ] Piloto LRG3 galform mstar produce errores coherentes.
- [ ] Batch Slurm documentado en el repo de producto.

## Tabla 1 — Jobs a ejecutar

Cada fila es un cálculo de error de plot independiente. El snapshot FastPM
corresponde al tracer indicado.

| # | Object | Snapshot | SAM | Property | Bin | P_gg file |
|---|--------|----------|-----|----------|-----|-----------|
| 1 | LRG1 | 109 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG1_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 2 | LRG1 | 109 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG1_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 3 | LRG1 | 109 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG1_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 4 | LRG1 | 109 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG1_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 5 | LRG1 | 109 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG1_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 6 | LRG1 | 109 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_LRG1_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 7 | LRG1 | 109 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG1_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 8 | LRG1 | 109 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG1_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 9 | LRG1 | 109 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG1_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 10 | LRG1 | 109 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG1_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 11 | LRG1 | 109 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG1_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 12 | LRG1 | 109 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_LRG1_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 13 | LRG2 | 104 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG2_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 14 | LRG2 | 104 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG2_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 15 | LRG2 | 104 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG2_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 16 | LRG2 | 104 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG2_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 17 | LRG2 | 104 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG2_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 18 | LRG2 | 104 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_LRG2_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 19 | LRG2 | 104 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG2_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 20 | LRG2 | 104 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG2_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 21 | LRG2 | 104 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG2_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 22 | LRG2 | 104 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG2_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 23 | LRG2 | 104 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG2_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 24 | LRG2 | 104 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_LRG2_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 25 | LRG3 | 098 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG3_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 26 | LRG3 | 098 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG3_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 27 | LRG3 | 098 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG3_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 28 | LRG3 | 098 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG3_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 29 | LRG3 | 098 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG3_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 30 | LRG3 | 098 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_LRG3_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 31 | LRG3 | 098 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_LRG3_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 32 | LRG3 | 098 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_LRG3_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 33 | LRG3 | 098 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_LRG3_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 34 | LRG3 | 098 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_LRG3_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 35 | LRG3 | 098 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_LRG3_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 36 | LRG3 | 098 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_LRG3_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 37 | ELG | 090 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_ELG_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 38 | ELG | 090 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_ELG_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 39 | ELG | 090 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_ELG_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 40 | ELG | 090 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_ELG_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 41 | ELG | 090 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_ELG_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 42 | ELG | 090 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_ELG_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 43 | ELG | 090 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_ELG_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 44 | ELG | 090 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_ELG_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 45 | ELG | 090 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_ELG_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 46 | ELG | 090 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_ELG_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 47 | ELG | 090 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_ELG_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 48 | ELG | 090 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_ELG_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 49 | QSO | 087 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 50 | QSO | 087 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 51 | QSO | 087 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 52 | QSO | 087 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 53 | QSO | 087 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 54 | QSO | 087 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_QSO_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 55 | QSO | 087 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 56 | QSO | 087 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 57 | QSO | 087 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 58 | QSO | 087 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 59 | QSO | 087 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 60 | QSO | 087 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_QSO_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 61 | QSO-4 | 081 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-4_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 62 | QSO-4 | 081 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-4_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 63 | QSO-4 | 081 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-4_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 64 | QSO-4 | 081 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 65 | QSO-4 | 081 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 66 | QSO-4 | 081 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 67 | QSO-4 | 081 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-4_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 68 | QSO-4 | 081 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-4_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 69 | QSO-4 | 081 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-4_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 70 | QSO-4 | 081 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 71 | QSO-4 | 081 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 72 | QSO-4 | 081 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 73 | QSO-5 | 074 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-5_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 74 | QSO-5 | 074 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-5_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 75 | QSO-5 | 074 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-5_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 76 | QSO-5 | 074 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 77 | QSO-5 | 074 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 78 | QSO-5 | 074 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 79 | QSO-5 | 074 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-5_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 80 | QSO-5 | 074 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-5_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 81 | QSO-5 | 074 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-5_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 82 | QSO-5 | 074 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 83 | QSO-5 | 074 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 84 | QSO-5 | 074 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 85 | QSO-6 | 065 | galform | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-6_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 86 | QSO-6 | 065 | galform | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-6_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 87 | QSO-6 | 065 | galform | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-6_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 88 | QSO-6 | 065 | galform | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 89 | QSO-6 | 065 | galform | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 90 | QSO-6 | 065 | galform | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 91 | QSO-6 | 065 | shark | mstar | 1º (bajo) [9.5, 9.696] | `P_gg_QSO-6_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 92 | QSO-6 | 065 | shark | mstar | 3º (medio) [9.907, 10.16] | `P_gg_QSO-6_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 93 | QSO-6 | 065 | shark | mstar | 5º (alto) [10.5, 12] | `P_gg_QSO-6_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 94 | QSO-6 | 065 | shark | OII | 1º (bajo) [39, 39.64] | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 95 | QSO-6 | 065 | shark | OII | 3º (medio) [40.1, 40.56] | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 96 | QSO-6 | 065 | shark | OII | 5º (alto) [41.08, 44] | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |

## Tabla 2 — Catálogo de ficheros P_gg

Descomposición del nombre según el patrón acordado.

| # | OBJ | simul | sam | prop | bin_val_0 | bin_val_1 | filename |
|---|-----|-------|-----|------|-----------|-----------|----------|
| 1 | LRG1 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_LRG1_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 2 | LRG1 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_LRG1_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 3 | LRG1 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_LRG1_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 4 | LRG1 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG1_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 5 | LRG1 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG1_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 6 | LRG1 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG1_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 7 | LRG1 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_LRG1_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 8 | LRG1 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_LRG1_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 9 | LRG1 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_LRG1_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 10 | LRG1 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG1_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 11 | LRG1 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG1_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 12 | LRG1 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG1_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 13 | LRG2 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_LRG2_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 14 | LRG2 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_LRG2_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 15 | LRG2 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_LRG2_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 16 | LRG2 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG2_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 17 | LRG2 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG2_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 18 | LRG2 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG2_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 19 | LRG2 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_LRG2_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 20 | LRG2 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_LRG2_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 21 | LRG2 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_LRG2_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 22 | LRG2 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG2_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 23 | LRG2 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG2_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 24 | LRG2 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG2_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 25 | LRG3 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_LRG3_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 26 | LRG3 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_LRG3_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 27 | LRG3 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_LRG3_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 28 | LRG3 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG3_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 29 | LRG3 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG3_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 30 | LRG3 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG3_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 31 | LRG3 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_LRG3_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 32 | LRG3 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_LRG3_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 33 | LRG3 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_LRG3_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 34 | LRG3 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_LRG3_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 35 | LRG3 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_LRG3_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 36 | LRG3 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_LRG3_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 37 | ELG | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_ELG_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 38 | ELG | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_ELG_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 39 | ELG | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_ELG_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 40 | ELG | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_ELG_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 41 | ELG | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_ELG_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 42 | ELG | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_ELG_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 43 | ELG | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_ELG_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 44 | ELG | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_ELG_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 45 | ELG | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_ELG_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 46 | ELG | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_ELG_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 47 | ELG | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_ELG_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 48 | ELG | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_ELG_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 49 | QSO | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_QSO_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 50 | QSO | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_QSO_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 51 | QSO | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_QSO_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 52 | QSO | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 53 | QSO | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 54 | QSO | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 55 | QSO | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_QSO_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 56 | QSO | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_QSO_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 57 | QSO | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_QSO_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 58 | QSO | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 59 | QSO | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 60 | QSO | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 61 | QSO-4 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_QSO-4_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 62 | QSO-4 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_QSO-4_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 63 | QSO-4 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_QSO-4_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 64 | QSO-4 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 65 | QSO-4 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 66 | QSO-4 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-4_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 67 | QSO-4 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_QSO-4_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 68 | QSO-4 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_QSO-4_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 69 | QSO-4 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_QSO-4_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 70 | QSO-4 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 71 | QSO-4 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 72 | QSO-4 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-4_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 73 | QSO-5 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_QSO-5_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 74 | QSO-5 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_QSO-5_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 75 | QSO-5 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_QSO-5_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 76 | QSO-5 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 77 | QSO-5 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 78 | QSO-5 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-5_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 79 | QSO-5 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_QSO-5_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 80 | QSO-5 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_QSO-5_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 81 | QSO-5 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_QSO-5_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 82 | QSO-5 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 83 | QSO-5 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 84 | QSO-5 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-5_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |
| 85 | QSO-6 | fnl100 | galform | mstar | 9p50000 | 9p69649 | `P_gg_QSO-6_fnl100_galform_mstar_9p50000_9p69649.npz` |
| 86 | QSO-6 | fnl100 | galform | mstar | 9p90654 | 10p15730 | `P_gg_QSO-6_fnl100_galform_mstar_9p90654_10p15730.npz` |
| 87 | QSO-6 | fnl100 | galform | mstar | 10p50350 | 12p00000 | `P_gg_QSO-6_fnl100_galform_mstar_10p50350_12p00000.npz` |
| 88 | QSO-6 | fnl100 | galform | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_39p00000_39p64443.npz` |
| 89 | QSO-6 | fnl100 | galform | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_40p10221_40p56051.npz` |
| 90 | QSO-6 | fnl100 | galform | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-6_fnl100_galform_log10_OII_lum_41p08099_44p00000.npz` |
| 91 | QSO-6 | fnl100 | shark | mstar | 9p50000 | 9p69649 | `P_gg_QSO-6_fnl100_shark_mstar_9p50000_9p69649.npz` |
| 92 | QSO-6 | fnl100 | shark | mstar | 9p90654 | 10p15730 | `P_gg_QSO-6_fnl100_shark_mstar_9p90654_10p15730.npz` |
| 93 | QSO-6 | fnl100 | shark | mstar | 10p50350 | 12p00000 | `P_gg_QSO-6_fnl100_shark_mstar_10p50350_12p00000.npz` |
| 94 | QSO-6 | fnl100 | shark | log10_OII_lum | 39p00000 | 39p64443 | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_39p00000_39p64443.npz` |
| 95 | QSO-6 | fnl100 | shark | log10_OII_lum | 40p10221 | 40p56051 | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_40p10221_40p56051.npz` |
| 96 | QSO-6 | fnl100 | shark | log10_OII_lum | 41p08099 | 44p00000 | `P_gg_QSO-6_fnl100_shark_log10_OII_lum_41p08099_44p00000.npz` |

## Artefactos generados

| Fichero | Contenido |
| --- | --- |
| [catalog.md](./2026-09-14-pgg-error-bars-mstar-oii-catalog.md) | 160 ficheros con nomenclatura `P_gg_*`; columna **Seleccionado** (sí/no) |
| [paths.txt](./2026-09-14-pgg-error-bars-mstar-oii-paths.txt) | Rutas absolutas de los 96 ficheros seleccionados |
| [manifest.csv](./2026-09-14-pgg-error-bars-mstar-oii-manifest.csv) | Manifiesto machine-readable de los jobs seleccionados |

## Notas de sesión

- **2026-09-14:** Rama `feature/pgg-error-bars-mstar-oii` creada. Inventario de 96
  ficheros P_gg verificado en disco. Plan y tablas documentados.
- **2026-09-14:** Fase 0 implementada; spec actualizada (sin errorbars SAM,
  `--dry-run` ni gate `validation_status.json`).

## Resultado

Fase 0 lista en repo de producto. Pendiente: piloto Etapa A, batch 96 y Etapa B.
