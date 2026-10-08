# Validación match_bins — reducción R(k) property P_gg

Criterio automático inicial: `opt_value` (χ² reducido en [`fit_k_min`, `fit_k_max`]) ≤ 1.0.
Clasificación final **revisada manualmente** inspeccionando las gráficas `pk_ratio`
y `pk_comparison` en `match_bins_power_spectrum/`.

La reducción de varianza R(k) solo es interpretable para casos válidos.

**Total:** 96 casos — **34 válidos**, **62 no válidos**.

### Casos reclasificados a no válidos tras revisión manual (13)

Tenían `opt_value` ≤ 1.0 pero el ratio P(k) FastPM/SAM no es aceptable visualmente:

- `ELG_Galform_mstar_10p50350_12p00000` (opt = —)
- `ELG_Galform_mstar_9p90654_10p15730` (opt = —)
- `LRG1_Galform_mstar_10p50350_12p00000` (opt = —)
- `LRG2_Galform_mstar_10p50350_12p00000` (opt = —)
- `LRG3_Galform_mstar_10p50350_12p00000` (opt = —)
- `QSO-4_Galform_mstar_10p50350_12p00000` (opt = —)
- `QSO-4_Galform_mstar_9p90654_10p15730` (opt = —)
- `QSO-5_Galform_mstar_9p50000_9p69649` (opt = —)
- `QSO-5_Galform_mstar_9p90654_10p15730` (opt = —)
- `QSO-5_Shark_mstar_10p50350_12p00000` (opt = —)
- `QSO-6_Shark_mstar_10p50350_12p00000` (opt = —)
- `QSO-6_Shark_mstar_9p50000_9p69649` (opt = —)
- `QSO_Galform_mstar_10p50350_12p00000` (opt = —)

## Casos válidos

| case_id | tracer | SAM | propiedad | opt_value |
|---------|--------|-----|-----------|-----------|
| ELG_Galform_log10_OII_lum_41p08099_44p00000 | ELG | Galform | log10_OII_lum_41p08099_44p00000 | — |
| ELG_Galform_mstar_9p50000_9p69649 | ELG | Galform | mstar_9p50000_9p69649 | — |
| ELG_Shark_log10_OII_lum_39p00000_39p64443 | ELG | Shark | log10_OII_lum_39p00000_39p64443 | — |
| ELG_Shark_mstar_10p50350_12p00000 | ELG | Shark | mstar_10p50350_12p00000 | — |
| ELG_Shark_mstar_9p50000_9p69649 | ELG | Shark | mstar_9p50000_9p69649 | — |
| ELG_Shark_mstar_9p90654_10p15730 | ELG | Shark | mstar_9p90654_10p15730 | — |
| LRG1_Galform_mstar_9p50000_9p69649 | LRG1 | Galform | mstar_9p50000_9p69649 | — |
| LRG1_Galform_mstar_9p90654_10p15730 | LRG1 | Galform | mstar_9p90654_10p15730 | — |
| LRG1_Shark_mstar_10p50350_12p00000 | LRG1 | Shark | mstar_10p50350_12p00000 | — |
| LRG1_Shark_mstar_9p50000_9p69649 | LRG1 | Shark | mstar_9p50000_9p69649 | — |
| LRG1_Shark_mstar_9p90654_10p15730 | LRG1 | Shark | mstar_9p90654_10p15730 | — |
| LRG2_Galform_mstar_9p50000_9p69649 | LRG2 | Galform | mstar_9p50000_9p69649 | — |
| LRG2_Galform_mstar_9p90654_10p15730 | LRG2 | Galform | mstar_9p90654_10p15730 | — |
| LRG2_Shark_mstar_10p50350_12p00000 | LRG2 | Shark | mstar_10p50350_12p00000 | — |
| LRG2_Shark_mstar_9p50000_9p69649 | LRG2 | Shark | mstar_9p50000_9p69649 | — |
| LRG2_Shark_mstar_9p90654_10p15730 | LRG2 | Shark | mstar_9p90654_10p15730 | — |
| LRG3_Galform_mstar_9p50000_9p69649 | LRG3 | Galform | mstar_9p50000_9p69649 | — |
| LRG3_Galform_mstar_9p90654_10p15730 | LRG3 | Galform | mstar_9p90654_10p15730 | — |
| LRG3_Shark_mstar_10p50350_12p00000 | LRG3 | Shark | mstar_10p50350_12p00000 | — |
| LRG3_Shark_mstar_9p90654_10p15730 | LRG3 | Shark | mstar_9p90654_10p15730 | — |
| QSO-4_Shark_log10_OII_lum_39p00000_39p64443 | QSO-4 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| QSO-4_Shark_mstar_10p50350_12p00000 | QSO-4 | Shark | mstar_10p50350_12p00000 | — |
| QSO-4_Shark_mstar_9p90654_10p15730 | QSO-4 | Shark | mstar_9p90654_10p15730 | — |
| QSO-5_Shark_log10_OII_lum_39p00000_39p64443 | QSO-5 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| QSO-5_Shark_mstar_9p50000_9p69649 | QSO-5 | Shark | mstar_9p50000_9p69649 | — |
| QSO-5_Shark_mstar_9p90654_10p15730 | QSO-5 | Shark | mstar_9p90654_10p15730 | — |
| QSO-6_Shark_log10_OII_lum_39p00000_39p64443 | QSO-6 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| QSO_Galform_log10_OII_lum_41p08099_44p00000 | QSO | Galform | log10_OII_lum_41p08099_44p00000 | — |
| QSO_Galform_mstar_9p50000_9p69649 | QSO | Galform | mstar_9p50000_9p69649 | — |
| QSO_Galform_mstar_9p90654_10p15730 | QSO | Galform | mstar_9p90654_10p15730 | — |
| QSO_Shark_log10_OII_lum_39p00000_39p64443 | QSO | Shark | log10_OII_lum_39p00000_39p64443 | — |
| QSO_Shark_mstar_10p50350_12p00000 | QSO | Shark | mstar_10p50350_12p00000 | — |
| QSO_Shark_mstar_9p50000_9p69649 | QSO | Shark | mstar_9p50000_9p69649 | — |
| QSO_Shark_mstar_9p90654_10p15730 | QSO | Shark | mstar_9p90654_10p15730 | — |

## Casos no válidos

| case_id | tracer | SAM | propiedad | opt_value |
|---------|--------|-----|-----------|-----------|
| ELG_Galform_log10_OII_lum_39p00000_39p64443 | ELG | Galform | log10_OII_lum_39p00000_39p64443 | — |
| ELG_Galform_log10_OII_lum_40p10221_40p56051 | ELG | Galform | log10_OII_lum_40p10221_40p56051 | — |
| ELG_Galform_mstar_10p50350_12p00000 | ELG | Galform | mstar_10p50350_12p00000 | — |
| ELG_Galform_mstar_9p90654_10p15730 | ELG | Galform | mstar_9p90654_10p15730 | — |
| ELG_Shark_log10_OII_lum_40p10221_40p56051 | ELG | Shark | log10_OII_lum_40p10221_40p56051 | — |
| ELG_Shark_log10_OII_lum_41p08099_44p00000 | ELG | Shark | log10_OII_lum_41p08099_44p00000 | — |
| LRG1_Galform_log10_OII_lum_39p00000_39p64443 | LRG1 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| LRG1_Galform_log10_OII_lum_40p10221_40p56051 | LRG1 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| LRG1_Galform_log10_OII_lum_41p08099_44p00000 | LRG1 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| LRG1_Galform_mstar_10p50350_12p00000 | LRG1 | Galform | mstar_10p50350_12p00000 | — |
| LRG1_Shark_log10_OII_lum_39p00000_39p64443 | LRG1 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| LRG1_Shark_log10_OII_lum_40p10221_40p56051 | LRG1 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| LRG1_Shark_log10_OII_lum_41p08099_44p00000 | LRG1 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| LRG2_Galform_log10_OII_lum_39p00000_39p64443 | LRG2 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| LRG2_Galform_log10_OII_lum_40p10221_40p56051 | LRG2 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| LRG2_Galform_log10_OII_lum_41p08099_44p00000 | LRG2 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| LRG2_Galform_mstar_10p50350_12p00000 | LRG2 | Galform | mstar_10p50350_12p00000 | — |
| LRG2_Shark_log10_OII_lum_39p00000_39p64443 | LRG2 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| LRG2_Shark_log10_OII_lum_40p10221_40p56051 | LRG2 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| LRG2_Shark_log10_OII_lum_41p08099_44p00000 | LRG2 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| LRG3_Galform_log10_OII_lum_39p00000_39p64443 | LRG3 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| LRG3_Galform_log10_OII_lum_40p10221_40p56051 | LRG3 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| LRG3_Galform_log10_OII_lum_41p08099_44p00000 | LRG3 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| LRG3_Galform_mstar_10p50350_12p00000 | LRG3 | Galform | mstar_10p50350_12p00000 | — |
| LRG3_Shark_log10_OII_lum_39p00000_39p64443 | LRG3 | Shark | log10_OII_lum_39p00000_39p64443 | — |
| LRG3_Shark_log10_OII_lum_40p10221_40p56051 | LRG3 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| LRG3_Shark_log10_OII_lum_41p08099_44p00000 | LRG3 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| LRG3_Shark_mstar_9p50000_9p69649 | LRG3 | Shark | mstar_9p50000_9p69649 | — |
| QSO-4_Galform_log10_OII_lum_39p00000_39p64443 | QSO-4 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| QSO-4_Galform_log10_OII_lum_40p10221_40p56051 | QSO-4 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| QSO-4_Galform_log10_OII_lum_41p08099_44p00000 | QSO-4 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| QSO-4_Galform_mstar_10p50350_12p00000 | QSO-4 | Galform | mstar_10p50350_12p00000 | — |
| QSO-4_Galform_mstar_9p50000_9p69649 | QSO-4 | Galform | mstar_9p50000_9p69649 | — |
| QSO-4_Galform_mstar_9p90654_10p15730 | QSO-4 | Galform | mstar_9p90654_10p15730 | — |
| QSO-4_Shark_log10_OII_lum_40p10221_40p56051 | QSO-4 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| QSO-4_Shark_log10_OII_lum_41p08099_44p00000 | QSO-4 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| QSO-4_Shark_mstar_9p50000_9p69649 | QSO-4 | Shark | mstar_9p50000_9p69649 | — |
| QSO-5_Galform_log10_OII_lum_39p00000_39p64443 | QSO-5 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| QSO-5_Galform_log10_OII_lum_40p10221_40p56051 | QSO-5 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| QSO-5_Galform_log10_OII_lum_41p08099_44p00000 | QSO-5 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| QSO-5_Galform_mstar_10p50350_12p00000 | QSO-5 | Galform | mstar_10p50350_12p00000 | — |
| QSO-5_Galform_mstar_9p50000_9p69649 | QSO-5 | Galform | mstar_9p50000_9p69649 | — |
| QSO-5_Galform_mstar_9p90654_10p15730 | QSO-5 | Galform | mstar_9p90654_10p15730 | — |
| QSO-5_Shark_log10_OII_lum_40p10221_40p56051 | QSO-5 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| QSO-5_Shark_log10_OII_lum_41p08099_44p00000 | QSO-5 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| QSO-5_Shark_mstar_10p50350_12p00000 | QSO-5 | Shark | mstar_10p50350_12p00000 | — |
| QSO-6_Galform_log10_OII_lum_39p00000_39p64443 | QSO-6 | Galform | log10_OII_lum_39p00000_39p64443 | — |
| QSO-6_Galform_log10_OII_lum_40p10221_40p56051 | QSO-6 | Galform | log10_OII_lum_40p10221_40p56051 | — |
| QSO-6_Galform_log10_OII_lum_41p08099_44p00000 | QSO-6 | Galform | log10_OII_lum_41p08099_44p00000 | — |
| QSO-6_Galform_mstar_10p50350_12p00000 | QSO-6 | Galform | mstar_10p50350_12p00000 | — |
| QSO-6_Galform_mstar_9p50000_9p69649 | QSO-6 | Galform | mstar_9p50000_9p69649 | — |
| QSO-6_Galform_mstar_9p90654_10p15730 | QSO-6 | Galform | mstar_9p90654_10p15730 | — |
| QSO-6_Shark_log10_OII_lum_40p10221_40p56051 | QSO-6 | Shark | log10_OII_lum_40p10221_40p56051 | — |
| QSO-6_Shark_log10_OII_lum_41p08099_44p00000 | QSO-6 | Shark | log10_OII_lum_41p08099_44p00000 | — |
| QSO-6_Shark_mstar_10p50350_12p00000 | QSO-6 | Shark | mstar_10p50350_12p00000 | — |
| QSO-6_Shark_mstar_9p50000_9p69649 | QSO-6 | Shark | mstar_9p50000_9p69649 | — |
| QSO-6_Shark_mstar_9p90654_10p15730 | QSO-6 | Shark | mstar_9p90654_10p15730 | — |
| QSO_Galform_log10_OII_lum_39p00000_39p64443 | QSO | Galform | log10_OII_lum_39p00000_39p64443 | — |
| QSO_Galform_log10_OII_lum_40p10221_40p56051 | QSO | Galform | log10_OII_lum_40p10221_40p56051 | — |
| QSO_Galform_mstar_10p50350_12p00000 | QSO | Galform | mstar_10p50350_12p00000 | — |
| QSO_Shark_log10_OII_lum_40p10221_40p56051 | QSO | Shark | log10_OII_lum_40p10221_40p56051 | — |
| QSO_Shark_log10_OII_lum_41p08099_44p00000 | QSO | Shark | log10_OII_lum_41p08099_44p00000 | — |

## Estructura de carpetas

```text
by_validity/
  valid/<case_id>/     # pk_ratio.png, pk_comparison.png, R_k.png, R_k.txt
  invalid/<case_id>/   # mismos 4 ficheros
```

## Resumen por trazador

| Trazador | válidos | no válidos |
|----------|---------|------------|
| ELG | 6 | 6 |
| LRG1 | 5 | 7 |
| LRG2 | 5 | 7 |
| LRG3 | 4 | 8 |
| QSO | 7 | 5 |
| QSO-4 | 3 | 9 |
| QSO-5 | 3 | 9 |
| QSO-6 | 1 | 11 |
